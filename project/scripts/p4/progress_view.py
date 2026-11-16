"""Open-work view for /progress. Read-only: never edits memory or Perforce.

Sections: memory-cited CLs that are UNSHELVED (opened, nothing shelved), SHELF BEHIND DISK (opened files differ
from the shelf) or PENDING; the default CL; your pending CLs that no memory names (newest first); the `Next:` and
not-yet-landed `Fix CL:` lines of live topic memories; and the JIRA_PROJECT_KEY keys MEMORY.md names.
Builds on memory_cl_status.py (same folder); --memory defaults to CLAUDE_MEMORY_DIR.

Usage: python -I -X utf8 ~/.claude/scripts/p4/progress_view.py [--memory DIR] [--uncited N]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_cl_status as mcs  # noqa: E402

NEXT_RE = re.compile(r"^(?:- )?(?:\*\*)?Next:(?:\*\*)?\s*(.+)$|^(?:- )?(?:\*\*)?Fix CL:(?:\*\*)?\s*(\d+)", re.M)
DONE_BUCKETS = ("LANDED", "RENUMBERED", "GONE")


def jira_keys(index_text):
    """Ticket keys of JIRA_PROJECT_KEY in MEMORY.md; (key, []) when the project has no Jira key."""
    project = mcs.get("JIRA_PROJECT_KEY", "")
    if not project:
        return "Jira", []
    return project, sorted(set(re.findall(rf"\b{re.escape(project)}-\d+\b", index_text)))


def my_pending():
    info = next(iter(mcs.p4_records("info")), {})
    user, client = info.get("userName", ""), info.get("clientName", "")
    rows = mcs.p4_records("changes", "-s", "pending", "-l", "-u", user, "-c", client)
    return [(int(r["change"]), mcs.first_line(r.get("desc"))) for r in rows if r.get("code") == "stat"]


def shelf_drift(num):
    """Opened files whose disk content differs from the shelved revision (`p4 diff -sa @=N`)."""
    return sum(1 for r in mcs.p4_records("diff", "-sa", f"@={num}") if r.get("code") == "stat" and r.get("depotFile"))


def cited_section(status, cites):
    unshelved, drifted, pending = [], [], []
    for num in sorted(status, reverse=True):
        info = status[num]
        if info["bucket"] != "PENDING":
            continue
        opened, shelved = info.get("opened"), info.get("shelved")
        drift = shelf_drift(num) if opened and shelved else 0
        row = f"  {num} opened {opened} shelved {shelved}{f' differ {drift}' if drift else ''} | {info['title']} | {', '.join(sorted(cites[num]))[:90]}"
        (unshelved if opened and not shelved else drifted if drift else pending).append(row)
    return unshelved, drifted, pending


def default_cl():
    rows = [r for r in mcs.p4_records("opened", "-c", "default") if r.get("code") == "stat"]
    return [f"  {r.get('action')} {r.get('depotFile')}{' (exclusive)' if re.search(r'\+\w*l', r.get('type', '')) else ''}" for r in rows]


def next_lines(files, status):
    out = []
    for name, text in sorted(files.items()):
        if name.startswith(("index_", "MEMORY")):
            continue
        for match in NEXT_RE.finditer(text):
            if match.group(2) and status.get(int(match.group(2)), {}).get("bucket") in DONE_BUCKETS:
                continue
            out.append(f"  {name[:-3]}: " + (match.group(1) or f"Fix CL {match.group(2)} (not landed)")[:150])
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--memory", help="memory folder (default: CLAUDE_MEMORY_DIR)")
    parser.add_argument("--uncited", type=int, default=25, help="max uncited pending CLs to list")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    files = mcs.read_memory(mcs.memory_dir(args.memory), include_archive=False)
    cites = mcs.cited_cls(files)
    status = mcs.resolve(cites)
    unshelved, drifted, pending = cited_section(status, cites)
    uncited = [(n, t) for n, t in my_pending() if n not in cites]
    default = default_cl()

    print(f"## UNSHELVED: opened, nothing shelved ({len(unshelved)})", *unshelved, sep="\n")
    print(f"\n## SHELF BEHIND DISK: opened files differ from the shelf ({len(drifted)})", *drifted, sep="\n")
    print(f"\n## Default CL ({len(default)} files)", *default, sep="\n")
    print(f"\n## PENDING, cited by memory ({len(pending)})", *pending, sep="\n")
    print(f"\n## Pending CLs no memory names ({len(uncited)}; newest {min(len(uncited), args.uncited)})")
    for num, title in sorted(uncited, reverse=True)[:args.uncited]:
        print(f"  {num} | {title}")
    nexts = next_lines(files, status)
    print(f"\n## Next: lines in topic memories ({len(nexts)})", *nexts, sep="\n")
    project, keys = jira_keys(files.get("MEMORY.md", ""))
    print(f"\n## {project} keys in MEMORY.md ({len(keys)}): {', '.join(keys)}")


if __name__ == "__main__":
    main()
