#!/usr/bin/env python3
"""
lint-on-stop.py — Run linters at end of turn to surface issues early.

Event: Stop
Matcher: *

Detects project type and runs the appropriate linter(s). Always exits 0 —
lint failures are printed but never block Claude from completing a turn.
Secrets and .env checks are handled by verify-no-secrets.py and check-env-sync.py.
"""
import os
import shutil
import subprocess
import sys

VERBOSE = os.environ.get("CLAUDE_HOOK_VERBOSE", "false").lower() == "true"
TIMEOUT = 30


def log(msg: str) -> None:
    if VERBOSE:
        print(f"[lint-on-stop] {msg}", file=sys.stderr)


def run_check(name: str, cmd: list[str]) -> None:
    log(f"Running: {name}")
    try:
        subprocess.run(cmd, capture_output=True, timeout=TIMEOUT)
        log(f"OK {name}")
    except (subprocess.TimeoutExpired, OSError):
        log(f"SKIP {name} (unavailable or timed out)")


# -----------------------------------------------------------------------------
# Project type detection
# -----------------------------------------------------------------------------

def is_nodejs() -> bool:
    return os.path.isfile("package.json")


def is_typescript() -> bool:
    return os.path.isfile("tsconfig.json")


def is_python() -> bool:
    return any(
        os.path.isfile(f)
        for f in ("pyproject.toml", "setup.py", "requirements.txt")
    )


def is_rust() -> bool:
    return os.path.isfile("Cargo.toml")


def is_go() -> bool:
    return os.path.isfile("go.mod")


# -----------------------------------------------------------------------------
# Per-language lint runs
# -----------------------------------------------------------------------------

def lint_nodejs() -> None:
    log("Detected Node.js project")
    if not os.path.isdir("node_modules"):
        log("node_modules missing, skipping npm checks")
        return

    try:
        pkg = open("package.json").read()
    except OSError:
        return

    if '"lint"' in pkg:
        run_check("npm lint", ["npm", "run", "lint", "--silent"])

    if is_typescript():
        if '"typecheck"' in pkg:
            run_check("typecheck", ["npm", "run", "typecheck", "--silent"])
        elif shutil.which("tsc"):
            run_check("tsc", ["tsc", "--noEmit"])


def lint_python() -> None:
    log("Detected Python project")
    if shutil.which("ruff"):
        run_check("ruff", ["ruff", "check", ".", "--fix", "--silent"])
    if shutil.which("mypy") and (
        os.path.isfile("mypy.ini") or os.path.isfile("pyproject.toml")
    ):
        run_check("mypy", ["mypy", ".", "--silent-imports"])


def lint_rust() -> None:
    log("Detected Rust project")
    if shutil.which("cargo"):
        run_check("cargo check", ["cargo", "check", "--quiet"])
        run_check("clippy", ["cargo", "clippy", "--quiet", "--", "-D", "warnings"])


def lint_go() -> None:
    log("Detected Go project")
    if shutil.which("go"):
        run_check("go vet", ["go", "vet", "./..."])
    if shutil.which("staticcheck"):
        run_check("staticcheck", ["staticcheck", "./..."])


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    log("Starting lint-on-stop checks")

    if is_nodejs():
        lint_nodejs()
    if is_python():
        lint_python()
    if is_rust():
        lint_rust()
    if is_go():
        lint_go()

    log("lint-on-stop complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
