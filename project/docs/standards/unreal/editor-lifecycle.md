# Editor Lifecycle Reference

## Script

**Location:** `$KC_PROJECT_ROOT/.claude/scripts/editor/close-editor.ps1`

This PowerShell script manages the Unreal Editor process. It lives in the target project (installed via `/kc:install`), not in the KahnClaude skill directory.

## Interface

| Flag | Behavior |
|------|----------|
| _(none)_ | Graceful close: sends WM_CLOSE to the editor's main window |
| `-Force` | Force kill: terminates the process immediately |

## Graceful Close Behavior

1. Finds the running Unreal Editor process
2. Sends a close signal to the main window
3. The editor may prompt the user to save unsaved changes
4. Waits up to 30 seconds for the process to exit
5. If the process is still running after 30s, reports timeout

## Force Kill Behavior

1. Finds the running Unreal Editor process
2. Kills the process immediately
3. No save prompt — unsaved changes are lost

## Environment Requirements

| Variable | Required | Purpose |
|----------|----------|---------|
| `KC_PROJECT_ROOT` | Yes | Locates the script at `.claude/scripts/editor/close-editor.ps1` |
