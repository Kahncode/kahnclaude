#!/usr/bin/env python3
"""
verify-no-secrets.py — Scan Perforce opened files for accidentally committed secrets.

Runs when Claude finishes a turn. Catches secrets before they reach a submit.
Warns (exit 1) on findings — does NOT block (exit 2) since the submit hasn't
happened yet; the user can review and revert before submitting.

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


# Basenames of files that should never be submitted
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

# Regex patterns checked against opened file contents
SECRET_CONTENT_PATTERNS = [
    (re.compile(r'(api[_\-]?key|secret[_\-]?key|password|token)\s*[:=]\s*["\'][A-Za-z0-9+/=_\-]{16,}', re.IGNORECASE), 'POSSIBLE SECRET'),
    (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS ACCESS KEY'),
    (re.compile(r'(ghp_[A-Za-z0-9]{36,}|gho_[A-Za-z0-9]{36,}|ghs_[A-Za-z0-9]{36,}|ghr_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})'), 'GITHUB TOKEN'),
    (re.compile(r'(xoxb-|xoxp-|xoxo-|xoxa-)[0-9A-Za-z\-]{20,}'), 'SLACK TOKEN'),
    (re.compile(r'(sk_live_|pk_live_|rk_live_)[A-Za-z0-9]{20,}'), 'STRIPE KEY'),
    (re.compile(r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'), 'PEM PRIVATE KEY'),
]


def run(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


def get_opened_local_paths() -> list[str]:
    """Get local paths of all P4 opened files via p4 opened + p4 where."""
    opened_output = run(['p4', 'opened'])
    if not opened_output:
        return []

    depot_files = []
    for line in opened_output.splitlines():
        if '#' in line:
            depot_path = line.split('#')[0].strip()
            depot_files.append(depot_path)

    if not depot_files:
        return []

    # Resolve depot paths to local paths
    local_paths = []
    where_output = run(['p4', 'where'] + depot_files)
    if where_output:
        for line in where_output.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                # p4 where output: depot_path client_path local_path
                local_paths.append(parts[-1])

    return local_paths


def main() -> None:
    local_paths = get_opened_local_paths()
    if not local_paths:
        sys.exit(0)

    violations: list[str] = []

    for file_str in local_paths:
        path = Path(file_str)
        name = path.name

        # Check sensitive basenames
        if name in SENSITIVE_BASENAMES:
            violations.append(f"  - SENSITIVE FILE OPENED: {file_str}")
            continue

        # Check private key filenames
        if name in PRIVATE_KEY_NAMES or path.suffix in PRIVATE_KEY_EXTENSIONS:
            violations.append(f"  - PRIVATE KEY FILE OPENED: {file_str}")
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
        print("WARNING: POTENTIAL SECRETS DETECTED IN OPENED FILES:", file=sys.stderr)
        for v in violations:
            print(v, file=sys.stderr)
        print("", file=sys.stderr)
        print("Review opened files before submitting.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
