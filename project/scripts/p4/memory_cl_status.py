"""Live Perforce status of every CL that Claude's memory cites. Read-only: it never edits memory.

Buckets: PENDING (yours, with opened/shelved counts), EMPTY (yours, nothing opened or shelved),
PENDING-OTHER (a teammate's), LANDED (submitted under the cited number), RENUMBERED (submitted under a new number),
GONE, and SWARM-COPY (Swarm's review copy, not listed).
Also lists memory files that still claim a state (pending/shelved/owed...) for a CL that has landed or is gone,
and project memories whose CLs have all landed and that MEMORY.md doesn't link (archive candidates).

--memory defaults to CLAUDE_MEMORY_DIR; p4 runs in PROJECT_ROOT (env var, else .claude/rules/project-vars.md).

Usage: python -I -X utf8 ~/.claude/scripts/p4/memory_cl_status.py [--memory DIR] [--json OUT] [--include-archive]
"""
import argparse
import functools
import io
import json
import marshal
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "scripts" / "lib"))
from project_vars import get  # noqa: E402

CL_RE = re.compile(r"(?<![\d.:#/x-])(\d{5,7})(?![\d.]|\s*(?:bytes|KB|MB|ms|cm)\b)")
STATE_RE = re.compile(r"\b(pending|shelved|shelf|owed|unbuilt|not shelved|PAUSED|unsubmitted)\b", re.I)
BATCH = 40


@functools.lru_cache(maxsize=None)
def workspace():
    return get("PROJECT_ROOT")


def memory_dir(arg=None):
    """--memory wins, else CLAUDE_MEMORY_DIR (KeyError with a fix hint when unset)."""
    return arg or get("CLAUDE_MEMORY_DIR")


def p4_records(*args):
    proc = subprocess.run(["p4", "-G", *args], capture_output=True, cwd=workspace())
    stream, records = io.BytesIO(proc.stdout), []
    while True:
        try:
            raw = marshal.load(stream)
        except EOFError:
            return records
        records.append({k.decode(): v.decode("utf-8", "replace") if isinstance(v, bytes) else v for k, v in raw.items()})


def read_memory(memory_dir, include_archive):
    files = {}
    dirs = [memory_dir] + ([os.path.join(memory_dir, "archive")] if include_archive else [])
    for folder in dirs:
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.endswith(".md"):
                rel = name if folder == memory_dir else f"archive/{name}"
                with open(os.path.join(folder, name), encoding="utf-8") as fh:
                    files[rel] = fh.read()
    return files


def cited_cls(files):
    cites = {}
    for name, text in files.items():
        for num in set(CL_RE.findall(text)):
            cites.setdefault(int(num), set()).add(name)
    return cites


def first_line(desc):
    lines = (desc or "").strip().splitlines()
    return lines[0][:80] if lines else ""


def pending_counts(change):
    opened = [r for r in p4_records("opened", "-a", "-c", str(change)) if r.get("code") == "stat"]
    shelf = [r for r in p4_records("describe", "-s", "-S", str(change)) if r.get("code") == "stat"]
    shelved = sum(1 for k in (shelf[0] if shelf else {}) if k.startswith("depotFile"))
    return len(opened), shelved


def pending_info(change, user, me):
    if user.lower() == "swarm":
        return {"bucket": "SWARM-COPY", "user": user}
    opened, shelved = pending_counts(change)
    bucket = "EMPTY" if opened == 0 and shelved == 0 else "PENDING"
    if user.lower() != me.lower():
        bucket += "-OTHER"
    return {"bucket": bucket, "opened": opened, "shelved": shelved, "user": user}


def classify(record, asked, me):
    """One describe -O record can answer for both its submitted number and its old pending number."""
    change, old = int(record["change"]), int(record.get("oldChange") or 0)
    if record.get("status") == "pending":
        return {change: pending_info(change, record.get("user", ""), me)}
    out = {change: {"bucket": "LANDED"}} if change in asked else {}
    if old and old != change and old in asked:
        out[old] = {"bucket": "RENUMBERED", "now": change}
    return out


def resolve(numbers):
    status, asked = {}, set(numbers)
    me = next((r.get("userName", "") for r in p4_records("info")), "")
    ordered = sorted(numbers)
    for i in range(0, len(ordered), BATCH):
        for rec in p4_records("describe", "-s", "-O", *map(str, ordered[i:i + BATCH])):
            if rec.get("code") == "stat" and rec.get("change"):
                for num, info in classify(rec, asked, me).items():
                    info["title"] = first_line(rec.get("desc"))
                    status[num] = info
    for num in ordered:
        status.setdefault(num, {"bucket": "GONE", "title": ""})
    return status


def stale_claims(files, cites, status):
    rows = []
    for name, text in files.items():
        done = [n for n, fs in cites.items() if name in fs and status[n]["bucket"] in ("LANDED", "RENUMBERED", "GONE", "EMPTY")]
        if not done:
            continue
        hits = [line.strip()[:140] for line in text.splitlines()
                if STATE_RE.search(line) and any(str(n) in line for n in done) and not line.startswith("**P4 check")]
        if hits:
            rows.append({"file": name, "cls": sorted(done), "lines": hits})
    return rows


def archive_candidates(files, cites, status):
    index = files.get("MEMORY.md", "")
    out = []
    for name in files:
        if not name.startswith("project_") or name in index:
            continue
        mine = [n for n, fs in cites.items() if name in fs and status[n]["bucket"] not in ("GONE", "SWARM-COPY")]
        if mine and all(status[n]["bucket"] in ("LANDED", "RENUMBERED") for n in mine):
            out.append(name)
    return sorted(out)


def describe(num, info, cites):
    extra = {"PENDING": f"opened {info.get('opened')} shelved {info.get('shelved')} ({info.get('user')})",
             "PENDING-OTHER": f"opened {info.get('opened')} shelved {info.get('shelved')} ({info.get('user')})",
             "RENUMBERED": f"-> {info.get('now')}"}.get(info["bucket"], "")
    return f"  {num} {extra} | {info['title']} | {', '.join(sorted(cites[num]))[:120]}"


def report(status, cites, stale, archive):
    for bucket in ("PENDING", "EMPTY", "PENDING-OTHER", "RENUMBERED", "GONE"):
        rows = [n for n in sorted(status) if status[n]["bucket"] == bucket]
        print(f"\n## {bucket} ({len(rows)})")
        for num in rows:
            print(describe(num, status[num], cites))
    landed = sum(1 for v in status.values() if v["bucket"] == "LANDED")
    print(f"\n## LANDED ({landed}) - not listed")
    print(f"\n## Stale state claims ({len(stale)} files)")
    for row in stale:
        print(f"  {row['file']} [{', '.join(map(str, row['cls']))}]")
        for line in row["lines"][:3]:
            print(f"      {line}")
    print(f"\n## Archive candidates ({len(archive)}): project memories, all CLs landed, not in MEMORY.md")
    for name in archive:
        print(f"  {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--memory", help="memory folder (default: CLAUDE_MEMORY_DIR)")
    parser.add_argument("--json")
    parser.add_argument("--include-archive", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    files = read_memory(memory_dir(args.memory), args.include_archive)
    cites = cited_cls(files)
    status = resolve(cites)
    stale, archive = stale_claims(files, cites, status), archive_candidates(files, cites, status)
    report(status, cites, stale, archive)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"status": status, "cites": {n: sorted(f) for n, f in cites.items()},
                       "stale": stale, "archive": archive}, fh, indent=1)


if __name__ == "__main__":
    main()
