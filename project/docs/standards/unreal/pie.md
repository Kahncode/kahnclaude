# PIE Reference

## Common Console Commands

| Command | Effect |
|---------|--------|
| `God` | Toggle god mode (invulnerability) |
| `Fly` | Toggle fly mode |
| `Ghost` | Toggle ghost mode (noclip + fly) |
| `Teleport` | Teleport to crosshair location |
| `Slomo <float>` | Set game speed (1.0 = normal, 0.5 = half, 2.0 = double) |
| `ShowDebug` | Toggle debug overlay |
| `ShowDebug AbilitySystem` | Show GAS debug info |
| `ShowDebug Animation` | Show animation debug info |
| `Stat FPS` | Toggle FPS counter |
| `Stat Unit` | Toggle frame timing breakdown |
| `Stat Game` | Toggle game thread stats |
| `SetHealth <value>` | Set player health |
| `AddItems <name> <count>` | Add items to inventory |

## PIE States

| State | Meaning |
|-------|---------|
| Not running | Editor is idle, no PIE session active |
| Running | PIE session is active, game is playing |
| Paused | PIE session is active but paused (via editor or `Pause` command) |

## Prerequisites

- Unreal Editor must be running
- Python Remote Execution must be enabled (`bRemoteExecution=True` in `DefaultEngine.ini`)

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| Connection refused | Editor not running or Remote Execution disabled | Start editor, verify `DefaultEngine.ini` has `bRemoteExecution=True` |
| PIE not running | Tried to exec/stop without active session | Start PIE first |
| PIE already running | Tried to start when already active | Stop first, or use exec to run commands |
