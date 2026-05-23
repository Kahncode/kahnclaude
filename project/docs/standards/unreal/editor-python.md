# Editor Python Reference

## Prerequisites

The editor must be running with Python Remote Execution enabled:

```ini
; In DefaultEngine.ini
[/Script/PythonScriptPlugin.PythonScriptPluginSettings]
bRemoteExecution=True
```

## Helper Script

**Location:** `$KC_PROJECT_ROOT/.claude/scripts/editor/editor-py.py`

This Python script lives in the target project (installed via `/kc:install`), not in the KahnClaude skill directory.

### Interface

| Flag | Input | Behavior |
|------|-------|----------|
| `--code "<code>"` | Inline Python | Sends code string to the editor for execution |
| `--file "<path>"` | Script file path | Reads the file and sends its contents to the editor |

Multi-line code works fine with `--code`; pass it as a single quoted argument.

Output from `print()` calls appears in both the terminal and the UE log.

## Examples

```bash
# Get current level name
py editor-py.py --code "print(unreal.EditorLevelLibrary.get_editor_world().get_name())"

# Run a script file
py editor-py.py --file "D:/my_scripts/create_assets.py"

# Multi-line inline
py editor-py.py --code "
import unreal
actors = unreal.EditorLevelLibrary.get_all_level_actors()
print(f'Actor count: {len(actors)}')
"
```

## Relationship to Other Skills

The `unreal-asset-inspections` and `pie` skills use the same underlying Remote Execution mechanism but through their own specialized scripts. This skill provides the general-purpose entry point for arbitrary Python execution when no specialized skill applies.

## Environment Requirements

| Variable | Required | Purpose |
|----------|----------|---------|
| `KC_PROJECT_ROOT` | Yes | Locates the helper script at `.claude/scripts/editor/editor-py.py` |
| `KC_UE_ENGINE` | Yes | UE engine root (used by the helper script internally) |
