#!/usr/bin/env python3
"""
check-env-sync.py — Warn if .env has keys not documented in .env.example.

Only reads key NAMES, never values — safe to run anywhere.
Skips gracefully if either file is absent.

Event: Stop
Matcher: (none — Stop events have no matcher)

Exit codes:
  0 — Allow / no issues
  1 — Warning (missing keys printed to stderr, turn continues)
"""
import re
import subprocess
import sys
from pathlib import Path


_KEY_PATTERN = re.compile(r'^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=', re.MULTILINE)


def extract_keys(path: Path) -> set[str]:
    """Extract variable names from a .env-style file."""
    try:
        content = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return set()
    return set(_KEY_PATTERN.findall(content))


def find_repo_root() -> Path | None:
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return None


def main() -> None:
    root = find_repo_root()
    if root is None:
        sys.exit(0)

    env_file = root / '.env'
    example_file = root / '.env.example'

    if not env_file.exists() or not example_file.exists():
        sys.exit(0)

    env_keys = extract_keys(env_file)
    example_keys = extract_keys(example_file)

    missing = sorted(env_keys - example_keys)
    if missing:
        print("", file=sys.stderr)
        print("ENV SYNC: Keys in .env missing from .env.example:", file=sys.stderr)
        for key in missing:
            print(f"  - {key}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Other developers won't know these variables exist.", file=sys.stderr)
        print("Add them to .env.example with placeholder values.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
