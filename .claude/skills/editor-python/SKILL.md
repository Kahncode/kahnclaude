---
name: editor-python
description: "Unreal Editor Python executor. ALWAYS invoke when the user asks to run Python in the editor, execute a script in UE, or automate editor tasks via Python. Do not call editor-py.py directly — this skill handles inline code and file dispatch."
allowed-tools: Bash(py *)
---

# Editor Python

Execute Python in the running Unreal Editor using the Remote Execution API (`PythonScriptPlugin`). The code runs inside the UE process with full access to the `unreal` module.

## Reference

See @docs/standards/unreal/editor-python.md for prerequisites, script interface, and examples.

## Required Variables

| Variable | Purpose |
|----------|---------|
| `PROJECT_ROOT` | Workspace root (parent of `.claude/`) |

`editor-py.py` reads `UE_ENGINE` from the process env, set (with `PROJECT_ROOT`) in `.claude/settings.local.json` `env`; never set it inline. Unset → "UE_ENGINE environment variable not set" / "No module named remote_execution": start a new session or check that file.

## Flow

### 1. Detect Argument Type

| Input | Detection | Action |
|-------|-----------|--------|
| Empty | No argument | Ask the user what Python code or script to run |
| Ends in `.py` and contains `/`, `\`, or drive letter | File path | Pass as `--file` |
| Anything else | Inline code | Pass as `--code` |

### 2. Execute

**Inline code:**
```
py "$KC_PROJECT_ROOT/.claude/scripts/editor/editor-py.py" --code "<code>"
```

**File:**
```
py "$KC_PROJECT_ROOT/.claude/scripts/editor/editor-py.py" --file "<path>"
```

### 3. Report

- On success: show the output
- On error: show the error clearly with the traceback
