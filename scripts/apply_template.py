#!/usr/bin/env python3
"""Apply a template git repo on top of a target directory.

Usage: apply_template.py <repo-url-or-path> <ref> <target>

Shallow-clones the template at <ref> into a temp dir, copies every file
(excluding .git/) over <target>, and prints what happened. Template files
win on conflict. Stdlib only; works on Windows, macOS and Linux.

Output (stdout), one line per file:
    ADDED <relative-path>
    OVERWROTE <relative-path>     (content differed from the existing file)
    SAME <relative-path>          (identical, left untouched)
Final line: SUMMARY added=<n> overwrote=<n> same=<n>
Exit codes: 0 ok, 1 usage/clone/copy error.
"""

from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def clone(repo: str, ref: str, dest: Path) -> None:
    """Shallow-clone `repo` at `ref` into `dest`."""
    cmd = ["git", "clone", "--depth", "1", "--branch", ref, repo, str(dest)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed: {result.stderr.strip()}")


def apply(src: Path, target: Path) -> tuple[int, int, int]:
    """Copy src tree over target. Returns (added, overwrote, same)."""
    added = overwrote = same = 0
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if rel.parts[0] == ".git" or path.is_dir():
            continue
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            status = "ADDED"
            added += 1
        elif filecmp.cmp(path, dest, shallow=False):
            print(f"SAME {rel.as_posix()}")
            same += 1
            continue
        else:
            status = "OVERWROTE"
            overwrote += 1
        shutil.copy2(path, dest)
        print(f"{status} {rel.as_posix()}")
    return added, overwrote, same


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 1
    repo, ref, target_arg = argv[1], argv[2], argv[3]
    target = Path(target_arg).resolve()
    if not target.is_dir():
        print(f"Target is not a directory: {target}", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "template"
        try:
            clone(repo, ref, src)
            added, overwrote, same = apply(src, target)
        except (RuntimeError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    print(f"SUMMARY added={added} overwrote={overwrote} same={same}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
