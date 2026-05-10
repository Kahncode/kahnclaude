---
name: game-log
description: "UE5 log analyst. ALWAYS invoke when the user asks about game logs, errors, warnings, crashes, or wants to tail a PIE session. Do not read log files directly — this skill auto-detects location, parses by category, and cross-references source code."
allowed-tools: Read, Grep, Glob, Bash
---

# Read + Diagnose Game Logs

Use PROACTIVELY when the user says: `analyze game log`, `parse log file`, `read log`, `game log`.

## Reference

See @docs/standards/unreal/game-log.md for UE log format, log categories, verbosity levels, and common error patterns.

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `KC_UE_PROJECT` | Full path to `.uproject` (derive project name) |
| `KC_PROJECT_ROOT` | Workspace root |

## Flow

### 1. Detect Log Source

Auto-detect the appropriate log file based on context:

| Context | Log Path |
|---------|----------|
| Default | `$KC_PROJECT_ROOT/Saved/Logs/<ProjectName>.log` |
| User mentions "crash" | `$KC_PROJECT_ROOT/Saved/Crashes/*/CrashContext.runtime-xml` + `*.log` |
| User mentions "test" | `$KC_PROJECT_ROOT/Saved/Logs/*Test*.log` |
| User provides a path | Use that path directly |
| User mentions "PIE" or "live" | Tail the active log during a PIE session |

### 2. Parse Log Entries

Read the log file and categorize entries:

- **Fatal**: Lines containing `Fatal` -- immediate attention
- **Error**: Lines containing `Error` -- likely bugs
- **Warning**: Lines containing `Warning` -- potential issues
- **Key Events**: Lines with `Display` level -- important game state changes

Filter out noise: skip `LogInit`, `LogConfig`, `LogPakFile` unless user asks.

### 3. Cross-Reference Source Code

For each error or warning:
1. Extract the log category (e.g., `LogCombat`, `LogNet`)
2. Grep the source for `DEFINE_LOG_CATEGORY` or `DECLARE_LOG_CATEGORY_EXTERN` matching that category
3. Grep for the log message text to find the exact callsite
4. Report: file path, line number, and surrounding context

### 4. Live PIE Session Tailing

If the user wants to monitor a live session:
1. Identify the latest log file being written to
2. Tail the file, filtering for errors and warnings
3. Report new issues as they appear

### 5. Summarize Findings

Present a structured summary:
- Total errors/warnings count
- Errors grouped by category with source file references
- Source file and line number for each callsite found in Step 3

Offer: "Want me to investigate specific errors in detail?" If yes, delegate to the `code-dev` agent via the Agent tool, passing the error details, source file references, and surrounding code context for diagnosis.

## Rules

- Always try the default log path first before asking the user
- Skip engine initialization noise unless specifically requested
- Cross-reference EVERY error against source code when possible
- For crash logs, also check `CrashContext.runtime-xml` for callstack
- Derive project name from `$KC_UE_PROJECT` filename (without extension)
