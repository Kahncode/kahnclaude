#!/usr/bin/env python3
"""
p4-auto-add.py — Auto-add new files to Perforce for dev agents.

Event: PostToolUse
Matcher: Write

Only runs when agent_type is 'code-dev' or 'blueprint-dev'.
Runs `p4 add` on newly created files.

Exit codes:
  0 — Always (never blocks)
"""
import json
import subprocess
import sys
from pathlib import Path


DEV_AGENTS = {'code-dev', 'blueprint-dev'}


def main() -> None:
    try:
        raw = sys.stdin.read()
        # Strip BOM if present (PowerShell UTF-16 can add this)
        raw = raw.lstrip('﻿￾')
        if raw.startswith('\xef\xbb\xbf'):
            raw = raw[3:]
        data = json.loads(raw)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    # Only run for dev agents
    agent_type = data.get('agent_type')
    if agent_type not in DEV_AGENTS:
        sys.exit(0)

    # Get file path from tool input
    tool_input = data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    if not file_path:
        sys.exit(0)

    path = Path(file_path)

    # Skip if file doesn't exist (write failed?)
    if not path.exists():
        sys.exit(0)

    # Try to add the file
    try:
        result = subprocess.run(
            ['p4', 'add', str(path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = (result.stdout + result.stderr).strip()
        if 'opened for add' in output:
            print(f'[p4-auto-add] Added: {path.name}', file=sys.stderr)
        # Silent for: not under client root, already opened, can't add (existing file)
    except FileNotFoundError:
        print('[p4-auto-add] p4 command not found', file=sys.stderr)
    except subprocess.TimeoutExpired:
        print('[p4-auto-add] p4 add timed out', file=sys.stderr)
    except Exception as e:
        print(f'[p4-auto-add] Error: {e}', file=sys.stderr)

    sys.exit(0)


if __name__ == '__main__':
    main()
