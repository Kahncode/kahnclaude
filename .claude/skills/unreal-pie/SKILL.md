---
name: unreal-pie
description: "Play In Editor manager. ALWAYS invoke when the user asks to start PIE, stop PIE, play in editor, or run a console command in PIE. Do not run PIE scripts directly — this skill manages session lifecycle and command execution."
allowed-tools: Bash(python3 *)
---

# Play In Editor (PIE)

Manage PIE sessions in the running Unreal Editor.

## Reference

See @docs/standards/unreal/pie.md for common console commands, PIE states, and troubleshooting.

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `KC_PROJECT_ROOT` | Workspace root (parent of `.claude/`) |
| `KC_UE_ENGINE` | UE root directory |

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

```bash
python3 "$KC_PROJECT_ROOT/.claude/scripts/unreal/pie/pie_start.py"
```

- Already running → report current status
- Success → "PIE session started."

#### Stop PIE

```bash
python3 "$KC_PROJECT_ROOT/.claude/scripts/unreal/pie/pie_stop.py"
```

- Not running → "No PIE session is running."
- Success → "PIE session stopped."

#### Execute Console Command

```bash
python3 "$KC_PROJECT_ROOT/.claude/scripts/unreal/pie/pie_exec.py" "$COMMAND"
```

- PIE not running → "PIE is not running. Start it first."
- Success → show command output

## Notes

- Requires the editor to be running with Python Remote Execution enabled.
- PIE must be actively running before executing console commands.
