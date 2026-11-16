"""List human-authored CLs submitted to a stream in the last N days, split into review batches.

Usage:
    python list_changes.py --days 2 [--path <P4_STREAM>/...] [--batches 6] [--out DIR]

Writes <out>/changes.json and prints a compact summary. One `p4 describe -s` call per
50 CLs (not one per CL), so a 2-day window takes seconds.
"""

import argparse
import datetime as dt
import io
import json
import marshal
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "scripts" / "lib"))
from project_vars import get  # noqa: E402

BOT_USERS = {u.strip().lower() for u in get("P4_BOT_USERS").split(",") if u.strip()}
BOT_CLIENT = re.compile(get("P4_BOT_CLIENT_REGEX"), re.IGNORECASE)
TEST_MODULE = get("UE_TEST_MODULE", "")
JIRA_PROJECT = get("JIRA_PROJECT_KEY", "")
NEVER = r"(?!x)x"  # matches nothing: used when the project has no test module / Jira key
JIRA_KEY = re.compile(rf"{re.escape(JIRA_PROJECT)}-\d+" if JIRA_PROJECT else NEVER)
CODE_EXT = {".cpp", ".h", ".hpp", ".inl", ".cs", ".py", ".ini", ".json", ".uplugin", ".uproject", ".usf", ".ush"}
ASSET_EXT = {".uasset", ".umap"}
# Paths whose changes never reach a playable build, or are generated.
SKIP_PATH = re.compile(r"/(Binaries|Intermediate|Saved|DerivedDataCache)/|\.temp/", re.IGNORECASE)
# Automation tests: kept out of review, but listed as test_files (submit-test-gaps reads them).
TEST_PATH = re.compile(rf"/Source/{re.escape(TEST_MODULE)}/" if TEST_MODULE else NEVER, re.IGNORECASE)
# Mostly editor/test tooling; still listed but flagged so reviewers deprioritize them.
TOOLING_PATH = re.compile(rf"/Source/({get('UE_TOOLING_MODULES_REGEX')})/|/Editor/|/Content/Python/|/Build/", re.IGNORECASE)
TOOLING_DESC = re.compile(r"^\s*\[(Automation|CI|Horde|Tests?)\]", re.IGNORECASE)


def p4_marshal(args):
    proc = subprocess.run(["p4", "-G"] + args, capture_output=True)
    records = []
    stream = io.BytesIO(proc.stdout)
    while True:
        try:
            rec = marshal.load(stream)
        except EOFError:
            break
        records.append({k.decode(): (v.decode("utf-8", "replace") if isinstance(v, bytes) else v) for k, v in rec.items()})
    errors = [r for r in records if r.get("code") == "error"]
    if errors:
        print(f"p4 {' '.join(args[:2])}: {errors[0].get('data', '').strip()}", file=sys.stderr)
    return [r for r in records if r.get("code") != "error"]


def is_bot(change):
    return change["user"].lower() in BOT_USERS or bool(BOT_CLIENT.search(change["client"]))


def area_of(path):
    m = re.search(r"/Source/([^/]+)/(?:(?:Private|Public)/)?([^/]+)/", path)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    m = re.search(r"/Plugins/(?:[^/]+/)*?([^/]+)/Source/", path)
    if m:
        return f"Plugin/{m.group(1)}"
    if "/Config/" in path:
        return "Config"
    if path.startswith("//") and "/Engine/" in path:
        return "Engine"
    return "Other"


def classify(describe):
    code, assets, other, tests = [], [], [], []
    i = 0
    while f"depotFile{i}" in describe:
        path = describe[f"depotFile{i}"]
        action = describe.get(f"action{i}", "")
        i += 1
        if SKIP_PATH.search(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        entry = f"{action} {path}"
        if TEST_PATH.search(path):
            tests.append(entry)
        elif ext in CODE_EXT:
            code.append(entry)
        elif ext in ASSET_EXT:
            assets.append(entry)
        else:
            other.append(entry)
    return code, assets, other, tests


def make_batches(code_changes, count):
    """Greedy: keep CLs of the same main area together, balance by code-file count."""
    files = lambda group: sum(len(c["code_files"]) for c in group)
    count = max(1, min(count, len(code_changes)))
    target = -(-files(code_changes) // count)
    groups = defaultdict(list)
    for c in code_changes:
        groups[c["area"]].append(c)
    # Chunk any area bigger than one agent's share so a busy system does not swamp a batch.
    chunks = []
    for group in groups.values():
        chunk = []
        for c in group:
            if chunk and files(chunk) + len(c["code_files"]) > target:
                chunks.append(chunk)
                chunk = []
            chunk.append(c)
        chunks.append(chunk)
    batches = [[] for _ in range(count)]
    for chunk in sorted(chunks, key=lambda g: -files(g)):
        idx = min(range(count), key=lambda i: files(batches[i]))
        batches[idx].extend(chunk)
    return [[c["change"] for c in b] for b in batches if b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float, required=True)
    ap.add_argument("--path", default=None, help="default: <P4_STREAM>/... from project-vars")
    ap.add_argument("--batches", type=int, default=0, help="0 = auto (about 1 batch per 15 code files, 3..10)")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    args.path = args.path or get("P4_STREAM") + "/..."

    since =dt.datetime.now() - dt.timedelta(days=args.days)
    since_str = since.strftime("%Y/%m/%d:%H:%M:%S")
    changes = p4_marshal(["changes", "-l", "-s", "submitted", f"{args.path}@{since_str},@now"])
    human = [c for c in changes if not is_bot(c)]
    bots = len(changes) - len(human)

    described = {}
    nums = [c["change"] for c in human]
    for i in range(0, len(nums), 50):
        for d in p4_marshal(["describe", "-s"] + nums[i:i + 50]):
            described[d["change"]] = d

    results = []
    for c in human:
        d = described.get(c["change"], {})
        code, assets, other, tests = classify(d)
        areas = defaultdict(int)
        for f in code:
            areas[area_of(f.split(" ", 1)[1])] += 1
        main_area = max(areas, key=areas.get) if areas else ""
        # A test-tagged CL may still edit ini; it only counts as tooling if it touches no game source.
        tooling = bool(code) and (all(TOOLING_PATH.search(f) for f in code) or (
            bool(TOOLING_DESC.match(c["desc"])) and all(TOOLING_PATH.search(f) or "/Config/" in f for f in code)))
        results.append({
            "change": c["change"],
            "user": c["user"],
            "date": dt.datetime.fromtimestamp(int(c["time"])).strftime("%Y-%m-%d %H:%M"),
            "desc": c["desc"].strip(),
            "jira": sorted(set(JIRA_KEY.findall(c["desc"]))),
            "area": main_area,
            "tooling_only": tooling,
            "code_files": code,
            "asset_files": assets,
            "other_files": other,
            "test_files": tests,
        })

    have = p4_marshal(["changes", "-m1", f"{args.path}#have"])
    have_cl = int(have[0]["change"]) if have else 0
    newest_cl = max((int(r["change"]) for r in results), default=0)

    code_changes = [r for r in results if r["code_files"] and not r["tooling_only"]]
    n_files = sum(len(r["code_files"]) for r in code_changes)
    count = args.batches or max(3, min(10, round(n_files / 15)))
    batches = make_batches(code_changes, count) if code_changes else []

    out = {
        "window": {"since": since.strftime("%Y-%m-%d %H:%M"), "until": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "days": args.days, "path": args.path},
        "workspace": {"have_change": have_cl, "newest_change": newest_cl, "behind": have_cl < newest_cl},
        "counts": {
            "submitted": len(changes), "bots_skipped": bots, "human": len(human),
            "code_review": len(code_changes),
            "tooling_only": sum(1 for r in results if r["tooling_only"]),
            "asset_only": sum(1 for r in results if not r["code_files"] and r["asset_files"]),
            "other": sum(1 for r in results if not r["code_files"] and not r["asset_files"]),
        },
        "batches": batches,
        "changes": results,
    }
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "changes.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)

    sys.stdout.reconfigure(encoding="utf-8")
    w = out["window"]
    print(f"Window {w['since']} -> {w['until']} on {w['path']}")
    print("Counts: " + ", ".join(f"{k}={v}" for k, v in out["counts"].items()))
    if out["workspace"]["behind"]:
        print(f"WARNING: workspace synced to {have_cl}, window goes to {newest_cl}; local files may predate some CLs")
    by_cl = {r["change"]: r for r in results}
    for i, b in enumerate(batches, 1):
        files = sum(len(by_cl[c]["code_files"]) for c in b)
        print(f"Batch {i} ({len(b)} CLs, {files} code files): " + " ".join(f"{c}[{by_cl[c]['area']}]" for c in b))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
