#!/usr/bin/env python3
"""
block-dangerous-commands.py — Block destructive or unsafe Bash commands.

Event: PreToolUse
Matcher: Bash

Exit codes:
  0 — Allow / no action
  2 — Block (printed to stderr, operation stopped)
"""
import json
import re
import sys


def block(message: str, command: str, tip: str = "") -> None:
    print(message, file=sys.stderr)
    print(f"Command: {command}", file=sys.stderr)
    if tip:
        print(f"Tip: {tip}", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    # rm -rf targeting root, home, or parent directory
    if re.search(
        r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|--recursive\s+--force|-rf|-fr)\s+(/|~|\.\.|\$HOME|\$\{HOME\})",
        command,
    ):
        block(
            "BLOCKED: Destructive rm command targeting root, home, or parent directory",
            command,
        )

    # rm -rf /* or rm -rf ~/*
    if re.search(
        r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|--recursive\s+--force|-rf|-fr)\s+(/\*|~/\*|/home)",
        command,
    ):
        block(
            "BLOCKED: Destructive rm command with wildcard on sensitive path",
            command,
        )

    # Force push to main/master/production/release
    if re.search(
        r"git\s+push\s+.*(-f|--force)\s+.*(main|master|production|release)",
        command,
    ):
        block(
            "BLOCKED: Force push to protected branch",
            command,
            "Create a PR instead of force pushing to main/master",
        )

    # chmod 777 (world-writable)
    if re.search(r"chmod\s+(777|a\+rwx)", command):
        block(
            "BLOCKED: Setting world-writable permissions (777)",
            command,
            "Use 755 for directories, 644 for files",
        )

    # Piping curl directly to shell
    if re.search(r"curl\s+.*\|\s*(ba)?sh", command):
        block(
            "BLOCKED: Piping curl output directly to shell",
            command,
            "Download script first, review it, then execute",
        )

    # wget piped to shell
    if re.search(r"wget\s+.*\|\s*(ba)?sh", command):
        block("BLOCKED: Piping wget output directly to shell", command)

    # dd writing to disk devices
    if re.search(r"dd\s+.*of=/dev/(sd|hd|nvme|disk)", command):
        block("BLOCKED: dd command writing directly to disk device", command)

    # mkfs (format disk)
    if re.search(r"mkfs", command):
        block("BLOCKED: mkfs command (disk formatting)", command)

    # Exfiltrating sensitive files via network tools
    if re.search(r"(curl|wget|nc|netcat)\s+.*\.(env|pem|key|secret)", command):
        block("BLOCKED: Command appears to exfiltrate sensitive files", command)

    # Reading .env files via shell commands
    if re.search(r"(cat|less|head|tail|more|bat)\s+.*\.env", command):
        block(
            "BLOCKED: Reading .env file via shell command",
            command,
            "Use environment variables instead of reading .env directly",
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
