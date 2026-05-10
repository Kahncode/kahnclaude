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


def block(message: str, detail: str = "", tip: str = "") -> None:
    print(message, file=sys.stderr)
    if detail:
        print(f"Detail: {detail}", file=sys.stderr)
    if tip:
        print(f"Tip: {tip}", file=sys.stderr)
    sys.exit(2)


def check_bash_command(command: str) -> None:
    """Block dangerous Bash commands."""
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

    # git reset --hard (destroys uncommitted changes)
    if re.search(r"git\s+reset\s+--hard", command):
        block(
            "BLOCKED: git reset --hard destroys uncommitted changes",
            command,
            "Use 'git stash' to preserve changes, or 'git reset' without --hard",
        )

    # git clean -f (deletes untracked files)
    if re.search(r"git\s+clean\s+.*-[a-zA-Z]*f", command):
        block(
            "BLOCKED: git clean -f permanently deletes untracked files",
            command,
            "Use 'git clean -n' (dry run) first to see what would be deleted",
        )

    # git push --force to any branch (not just protected ones)
    if re.search(r"git\s+push\s+.*(-f|--force-with-lease|--force)", command):
        block(
            "BLOCKED: Force push can overwrite remote history",
            command,
            "Push without --force, or ask the user to run this manually",
        )

    # rm -rf without safe path restrictions (catch broader patterns)
    if re.search(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-rf|-fr)\b", command):
        # Allow rm -rf on clearly safe paths like node_modules, __pycache__, .cache, build, dist
        safe_targets = r"\s+(node_modules|__pycache__|\.cache|\.pytest_cache|build|dist|\.tox|\.mypy_cache|\.ruff_cache)"
        if not re.search(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-rf|-fr)" + safe_targets, command):
            block(
                "BLOCKED: rm -rf on non-standard target — review carefully",
                command,
                "Only rm -rf on known build artifacts (node_modules, __pycache__, build, dist)",
            )

    # DROP TABLE / DROP DATABASE (SQL destruction)
    if re.search(r"DROP\s+(TABLE|DATABASE|SCHEMA|INDEX)", command, re.IGNORECASE):
        block("BLOCKED: Destructive SQL command", command)

    # kill -9 / kill -KILL on PID 1 or system processes
    if re.search(r"kill\s+(-9|-KILL|-SIGKILL)\s+(1|0|-1)\b", command):
        block("BLOCKED: Killing system-critical processes", command)

    # Exfiltrating via base64 encoding tricks
    if re.search(r"base64\s+.*\.(env|pem|key|secret|credentials)", command):
        block("BLOCKED: Encoding sensitive files (potential exfiltration)", command)

    # env / printenv / set — can leak secrets
    if re.search(r"^(env|printenv|set)$", command.strip()):
        block(
            "BLOCKED: Dumping all environment variables may expose secrets",
            command,
            "Access specific variables with 'echo $VAR_NAME' instead",
        )

    # echo / printf of sensitive env vars
    sensitive_var_patterns = (
        r"(TOKEN|SECRET|KEY|PASSWORD|PASSWD|CREDENTIAL|AUTH"
        r"|API_KEY|APIKEY|PRIVATE|ACCESS_KEY|SESSION"
        r"|BEARER|OAUTH|JWT|SIGNING|ENCRYPTION|ENCRYPT"
        r"|CONN_STRING|CONNECTION_STRING|DATABASE_URL|DB_URL|DB_PASS"
        r"|MONGO_URI|REDIS_URL|REDIS_PASS|AMQP_URL"
        r"|SMTP_PASS|MAIL_PASS|EMAIL_PASS"
        r"|AWS_SECRET|AZURE_KEY|GCP_KEY|CLOUD_KEY"
        r"|STRIPE|TWILIO|SENDGRID|SLACK_TOKEN|SLACK_WEBHOOK"
        r"|WEBHOOK_SECRET|SIGNING_KEY|HMAC"
        r"|CLIENT_SECRET|APP_SECRET|MASTER_KEY"
        r"|CERTIFICATE|CERT_KEY|TLS_KEY|SSL_KEY"
        r"|PASSPHRASE|PIN_CODE|MFA|OTP_SECRET|TOTP"
        r"|GITHUB_TOKEN|GH_TOKEN|GITLAB_TOKEN|BITBUCKET"
        r"|NPM_TOKEN|PYPI_TOKEN|NUGET_KEY|DOCKER_PASS"
        r"|ANTHROPIC|OPENAI|COHERE|HUGGING|REPLICATE)"
    )
    if re.search(
        r"(echo|printf)\s+.*\$\{?" + sensitive_var_patterns,
        command,
        re.IGNORECASE,
    ):
        block(
            "BLOCKED: Echoing a variable that likely contains a secret",
            command,
            "If you need to verify a token is set, use: [ -n \"$VAR\" ] && echo 'set' || echo 'not set'",
        )

    # Docker destructive commands
    if re.search(r"docker\s+(system\s+prune|rm\s+-f|rmi\s+-f)", command):
        block("BLOCKED: Destructive Docker command", command)

    # kubectl delete on production namespaces
    if re.search(r"kubectl\s+delete\s+.*(--all|namespace|prod)", command):
        block("BLOCKED: Destructive kubectl command targeting production", command)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if command:
        check_bash_command(command)

    sys.exit(0)


if __name__ == "__main__":
    main()
