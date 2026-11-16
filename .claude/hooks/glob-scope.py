#!/usr/bin/env python3
"""
glob-scope.py — Keep Glob calls from scanning the whole workspace.

Event: PreToolUse
Matcher: Glob

A Glob rooted at an Unreal workspace (it holds Engine/ and Content/) times out after 20 s.
- Literal leading folders in the pattern move into `path` (docs/subsystems/*.md -> path docs/subsystems).
- A pattern that still starts with ** at the workspace root is denied with a narrower-path hint.
No-op outside an Unreal project (no *.uproject in or one level below the project, no UE_PROJECT).
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from hook_project import find_uproject, layout_hint, uproject_folder
except ImportError as import_error:  # helper missing: allow everything rather than block
    print(f"glob-scope: {import_error}; allowing", file=sys.stderr)
    sys.exit(0)

GLOB_CHARS = re.compile(r"[*?\[\]{}]")
LAYOUT_FOLDERS = ("Source", "Source/<Module>", "Config", "Content/<Folder>")


def hint(project_dir: str, uproject: str) -> str:
    return ("Glob from the workspace root times out (Engine/ + Content/). Pass the deepest known folder as "
            f"`path`: {layout_hint(project_dir, uproject, LAYOUT_FOLDERS)}, docs, scripts or .claude.")


def split_literal_prefix(pattern: str) -> tuple[str, str]:
    parts = re.split(r"[\\/]", pattern)
    literal = []
    while len(parts) > 1 and not GLOB_CHARS.search(parts[0]):
        literal.append(parts.pop(0))
    return os.sep.join(literal), "/".join(parts)


def is_workspace_root(path: str, project_dir: str) -> bool:
    return bool(project_dir) and os.path.normcase(os.path.abspath(path)) == os.path.normcase(os.path.abspath(project_dir))


def emit(decision: str, reason: str, updated: dict | None = None) -> None:
    out = {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}
    if updated is not None:
        out["updatedInput"] = updated
    json.dump({"hookSpecificOutput": out}, sys.stdout)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    pattern = str(tool_input.get("pattern") or "")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd", "")
    base = str(tool_input.get("path") or data.get("cwd") or project_dir)
    if not pattern or not base:
        sys.exit(0)
    uproject = find_uproject(project_dir)
    if not uproject:
        sys.exit(0)

    prefix, rest = split_literal_prefix(pattern)
    if prefix:
        candidate = prefix if os.path.isabs(prefix) else os.path.join(base, prefix)
        if os.path.isdir(candidate):
            updated = dict(tool_input, path=os.path.normpath(candidate), pattern=rest)
            emit("allow", f"glob-scope: searching {os.path.normpath(candidate)} for {rest}", updated)
            return
        if is_workspace_root(base, project_dir) and rest.startswith(("**", "*/", "{")):
            source = uproject_folder(project_dir, uproject) + "Source"
            emit("deny", f"No folder {prefix} at the workspace root (Source/ is {source}). " + hint(project_dir, uproject))
            return
        sys.exit(0)

    if is_workspace_root(base, project_dir) and pattern.startswith(("**", "*/", "{")):
        emit("deny", hint(project_dir, uproject))
        return
    sys.exit(0)


if __name__ == "__main__":
    main()
