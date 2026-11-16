---
name: unreal-project-compilation
description: "UE5 build expert. ALWAYS invoke when the user asks to compile, build, or rebuild the project. Do not run UnrealBuildTool or VS build commands directly — this skill handles auto-detect, error analysis, fix loop, and shelve on success."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Build + Analyze + Fix Loop

Use PROACTIVELY when the user says: `compile project`, `build project`, `build editor`.

## Reference

Load `@docs/standards/unreal/unreal-project-compilation.md` for build targets, VS DTE commands, UBT fallback, and error patterns.

## Required Variables

| Variable | Purpose |
|----------|---------|
| `UE_PROJECT` | Full path to `.uproject` file |
| `UE_ENGINE` | UE engine root directory |

Set in the process env by `.claude/settings.local.json` `env` (values also in .claude/rules/project-vars.md). The UBT command below still takes literal paths.

## Flow

### 1. Resolve Paths

1. Read .claude/rules/project-vars.md for `UE_ENGINE` and `UE_PROJECT` values
2. Derive project name from the .uproject filename (without extension)

### 2. Determine Target

If user specified a target, use it. Otherwise default to `{{UE_DEFAULT_TARGET}}` without asking.

**Before building:** if the user said they're running tests / not to compile, or an automation run is in progress, don't build; report "build owed". If `{{EDITOR_PROCESS}}` is running with Live Coding active, UBT will refuse; for a body-only change use Live Coding instead (code-dev Step 2a), otherwise ask the user to close the editor.

Default configuration: `DebugGame` for Editor, `Development` for others.

### 3. Build -- UBT

Run in background (builds are long). Substitute the resolved paths into this command:

```
"{{UBT_DOTNET}}" "{{UBT_DLL}}" -Target="<PROJECT_NAME><SUFFIX> Win64 <CONFIG> -Project=<UE_PROJECT>" -WaitMutex -architecture=x64
```

Use literal paths in the command — do NOT use shell variable syntax like `$env:` or `$VAR`.

### 4. Analyze Output

If build fails, parse errors and categorize them using reference.md error pattern table. Present a structured error summary:
- Error count by category
- File path and line number for each error
- The raw error text

### 5. Delegate Fix to Agent

Delegate to the `code-dev` agent via the Agent tool, passing:
- The categorized error list with file paths and line numbers
- The raw build output
- Ask it to propose fixes for each error

Present the agent's proposed fixes to the user for approval.

### 6. Apply + Rebuild Loop

If user approves fixes:
1. Apply the approved fixes
2. Rebuild (go to Step 3)
3. If new errors appear, repeat from Step 5

### 7. On Success

Report: `Build succeeded: ${TARGET} Win64 ${CONFIG}`

## Rules
- Run builds in background (`run_in_background`) and wait for the completion notice or Monitor the log -- never a foreground `while`/`sleep` poll loop
- Never `p4 edit`/`p4 add` rebuilt binaries; if one was opened by mistake, `p4 revert -k <file>`
- Never modify `.generated.h`, `Intermediate/`, or `Saved/`
- Regenerate project files after adding modules (`GenerateProjectFiles.bat`)
