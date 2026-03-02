#!/usr/bin/env python3
"""
check-branch.py — Block direct commits to main/master when branch protection is active.

Activation (either condition enables protection):
  - Environment variable KC_BRANCH_PROTECT=true
  - Marker file .claude/branch-protection exists in the git repo

Event: PreToolUse
Matcher: Bash

Exit codes:
  0 — Allow / no action
  2 — Block (printed to stderr, operation stopped)
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PROTECTED_BRANCHES = {'main', 'master'}


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout.strip()


def is_protection_enabled(repo_root: str) -> bool:
    """Return True if branch protection is active for this repo."""
    if os.environ.get('KC_BRANCH_PROTECT', '').lower() == 'true':
        return True
    marker = Path(repo_root) / '.claude' / 'branch-protection'
    return marker.exists()


def get_repo_root(cwd: str | None = None) -> str | None:
    code, out = run(['git', 'rev-parse', '--show-toplevel'], cwd=cwd)
    return out if code == 0 else None


def get_branch(cwd: str | None = None) -> str | None:
    code, out = run(['git', 'branch', '--show-current'], cwd=cwd)
    return out if code == 0 else None


def has_commits(cwd: str | None = None) -> bool:
    code, _ = run(['git', 'rev-parse', 'HEAD'], cwd=cwd)
    return code == 0


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    command = data.get('tool_input', {}).get('command', '')
    if not command:
        sys.exit(0)

    # Only check git commit commands
    if not re.search(r'\bgit\s+commit\b', command):
        sys.exit(0)

    # Detect if git -C <path> was used — check that repo instead of CWD
    git_c_match = re.search(r'\bgit\s+-C\s+([^\s<>]+)', command)
    target_dir: str | None = None
    if git_c_match:
        candidate = git_c_match.group(1)
        # Ignore shell placeholders like <dir>
        if not candidate.startswith('<') and Path(candidate).is_dir():
            target_dir = candidate

    # Resolve git context
    cwd_arg = target_dir  # None = current working directory

    repo_root = get_repo_root(cwd=cwd_arg)
    if not repo_root:
        sys.exit(0)  # not a git repo

    if not has_commits(cwd=cwd_arg):
        sys.exit(0)  # allow initial commit

    branch = get_branch(cwd=cwd_arg)
    if not branch or branch not in PROTECTED_BRANCHES:
        sys.exit(0)

    if not is_protection_enabled(repo_root):
        sys.exit(0)

    print(
        f"BLOCKED: Direct commit to '{branch}' is not allowed.",
        file=sys.stderr,
    )
    print("Create a feature branch first:", file=sys.stderr)
    print(f"  git checkout -b feat/<feature-name>", file=sys.stderr)
    print("  Or use: /worktree <name>", file=sys.stderr)
    print("", file=sys.stderr)
    print("To disable: set KC_BRANCH_PROTECT=false or remove .claude/branch-protection", file=sys.stderr)
    sys.exit(2)


if __name__ == '__main__':
    main()
