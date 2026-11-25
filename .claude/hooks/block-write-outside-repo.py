#!/usr/bin/env python3
"""
block-write-outside-repo.py — Ask for confirmation before Claude writes outside the project.

Event: PreToolUse
Matcher: Edit|Write|NotebookEdit

Allowed without asking: the project directory, ~/.claude/, the system temp
directory (Claude's scratchpad lives there) and any permissions.additionalDirectories
from the user, project and local settings files. Writes into a .git folder always ask.

Only covers the file tools: Bash redirections and cp/mv are not seen by this hook.
Directories added for the session with --add-dir or /add-dir are not visible to
hooks, so writes there still ask; list them in permissions.additionalDirectories instead.

When wired both in ~/.claude/settings.json and in a project, the project copy
steps aside so the check runs once.

Exit codes:
  0 — Always. The decision is returned as JSON on stdout
      (hookSpecificOutput.permissionDecision = "ask"), which forces a user prompt.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


def ask(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve(raw: str, base: Path) -> Path | None:
    try:
        p = Path(os.path.expanduser(raw))
        return (p if p.is_absolute() else base / p).resolve()
    except (OSError, RuntimeError):
        return None


def additional_directories(project: Path) -> list[Path]:
    """Collect permissions.additionalDirectories from all settings scopes."""
    files = [
        Path.home() / ".claude" / "settings.json",
        project / ".claude" / "settings.json",
        project / ".claude" / "settings.local.json",
    ]
    dirs: list[Path] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for raw in data.get("permissions", {}).get("additionalDirectories", []) or []:
            if isinstance(raw, str) and (p := resolve(raw, project)) is not None:
                dirs.append(p)
    return dirs


def wired_globally() -> bool:
    """True if this is a project copy and the user-level settings already wire the hook."""
    global_dir = (Path.home() / ".claude").resolve()
    if is_within(Path(__file__).resolve(), global_dir):
        return False
    try:
        text = (global_dir / "settings.json").read_text(encoding="utf-8")
    except OSError:
        return False
    return Path(__file__).name in text


def main() -> None:
    if wired_globally():
        sys.exit(0)
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ""
    if not project_dir:
        sys.exit(0)  # Can't determine project root; fail open
    project = Path(project_dir).resolve()

    target = resolve(file_path, project)
    if target is None:
        sys.exit(0)

    if ".git" in target.parts:
        ask(f"'{file_path}' is inside a .git folder.")

    allowed = [project, (Path.home() / ".claude").resolve(), Path(tempfile.gettempdir()).resolve()]
    allowed += additional_directories(project)
    if any(is_within(target, root) for root in allowed):
        sys.exit(0)

    ask(f"'{file_path}' is outside the project ({project}).")


if __name__ == "__main__":
    main()
