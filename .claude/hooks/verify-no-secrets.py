#!/usr/bin/env python3
"""
verify-no-secrets.py — Scan staged git files for accidentally committed secrets.

Runs when Claude finishes a turn. Catches secrets before they reach a commit.
Warns (exit 1) on findings — does NOT block (exit 2) since the commit hasn't
happened yet; the user can review and unstage before committing.

Event: Stop
Matcher: (none — Stop events have no matcher)

Exit codes:
  0 — Allow / no issues found
  1 — Warning (violations printed to stderr, turn continues)
"""
import re
import subprocess
import sys
from pathlib import Path


# Basenames of files that should never be staged
SENSITIVE_BASENAMES = {
    '.env',
    '.env.local',
    '.env.production',
    '.env.staging',
    'secrets.json',
    'credentials.json',
    'service-account.json',
    '.npmrc',
}

# Private key file extensions / exact basenames
PRIVATE_KEY_NAMES = {'id_rsa', 'id_ed25519', 'id_ecdsa', 'id_dsa'}
PRIVATE_KEY_EXTENSIONS = {'.pem', '.key'}

# Regex patterns checked against staged file contents
SECRET_CONTENT_PATTERNS = [
    (re.compile(r'(api[_\-]?key|secret[_\-]?key|password|token)\s*[:=]\s*["\'][A-Za-z0-9+/=_\-]{16,}', re.IGNORECASE), 'POSSIBLE SECRET'),
    (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS ACCESS KEY'),
    (re.compile(r'(ghp_[A-Za-z0-9]{36,}|gho_[A-Za-z0-9]{36,}|ghs_[A-Za-z0-9]{36,}|ghr_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})'), 'GITHUB TOKEN'),
    (re.compile(r'(xoxb-|xoxp-|xoxo-|xoxa-)[0-9A-Za-z\-]{20,}'), 'SLACK TOKEN'),
    (re.compile(r'(sk_live_|pk_live_|rk_live_)[A-Za-z0-9]{20,}'), 'STRIPE KEY'),
    (re.compile(r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'), 'PEM PRIVATE KEY'),
]


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def main() -> None:
    # Only run inside a git repo
    check = subprocess.run(
        ['git', 'rev-parse', '--is-inside-work-tree'],
        capture_output=True,
    )
    if check.returncode != 0:
        sys.exit(0)

    staged_output = run(['git', 'diff', '--cached', '--name-only'])
    if not staged_output:
        sys.exit(0)

    staged_files = [f for f in staged_output.splitlines() if f]
    violations: list[str] = []

    for file_str in staged_files:
        path = Path(file_str)
        name = path.name

        # Check sensitive basenames
        if name in SENSITIVE_BASENAMES:
            violations.append(f"  - SENSITIVE FILE STAGED: {file_str}")
            continue

        # Check private key filenames
        if name in PRIVATE_KEY_NAMES or path.suffix in PRIVATE_KEY_EXTENSIONS:
            violations.append(f"  - PRIVATE KEY FILE STAGED: {file_str}")
            continue

        # Check file contents for secret patterns
        if path.is_file():
            try:
                content = path.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            for pattern, label in SECRET_CONTENT_PATTERNS:
                if pattern.search(content):
                    violations.append(f"  - {label} in {file_str}")
                    break  # one violation per file is enough

    if violations:
        print("WARNING: POTENTIAL SECRETS DETECTED:", file=sys.stderr)
        for v in violations:
            print(v, file=sys.stderr)
        print("", file=sys.stderr)
        print("Review staged files before committing.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
