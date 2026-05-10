#!/usr/bin/env python3
"""
p4-commands-permission.py — Permission gate for P4 Bash commands.

Event: PreToolUse
Matcher: Bash

Safe p4 subcommands get permissionDecision "allow".
Dangerous p4 subcommands get permissionDecision "deny".
Non-p4 commands and unknown subcommands get no opinion (exit 0).
"""
import json
import re
import sys

SAFE_SUBCOMMANDS = frozenset({
    "status",
    "opened",
    "changes",
    "diff",
    "describe",
    "client",
    "stream",
    "shelve",
    "edit",
    "add",
    "filelog",
    "files",
    "info",
    "change",
    "reopen",
    "set",
    "print",
    "property",
})

BLOCKED_SUBCOMMANDS = frozenset({
    "submit",
    "obliterate",
    "admin",
    "protect",
    "counter",
})

BLOCK_REASONS = {
    "submit": "Create a pending changelist or shelve instead.",
    "obliterate": "p4 obliterate permanently destroys files.",
    "admin": "p4 admin commands are not allowed.",
    "protect": "p4 protect commands are not allowed.",
    "counter": "p4 counter commands are not allowed.",
}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    match = re.search(r"\bp4(?:\s+-\w+)*\s+(\w+)", command)
    if not match:
        sys.exit(0)

    subcommand = match.group(1)

    if subcommand in SAFE_SUBCOMMANDS:
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": f"Safe p4 command: p4 {subcommand}",
            }
        }, sys.stdout)
        return

    if subcommand in BLOCKED_SUBCOMMANDS:
        reason = BLOCK_REASONS.get(subcommand, "Blocked by policy.")
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"BLOCKED: p4 {subcommand} — {reason}",
            }
        }, sys.stdout)
        return

    # Unknown subcommand — no opinion, will prompt user
    sys.exit(0)


if __name__ == "__main__":
    main()
