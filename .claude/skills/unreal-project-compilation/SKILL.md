---
name: unreal-project-compilation
description: "UE5 build expert. ALWAYS invoke when the user asks to compile, build, or rebuild the project. Do not run UnrealBuildTool or VS build commands directly — this skill handles auto-detect, error analysis, fix loop, and shelve on success."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Build + Analyze + Fix Loop

Use PROACTIVELY when the user says: `compile project`, `build project`, `build editor`.

## Reference

Load `@docs/standards/unreal/unreal-project-compilation.md` for build targets, VS DTE commands, UBT fallback, and error patterns.

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `KC_UE_PROJECT` | Full path to `.uproject` file |
| `KC_UE_SOLUTION` | Full path to `.sln` file |
| `KC_PROJECT_ROOT` | Workspace root (parent of `.claude/`) |
| `KC_UE_ENGINE` | UE root directory |

## Flow

### 1. Detect Project

1. Read `$KC_UE_PROJECT` to get the `.uproject` path
2. Derive project name from filename (without extension)
3. Read `.uproject` for engine version and module list

### 2. Determine Target

If user specified a target, use it. Otherwise, ask which Build target.

Default configuration: `DebugGame` for Editor, `Development` for others.

### 3. Build -- UBT

Run in background (builds are long):

```bash
dotnet "$KC_UE_ENGINE/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll" \
  -Target="${PROJECT_NAME}${SUFFIX} Win64 ${CONFIG} -Project=\"$KC_UE_PROJECT\"" \
  -WaitMutex -architecture=x64
```

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
- Run builds in background -- they take a long time
- Never modify `.generated.h`, `Intermediate/`, or `Saved/`
- Regenerate project files after adding modules (`GenerateProjectFiles.bat`)
