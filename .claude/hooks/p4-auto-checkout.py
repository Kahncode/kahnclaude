#!/usr/bin/env python3
"""
p4-auto-checkout.py — Auto-checkout files before edit for dev agents.

Event: PreToolUse
Matcher: Edit|Write

Only runs when agent_type is 'code-dev' or 'blueprint-dev'.
Runs `p4 edit` on the file before modification.

Exit codes:
  0 — Always (never blocks edits)
"""
import json
import os
import subprocess
import sys
from pathlib import Path


DEV_AGENTS = {'code-dev', 'blueprint-dev'}


def main() -> None:
    try:
        raw = sys.stdin.read()
        # Strip BOM if present (U+FEFF or UTF-8 BOM bytes)
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

    # Skip if file doesn't exist (new file — will need p4 add later)
    if not path.exists():
        sys.exit(0)

    # Skip if file is already writable (already checked out or not in P4)
    if os.access(path, os.W_OK):
        sys.exit(0)

    # Try to checkout the file
    try:
        result = subprocess.run(
            ['p4', 'edit', str(path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # p4 returns 0 even on some errors; check output to confirm success
        output = (result.stdout + result.stderr).strip()
        if 'opened for edit' in output:
            print(f'[p4-auto-checkout] Checked out: {path.name}', file=sys.stderr)
        elif 'not on client' in output or 'not under client' in output:
            # Not in depot — silent, this is expected for local-only files
            pass
        elif 'already opened' in output:
            print(f'[p4-auto-checkout] Already opened: {path.name}', file=sys.stderr)
        elif result.returncode != 0:
            print(f'[p4-auto-checkout] p4 edit failed: {output}', file=sys.stderr)
    except FileNotFoundError:
        # p4 not installed or not in PATH
        print('[p4-auto-checkout] p4 command not found', file=sys.stderr)
    except subprocess.TimeoutExpired:
        print('[p4-auto-checkout] p4 edit timed out', file=sys.stderr)
    except Exception as e:
        print(f'[p4-auto-checkout] Error: {e}', file=sys.stderr)

    # Never block edits
    sys.exit(0)


if __name__ == '__main__':
    main()
