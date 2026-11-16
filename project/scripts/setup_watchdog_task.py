"""Setup / teardown the Claude Remote Control Watchdog scheduled task.

Usage:
    python setup_watchdog_task.py            # Create the scheduled task
    python setup_watchdog_task.py --remove   # Remove the scheduled task
    python setup_watchdog_task.py --status   # Check if the task exists
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

TASK_NAME = "ClaudeRemoteControlWatchdog"
WATCHDOG_SCRIPT = Path(__file__).resolve().parent / "claude_remote_watchdog.py"


def find_python() -> str:
    """Return the full path to the Python interpreter."""
    python = shutil.which("python") or shutil.which("python3") or sys.executable
    return str(Path(python).resolve())


def create_task() -> None:
    """Register the watchdog as a Windows Task Scheduler task (every 10 min)."""
    python_path = find_python()

    if not WATCHDOG_SCRIPT.exists():
        print(f"Error: watchdog script not found at {WATCHDOG_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    # Build the schtasks command
    trigger_cmd = (
        f'"{python_path}" "{WATCHDOG_SCRIPT}"'
    )
    cmd = [
        "schtasks", "/create",
        "/tn", TASK_NAME,
        "/tr", trigger_cmd,
        "/sc", "minute",
        "/mo", "5",
        "/f",  # force overwrite if exists
    ]

    print(f"Creating scheduled task '{TASK_NAME}'...")
    print(f"  Python:  {python_path}")
    print(f"  Script:  {WATCHDOG_SCRIPT}")
    print(f"  Schedule: every 5 minutes")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' created successfully.")
        print()
        print("Verify with:")
        print(f'  schtasks /query /tn "{TASK_NAME}"')
        print()
        print("To run it immediately:")
        print(f'  schtasks /run /tn "{TASK_NAME}"')
    else:
        print(f"Error creating task (exit code {result.returncode}):", file=sys.stderr)
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(1)


def remove_task() -> None:
    """Remove the watchdog scheduled task."""
    print(f"Removing scheduled task '{TASK_NAME}'...")
    result = subprocess.run(
        ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' removed successfully.")
    else:
        print(f"Error removing task (exit code {result.returncode}):", file=sys.stderr)
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(1)


def check_status() -> None:
    """Check if the scheduled task exists and show its status."""
    result = subprocess.run(
        ["schtasks", "/query", "/tn", TASK_NAME, "/fo", "LIST", "/v"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' exists:\n")
        # Show relevant lines
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if stripped and any(
                stripped.startswith(prefix)
                for prefix in ("TaskName:", "Status:", "Next Run Time:", "Last Run Time:", "Schedule Type:", "Repeat:")
            ):
                print(f"  {stripped}")
    else:
        print(f"Task '{TASK_NAME}' does not exist.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Setup or remove the Claude Remote Control Watchdog scheduled task."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--remove", action="store_true", help="Remove the scheduled task")
    group.add_argument("--status", action="store_true", help="Check task status")
    args = parser.parse_args()

    if args.remove:
        remove_task()
    elif args.status:
        check_status()
    else:
        create_task()


if __name__ == "__main__":
    main()
