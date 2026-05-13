---
name: editor-lifecycle
description: "Unreal Editor process manager. ALWAYS invoke when the user asks to close, kill, stop, restart, launch, debug, or start the editor. Do not run taskkill, process commands, or VS scripts directly — this skill handles graceful close, force kill, and launching with debugger attached."
allowed-tools: Bash(powershell *), AskUserQuestion
---

# Editor Lifecycle

Manage the Unreal Editor process — close, kill, or launch with VS debugger attached.

## References

- @docs/standards/unreal/editor-lifecycle.md — close/kill script details and behavior
- @docs/standards/vs/launch-debug.md — COM automation details, build configurations, troubleshooting

## Tech-Stack Context

Load these if they exist in the project:
- `@docs/tech-stacks/unreal.md` — UE5 project auto-detection, engine paths, env vars
- `@docs/tech-stacks/visual_studio.md` — VS COM automation, env vars, solution path

## Required Environment Variables

| Variable | Required For | Purpose |
|----------|-------------|---------|
| `KC_PROJECT_ROOT` | All operations | Workspace root (parent of `.claude/`) |
| `KC_UE_SOLUTION` | Launch/debug only | Full path to `.sln` file |
| `KC_UE_PROJECT` | Launch/debug only | Full path to `.uproject` file |

## Flow

### 1. Detect Intent

| Input | Action |
|-------|--------|
| Empty, `close`, `close-editor`, `stop` | Graceful close |
| `force`, `kill`, `kill-editor` | Force kill |
| `launch`, `debug`, `start`, `attach`, `start debugging` | Launch with debugger |

### 2. Execute

#### Graceful Close

```bash
powershell -ExecutionPolicy Bypass -File "$KC_PROJECT_ROOT/.claude/scripts/editor/close-editor.ps1"
```

Sends WM_CLOSE to the editor's main window. May prompt to save. Waits up to 30 seconds.

#### Force Kill

```bash
powershell -ExecutionPolicy Bypass -File "$KC_PROJECT_ROOT/.claude/scripts/editor/close-editor.ps1" -Force
```

Kills the editor process immediately. Unsaved changes will be lost.

#### Launch with Debugger

Parse optional arguments from `$ARGUMENTS`: **Configuration** (`DebugGame Editor` default) and **Platform** (`Win64` default).

**VS Not Running** — full orchestration (opens VS, waits for solution load, launches editor):

```bash
powershell -ExecutionPolicy Bypass -File "$KC_PROJECT_ROOT/.claude/scripts/vs/launch-editor-from-vs.ps1" -Configuration "$CONFIGURATION" -Platform "$PLATFORM"
```

**VS Already Running** — triggers F5 in the existing instance:

```bash
powershell -ExecutionPolicy Bypass -File "$KC_PROJECT_ROOT/.claude/scripts/vs/launch-vs.ps1" -Configuration "$CONFIGURATION" -Platform "$PLATFORM"
```

First launch after a clean build can take 5-15 minutes. The editor runs under the VS debugger, so breakpoints and crash dumps work. RPC_E_CALL_REJECTED retries are handled automatically by the scripts.

### 3. Report

| Condition | Message |
|-----------|---------|
| No editor running (close/kill) | "No running Unreal Editor found." |
| Graceful close success | "Editor closed." |
| Graceful close timeout | "Editor still running after 30s. Use force to kill it." |
| Force kill success | "Editor killed." |
| Launch success | Report editor running with window title |
| Launch timeout | Warn editor didn't appear within timeout |
| VS error | Show error and suggest fixes |
