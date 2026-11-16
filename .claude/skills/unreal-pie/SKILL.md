---
name: unreal-pie
description: "Play In Editor manager. ALWAYS invoke when the user asks to start PIE, stop PIE, play in editor, or run a console command in PIE. Do not run PIE scripts directly — this skill manages session lifecycle and command execution."
allowed-tools: Bash(py *)
---

# Play In Editor (PIE)

Manage PIE sessions in the running Unreal Editor.

## Reference

See @docs/standards/unreal/pie.md for common console commands, PIE states, and troubleshooting.

## Required Variables

| Variable | Purpose |
|----------|---------|
| `UE_ENGINE` | UE engine root directory (read by the scripts) |

Set in the process env by `.claude/settings.local.json` `env` (the scripts read `UE_ENGINE` from it; never set it inline). The scripts live in `.claude/scripts/unreal/pie/`.

## Flow

### 1. Detect Intent

Parse `$ARGUMENTS` to determine the action:

| Input | Action |
|-------|--------|
| `start` or empty | Start a PIE session |
| `stop` | Stop the active PIE session |
| Anything else | Treat as a console command to execute in PIE |

### 2. Execute

#### Start PIE

```
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/pie/pie_start.py"
```

- Already running → report current status
- Success → "PIE session started."

#### Stop PIE

```
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/pie/pie_stop.py"
```

- Not running → "No PIE session is running."
- Success → "PIE session stopped."

#### Execute Console Command

```
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/pie/pie_exec.py" "<COMMAND>"
```

- PIE not running → "PIE is not running. Start it first."
- Success → show command output

## Notes

- Requires the editor to be running with Python Remote Execution enabled.
- PIE must be actively running before executing console commands.
