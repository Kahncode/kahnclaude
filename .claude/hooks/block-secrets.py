#!/usr/bin/env python3
"""
block-secrets.py — Prevent Claude from reading or editing sensitive files.

Event: PreToolUse
Matcher: Read|Edit|Write

Exit codes:
  0 — Allow / no action
  2 — Block (printed to stderr, operation stopped)
"""
import json
import sys
from pathlib import Path


# Files that should NEVER be read or edited by Claude
SENSITIVE_FILENAMES = {
    '.env',
    '.env.local',
    '.env.production',
    '.env.staging',
    '.env.development',
    '.env.test',
    '.secrets',
    'secrets.json',
    'secrets.yaml',
    'secrets.yml',
    'secrets.toml',
    'id_rsa',
    'id_ed25519',
    '.npmrc',        # may contain auth tokens
    '.pypirc',       # PyPI auth tokens
    '.pgpass',       # PostgreSQL passwords
    '.my.cnf',       # MySQL credentials
    '.mongorc.js',   # MongoDB credentials
    '.git-credentials',
    '.gitconfig',
    '.yarnrc',       # may contain auth tokens
    'credentials.json',
    'service-account.json',
    '.docker/config.json',
}

# Substrings in file paths that indicate sensitive content
SENSITIVE_PATTERNS = [
    'aws/credentials',
    'aws/config',
    '.ssh/',
    'private_key',
    'secret_key',
    'gcloud/credentials.db',
    '.azure/credentials',
]

# File extensions that indicate key material or certificates
SENSITIVE_EXTENSIONS = {
    '.p12',
    '.pfx',
    '.jks',
    '.keystore',
    '.cer',
    '.pem',
    '.key',
}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    file_path = data.get('tool_input', {}).get('file_path', '')

    if not file_path:
        sys.exit(0)

    path = Path(file_path)

    # Allow Write to .env files (project setup may need to create them).
    # Only block Read/Edit which could leak existing secret values.
    if tool_name == 'Write' and path.name.startswith('.env'):
        sys.exit(0)

    # Check exact filename matches
    if path.name in SENSITIVE_FILENAMES:
        print(
            f"BLOCKED: Access to '{file_path}' denied. This is a sensitive file.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Check path pattern matches
    path_str = str(path).replace('\\', '/')
    for pattern in SENSITIVE_PATTERNS:
        if pattern in path_str:
            print(
                f"BLOCKED: Access to '{file_path}' denied."
                f" Path matches sensitive pattern '{pattern}'.",
                file=sys.stderr,
            )
            sys.exit(2)

    # Check file extension matches
    if path.suffix.lower() in SENSITIVE_EXTENSIONS:
        print(
            f"BLOCKED: Access to '{file_path}' denied."
            f" Extension '{path.suffix}' indicates key material or certificate.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
