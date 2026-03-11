#!/usr/bin/env python3
"""
block-write-outside-repo.py — Prevent Claude from writing or editing files
outside the current repository root.

Event: PreToolUse
Matcher: Edit|Write

Exit codes:
  0 — Allow / no action
  2 — Block (printed to stderr, operation stopped)
"""
import json
import os
import sys
from pathlib import Path


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = data.get('tool_input', {}).get('file_path', '')
    if not file_path:
        sys.exit(0)

    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '')
    if not project_dir:
        sys.exit(0)  # Can't determine project root; fail open

    try:
        resolved = Path(file_path).resolve()
        root = Path(project_dir).resolve()
        resolved.relative_to(root)
    except ValueError:
        print(
            f"BLOCKED: Write to '{file_path}' denied."
            f" Path is outside repository root '{project_dir}'.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
