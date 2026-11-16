"""Filter a list_changes.py changes.json down to CLs that changed game code, and batch them.

Usage:
    python game_cls.py <out>/changes.json [--focus TEXT] [--per-batch 10] [--max-batches 8]

Game code = runtime C++ under <UE_PROJECT_NAME>/Source or <UE_PROJECT_NAME>/Plugins/**/Source (not Editor,
Automation, Tests or visualizer modules) plus gameplay .ini under Config (not *Editor*.ini).
Writes <out>/game_cls.json and prints a short summary.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "qa-bug-sweep" / "scripts"))
from list_changes import area_of  # noqa: E402
sys.path.insert(0, str(Path.home() / ".claude" / "scripts" / "lib"))
from project_vars import get  # noqa: E402

PROJECT = re.escape(get("UE_PROJECT_NAME"))  # depot folder holding the .uproject
TEST_MODULE = get("UE_TEST_MODULE", "")
GAME_SOURCE = re.compile(rf"/{PROJECT}/(?:Plugins/(?:[^/]+/)+?)?Source/([^/]+)/.+\.(?:h|hpp|cpp|inl)$", re.IGNORECASE)
NON_GAME_MODULE = re.compile(r"Editor|Automation|Tests?$|Visualizers?$", re.IGNORECASE)
GAME_CONFIG = re.compile(rf"/{PROJECT}/(?:Plugins/(?:[^/]+/)+?)?Config/([^/]+\.ini)$", re.IGNORECASE)


def path_of(entry):
    return entry.split(" ", 1)[1]


def is_game_source(path):
    m = GAME_SOURCE.search(path)
    return bool(m) and not NON_GAME_MODULE.search(m.group(1))


def is_game_config(path):
    m = GAME_CONFIG.search(path)
    return bool(m) and "editor" not in m.group(1).lower()


def first_line(desc):
    return desc.strip().splitlines()[0][:120] if desc.strip() else ""


def summarize(c, game, config):
    areas = {}
    for f in game + config:
        a = area_of(path_of(f))
        areas[a] = areas.get(a, 0) + 1
    return {
        "change": c["change"], "user": c["user"], "date": c["date"], "desc": c["desc"], "jira": c["jira"],
        "area": max(areas, key=areas.get) if areas else "",
        "game_files": game, "config_files": config, "test_files": c.get("test_files", []),
        "asset_count": len(c["asset_files"]),
        "code_files": game + config,
    }


def weight(c):
    # Every CL costs a diff read; big CLs cost more, but a judge skims past ~25 files.
    return 1 + min(len(c["code_files"]), 25) / 5


def make_batches(cls, count):
    """Greedy: keep each area together, split areas heavier than one batch, balance by weight."""
    target = sum(weight(c) for c in cls) / count
    groups = {}
    for c in cls:
        groups.setdefault(c["area"], []).append(c)
    chunks = []
    for group in groups.values():
        chunk = []
        for c in group:
            if chunk and sum(map(weight, chunk)) + weight(c) > target:
                chunks.append(chunk)
                chunk = []
            chunk.append(c)
        chunks.append(chunk)
    batches = [[] for _ in range(count)]
    for chunk in sorted(chunks, key=lambda g: -sum(map(weight, g))):
        min(batches, key=lambda b: sum(map(weight, b))).extend(chunk)
    return [[c["change"] for c in b] for b in batches if b]


def focus_match(c, words):
    """'desc' when the description/author names the focus, 'files' when only some files do, else None."""
    if any(w in f"{c['desc']} {c['user']}".lower() for w in words):
        return "desc"
    hits = [f for f in c["code_files"] if any(w in area_of(path_of(f)).lower() for w in words)]
    if hits:
        c["focus_files"] = hits
        return "files"
    return None


def apply_focus(game_cls, focus):
    words = focus.lower().split()
    kept = []
    for c in game_cls:
        c["focus_match"] = focus_match(c, words)
        if c["focus_match"]:
            kept.append(c)
    return kept


def test_cl_entry(c):
    files = [path_of(f).split(f"/Source/{TEST_MODULE}/", 1)[-1] for f in c["test_files"]]
    return {"change": c["change"], "user": c["user"], "summary": first_line(c["desc"]), "test_files": files}


def split_changes(changes):
    game_cls, test_cls = [], []
    skipped = {"tooling_or_engine_only": 0, "asset_only": 0, "test_only": 0, "other": 0}
    for c in changes:
        game = [f for f in c["code_files"] if is_game_source(path_of(f))]
        config = [f for f in c["code_files"] if is_game_config(path_of(f))]
        if c.get("test_files"):
            test_cls.append(test_cl_entry(c))
        if (game or config) and not c["tooling_only"]:
            game_cls.append(summarize(c, game, config))
        elif c["code_files"]:
            skipped["tooling_or_engine_only"] += 1
        elif c["asset_files"]:
            skipped["asset_only"] += 1
        elif c.get("test_files"):
            skipped["test_only"] += 1
        else:
            skipped["other"] += 1
    return game_cls, test_cls, skipped


def test_cls_brief(test_cls):
    """Paste-ready block for judge prompts: one line per test CL, test file names only, capped."""
    lines = []
    for t in test_cls:
        names = sorted({Path(f).stem for f in t["test_files"]})
        more = f" (+{len(names) - 6} more)" if len(names) > 6 else ""
        lines.append(f"- {t['change']} {t['user']}: {t['summary']} — {', '.join(names[:6])}{more}")
    return "\n".join(lines) or "none"


def check(out_dir):
    """Exit non-zero when a game CL has no item in any batch_*.json (judges may end without replying)."""
    game = json.loads((out_dir / "game_cls.json").read_text(encoding="utf-8"))
    judged = set()
    for b in sorted(out_dir.glob("batch_*.json")):
        judged |= {str(i["id"]).split("-")[0] for i in json.loads(b.read_text(encoding="utf-8"))}
    missing = [c["change"] for c in game["changes"] if str(c["change"]) not in judged]
    print(f"{len(game['changes']) - len(missing)}/{len(game['changes'])} game CLs judged" +
          (f"; missing: {' '.join(missing)}" if missing else ""))
    sys.exit(1 if missing else 0)


def report(out, path):
    by_cl = {c["change"]: c for c in out["changes"]}
    print("Counts: " + ", ".join(f"{k}={v}" for k, v in out["counts"].items()))
    ws = out["workspace"]
    newer = [c for c in by_cl if int(c) > ws["have_change"]]
    if newer:
        print(f"WARNING: workspace at {ws['have_change']}; CLs {' '.join(newer)} are newer. Their judges must read "
              f"files with p4 print -q <file>@<CL>")
    print(f"{len(out['test_cls'])} CLs in the window touched {TEST_MODULE or 'the test module'} (brief: test_cls.md)")
    for i, b in enumerate(out["batches"], 1):
        print(f"Batch {i} ({len(b)} CLs): " + " ".join(
            f"{c}[{by_cl[c]['area']}{'*' if by_cl[c].get('focus_match') == 'files' else ''}]" for c in b))
    if any(c.get("focus_match") == "files" for c in by_cl.values()):
        print("* = matched the focus only through some files; judge only focus_files for that CL")
    print(f"Wrote {path}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("changes", type=Path, help="changes.json, or the OUT folder with --check")
    ap.add_argument("--focus", default="", help="keep CLs whose desc/author/file areas contain any of the words")
    ap.add_argument("--per-batch", type=int, default=10, help="target CLs per judge agent")
    ap.add_argument("--max-batches", type=int, default=8)
    ap.add_argument("--check", action="store_true", help="verify every game CL has an item in batch_*.json")
    args = ap.parse_args()
    if args.check:
        check(args.changes if args.changes.is_dir() else args.changes.parent)

    data = json.loads(args.changes.read_text(encoding="utf-8"))
    if data["changes"] and "test_files" not in data["changes"][0]:
        sys.exit("error: changes.json has no test_files field; re-run qa-bug-sweep/scripts/list_changes.py")
    game_cls, test_cls, skipped = split_changes(data["changes"])
    before = len(game_cls)
    if args.focus:
        game_cls = apply_focus(game_cls, args.focus)

    count = max(1, min(args.max_batches, math.ceil(len(game_cls) / max(1, args.per_batch))))
    out = {
        "window": data["window"], "workspace": data["workspace"], "focus": args.focus,
        # Skipped counts cover the whole window; focus applies to game CLs only.
        "counts": {"human": data["counts"]["human"], "game": len(game_cls), "focused_out": before - len(game_cls),
                   "with_tests": sum(1 for c in game_cls if c["test_files"]), **skipped},
        "batches": make_batches(game_cls, count) if game_cls else [],
        "changes": game_cls,
        "test_cls": test_cls,
    }
    path = args.changes.parent / "game_cls.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    (args.changes.parent / "test_cls.md").write_text(test_cls_brief(test_cls) + "\n", encoding="utf-8")
    report(out, path)


if __name__ == "__main__":
    main()
