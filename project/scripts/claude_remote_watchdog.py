"""Claude Remote Control Watchdog

Ensures a Claude Code remote-control session is always running WITH active
sessions. Designed to be invoked every 5 minutes by Windows Task Scheduler.

Each invocation:
  1. Queries running processes for the 'claude remote-control' server
  2. If no server found, launches one
  3. If server found but has 0 active sessions (no child processes)
     and has been running > GRACE_PERIOD_MINUTES, kills and relaunches
  4. Appends timestamped log entries to LOG_FILE
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration — edit these to match your setup
# ---------------------------------------------------------------------------

PROJECT_DIR = os.environ.get("CLAUDE_REMOTE_PROJECT_DIR", str(Path.home()))
SESSION_NAME_PREFIX = "<user>'s PC"
LOG_FILE = Path.home() / ".claude" / "remote-watchdog.log"
GRACE_PERIOD_MINUTES = 5  # Don't restart a freshly launched server

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    """Append a timestamped line to the log file and print to stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as exc:
        print(f"Warning: could not write to log file: {exc}", file=sys.stderr)


def run_ps(command: str) -> str:
    """Run a PowerShell command and return stdout, or empty string on error."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


def get_server_processes() -> list[dict]:
    """Find claude remote-control server processes.

    Returns list of dicts with 'pid' and 'created' (datetime or None).
    """
    ps_command = (
        "Get-CimInstance Win32_Process "
        "| Where-Object { "
        "$_.CommandLine -match 'remote-control' -and "
        "$_.CommandLine -match 'claude' -and "
        "$_.CommandLine -notmatch 'Get-CimInstance' -and "
        "$_.CommandLine -notmatch 'claude_remote_watchdog' "
        "} "
        "| ForEach-Object { "
        "$_.ProcessId.ToString() + '|' + $_.CreationDate.ToString('yyyy-MM-dd HH:mm:ss') + '|' + $_.CommandLine "
        "}"
    )
    output = run_ps(ps_command)
    if not output:
        return []

    servers = []
    for line in output.splitlines():
        parts = line.split("|", 2)
        if len(parts) >= 2:
            try:
                pid = int(parts[0].strip())
                created = datetime.strptime(parts[1].strip(), "%Y-%m-%d %H:%M:%S")
                cmdline = parts[2].strip() if len(parts) > 2 else ""
                servers.append({"pid": pid, "created": created, "cmdline": cmdline})
            except (ValueError, IndexError):
                continue
    return servers


def count_child_processes(pid: int) -> int:
    """Count child processes of a given PID."""
    ps_command = (
        f"(Get-CimInstance Win32_Process "
        f"| Where-Object {{ $_.ParentProcessId -eq {pid} }}"
        f"| Measure-Object).Count"
    )
    output = run_ps(ps_command)
    try:
        return int(output)
    except ValueError:
        return -1  # Unknown


def kill_process(pid: int) -> bool:
    """Kill a process by PID using taskkill."""
    try:
        result = subprocess.run(
            ["taskkill", "/pid", str(pid), "/t", "/f"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def build_session_name() -> str:
    """Build session name with prefix + date + hour."""
    now = datetime.now()
    return f"{SESSION_NAME_PREFIX} {now.strftime('%Y-%m-%d %Hh%M')}"


def launch_remote_control() -> None:
    """Launch Windows Terminal with claude remote-control."""
    session_name = build_session_name()
    cmd = [
        "wt.exe",
        "new-tab",
        "--title", "Claude Remote Control",
        "-d", PROJECT_DIR,
        "--",
        "claude", "remote-control",
        "--name", session_name,
    ]
    log(f"Launching: {' '.join(cmd)}")
    try:
        subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        log("Launch command sent successfully")
    except OSError as exc:
        log(f"Error launching Windows Terminal: {exc}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    log("Watchdog check starting")

    servers = get_server_processes()

    if not servers:
        log("No remote-control server found")
        launch_remote_control()
        log("Watchdog check complete")
        return

    for server in servers:
        pid = server["pid"]
        created = server["created"]
        age_minutes = (datetime.now() - created).total_seconds() / 60
        children = count_child_processes(pid)
        cmdline_short = server["cmdline"][:100]

        log(f"Server PID {pid} | age {age_minutes:.0f}m | children {children} | {cmdline_short}")

        if children > 0:
            log("Active sessions detected — all good")
            log("Watchdog check complete")
            return

    # All servers have 0 children
    server = servers[0]
    age_minutes = (datetime.now() - server["created"]).total_seconds() / 60

    if age_minutes < GRACE_PERIOD_MINUTES:
        log(f"Server is fresh ({age_minutes:.0f}m old, grace period {GRACE_PERIOD_MINUTES}m) — skipping restart")
    else:
        log(f"Server has 0 sessions and is {age_minutes:.0f}m old — killing and relaunching")
        for s in servers:
            kill_process(s["pid"])
        time.sleep(2)
        launch_remote_control()

    log("Watchdog check complete")


if __name__ == "__main__":
    main()
