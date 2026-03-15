---
description: Smart commit — stages nothing extra, commits with a conventional message, stops if pre-commit hooks fail
scope: project
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git branch:*), Bash(git log:*)
argument-hint: [optional commit message override]
---

# Smart Commit

## Context

- Current status: !`git status --short`
- Staged diff summary: !`git diff --cached --stat`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`

## Step 0 — Staged Files Check

Run `git diff --cached --name-only` to check what is staged.

- **If nothing is staged:** Tell the user: "Nothing is staged. Stage the files you want to commit with `git add <files>` and re-run `/commit`." Then **stop immediately** — do not proceed.
- **If files are staged:** Proceed with exactly those staged files. Do not stage any additional files.

## Step 1 — Safety Checks

Before anything else:

1. If `.gitignore` is modified in this commit, verify `.env` or other secret files are is in `.gitignore`
2. Verify no sensitive files are staged (`.env`, `secrets.json`, private keys) — **abort and warn if found**
3. If on `main` or `master`: warn the user and suggest creating a feature branch first

## Step 2 — Commit

### Message rules

1. Use **conventional commit** format: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore, perf
   - Scope: optional, identifies the area changed
2. Description: concise, max 72 characters, imperative mood
3. If changes span multiple unrelated concerns: suggest splitting into multiple commits
4. NEVER commit `.env` or secret files — abort and warn if found staged

### If message provided

Use `$ARGUMENTS` as the commit message (still apply conventional format if it fits).

### If no message provided

Generate an appropriate message based on **only the staged changes** (use `git diff --cached` to analyze what will be committed).

### Pre-commit hook failures

If the commit attempt triggers pre-commit hooks that fail:

1. Diagnose each failure and fix the affected files
2. **Do NOT stage any files modified as a result of fixing pre-commit errors**
3. **Stop here** — report to the user: which hooks failed, what was fixed, and which files were changed
4. Ask the user to review the fixes and stage them manually before re-running `/commit`

### GitHub MCP (if available)

If the GitHub MCP server is connected:

- After a successful commit, offer: "Create a PR for this branch?"
- If yes: use the MCP to create the PR with a generated title and description
- If the branch has no upstream yet, push it first
