---
name: game-log
description: "UE5 log analyst. ALWAYS invoke for game logs, errors, warnings, crashes or tailing a PIE session, and when the user hands over a log or report (a .log file, a QA or Horde step log, Saved/Automation/Reports/*/index.json, 'what failed in this log'). Finds the log, parses by category, cross-references source. A Horde job or Slack failure paste goes to horde-artifact first."
allowed-tools: Read, Grep, Glob, Bash
---

# Read + Diagnose Game Logs

Use PROACTIVELY when the user says: `analyze game log`, `parse log file`, `read log`, `game log`.

## Reference

See @docs/standards/unreal/game-log.md for UE log format, log categories, verbosity levels, and common error patterns.

## Required Variables

| Variable | Purpose |
|----------|---------|
| `UE_PROJECT` | Full path to `.uproject` (derive project name) |
| `PROJECT_ROOT` | Workspace root |

Set in the process env by `.claude/settings.local.json` `env` (values also listed in .claude/rules/project-vars.md).

## Flow

### 1. Detect Log Source

Auto-detect the appropriate log file based on context:

| Context | Log Path |
|---------|----------|
| Default | `{{UE_PROJECT_DIR}}/Saved/Logs/<ProjectName>.log` |
| User mentions "crash" | `{{UE_PROJECT_DIR}}/Saved/Crashes/*/CrashContext.runtime-xml` + `*.log` |
| User mentions "test" | `{{UE_PROJECT_DIR}}/Saved/Automation/Reports/<newest>/index.json`, then `{{UE_PROJECT_DIR}}/Saved/Logs/*Test*.log` |
| User hands over a log/artifact path (`{{DOWNLOADS}}\*.log`, `step-saved_*`, a Horde zip) | that path; for a Horde artifact use `horde-artifact` first and read its `DIGEST.md` |
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
- Derive project name from `UE_PROJECT` filename (without extension)
