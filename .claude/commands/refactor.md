---
description: Refactor a file against this project's CLAUDE.md rules — split, extract, clean up
scope: project
argument-hint: <file-path> [--dry-run]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Refactor — Project Rules Enforcement

Refactor the target file following every rule in this project's `CLAUDE.md`.

**Target:** $ARGUMENTS

If `--dry-run` is passed, report what WOULD change without modifying any files.

## Step 0 — Read Before Touching

**Never refactor blind.** Read these files first:

1. The target file (every line)
2. `CLAUDE.md` — current project rules
3. `@docs/ARCHITECTURE.md` — where things belong (if it exists)

Also check what imports the target file:

```bash
grep -r "<filename>" --include="*" -l .
```

Report: "This file is imported by X other files. Changes here affect: [list]"

## Step 1 — Audit the File

Check every item. Note line number, what's wrong, and the fix.

### 1A. File Size

- **> 300 lines → MUST split.** Identify logical sections: types, constants, helpers, main logic, exports.

### 1B. Function Size

- **> 50 lines → MUST extract.** Each extracted function named by what it DOES.

### 1C. Error Handling

- No swallowed errors (`catch { return null }` or empty `except`)
- Errors logged with context (what was attempted, relevant IDs)
- User-facing errors have clear messages

### 1D. Import Hygiene

- No wildcard imports (`import *`)
- No circular imports
- Remove unused imports
- Sort: stdlib → external → internal

### 1E. Security

- No hardcoded secrets, API keys, tokens, or connection strings
- Input validation on external data
- No injection vulnerabilities (SQL, shell, etc.)

### 1F. Independent Async Operations

- Multiple independent awaits / async calls that don't depend on each other → parallelize

### 1G. Dead Code

- Remove unused functions, variables, and unreachable code
- Remove commented-out code blocks (that's what git history is for)

### 1H. Project-Specific Rules

Check `CLAUDE.md` for any additional project rules and apply them.

## Step 2 — Plan the Refactor

Before changing anything, present a plan to the user:

```
Refactor Plan for: src/handlers/users.py (347 lines)
====================================================

File size: 347 lines → SPLIT REQUIRED (max 300)

Split into:
  1. src/handlers/users.py          — main handler (~120 lines)
  2. src/handlers/user_validation.py — validation helpers (~80 lines)
  3. src/models/user.py              — User type definitions (~40 lines)

Function extraction:
  - process_user_signup() (73 lines) → validate_input() + create_record() + send_welcome()

Other fixes:
  - Line 67: swallowed exception → proper logging + re-raise
  - Lines 23-25: sequential independent calls → parallelize
  - Lines 200-215: dead code (commented-out old auth) → remove

Blast radius: imported by 3 files (server.py, routes.py, admin.py)
  - Imports will be updated in all affected files

Proceed? (yes / no / modify plan)
```

**Wait for user approval before making any changes.**

## Step 3 — Execute the Refactor

After approval, apply changes in this order:

1. Create new files (types, helpers, utilities)
2. Move code from original to new files
3. Update imports in the original file
4. Update imports in all files that imported from the original
5. Apply remaining fixes (error handling, dead code, parallelization)
6. Verify the project still compiles / passes linting if applicable

## Step 4 — Report

```
Refactor Complete: src/handlers/users.py
=========================================
Before: 1 file, 347 lines, 4 violations
After:  3 files, ~240 lines total, 0 violations

Files created:
  + src/handlers/user_validation.py (80 lines)
  + src/models/user.py (40 lines)

Files modified:
  ~ src/handlers/users.py (120 lines, down from 347)
  ~ src/server.py (imports updated)

Fixes applied:
  - 2 functions extracted (were >50 lines)
  - 1 swallowed exception fixed
  - 15 lines of dead code removed
```
