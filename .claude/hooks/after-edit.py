#!/usr/bin/env python3
"""
after-edit.py — Auto-format files after Claude edits or writes them.

Event: PostToolUse
Matcher: Edit|Write

Runs the appropriate formatter for each file type. Always exits 0 —
formatting failures are silently skipped so they never block work.
"""
import json
import os
import shutil
import subprocess
import sys


def run(cmd: list[str], file_path: str) -> None:
    """Run a formatter, silently ignoring failures and missing tools."""
    if shutil.which(cmd[0]):
        try:
            subprocess.run(
                cmd + [file_path],
                capture_output=True,
                timeout=30,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path") or tool_input.get("path", "")
    if not file_path:
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lstrip(".")

    if ext in ("js", "jsx", "ts", "tsx", "json", "md", "yaml", "yml", "css", "scss", "html"):
        run(["prettier", "--write"], file_path)

    elif ext == "py":
        run(["black", "--quiet"], file_path)
        run(["ruff", "check", "--fix", "--silent"], file_path)

    elif ext == "go":
        run(["gofmt", "-w"], file_path)

    elif ext == "rs":
        run(["rustfmt"], file_path)

    # Always exit 0 — formatting failures must not block work
    sys.exit(0)


if __name__ == "__main__":
    main()
