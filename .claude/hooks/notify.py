#!/usr/bin/env python3
"""
notify.py — Send desktop notifications when Claude needs attention.

Event: Notification
Matcher: *

Cross-platform:
  Windows  — PowerShell toast notification
  macOS    — osascript
  Linux    — notify-send (or PowerShell toast if WSL)
  Fallback — terminal bell
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def send_windows(title: str, message: str) -> None:
    title_esc = title.replace("'", "''")
    msg_esc = message.replace("'", "''")
    ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = '<toast><visual><binding template="ToastText02"><text id="1">{title_esc}</text><text id="2">{msg_esc}</text></binding></visual></toast>'
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Claude Code').Show($toast)
"""
    subprocess.run(  # noqa: S603
        ["powershell.exe", "-NoProfile", "-Command", ps_script],  # noqa: S607
        capture_output=True,
        timeout=10,
        check=False,
    )


def send_macos(title: str, message: str) -> None:
    script = f'display notification "{message}" with title "{title}" sound name "Glass"'
    subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10, check=False)  # noqa: S603, S607


def send_linux(title: str, message: str) -> None:
    subprocess.run(  # noqa: S603
        ["notify-send", title, message, "-u", "normal", "-t", "5000"],  # noqa: S607
        capture_output=True,
        timeout=10,
        check=False,
    )


def send_notification(title: str, message: str) -> None:
    system = platform.system()

    try:
        if system == "Windows":
            send_windows(title, message)
            return

        if system == "Darwin":
            send_macos(title, message)
            return

        if system == "Linux":
            # Check for WSL — route to Windows toast
            try:
                if "microsoft" in Path("/proc/version").read_text().lower():
                    send_windows(title, message)
                    return
            except OSError:
                pass

            if shutil.which("notify-send"):
                send_linux(title, message)
                return

    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        pass

    # Fallback: terminal bell
    sys.stdout.write("\a")
    sys.stdout.flush()


MAX_MESSAGE_LENGTH = 100


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    content = data.get("content", "Claude needs your attention")

    # Get folder name from project directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", str(Path.cwd()))
    folder_name = Path(project_dir).name

    # Build message with folder context
    message = f"[{folder_name}] {content}"
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[:MAX_MESSAGE_LENGTH] + "..."

    send_notification("Claude Code", message)
    sys.exit(0)


if __name__ == "__main__":
    main()
