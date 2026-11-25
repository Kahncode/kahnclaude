---
name: commit
description: Smart commit — stages nothing extra, commits with a conventional message, re-stages auto-fixes from pre-commit hooks once, stops on real hook failures
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
- **If files are staged:** Commit ONLY those files. **Never run `git add` on any file that was not already staged before `/commit` was invoked** — even if other dirty or untracked files appear in context. Unstaged files are the user's responsibility to stage explicitly.

## Step 1 — Safety Checks

Before anything else:

1. If `.gitignore` is staged, verify `.env` or other secret files are is in `.gitignore`
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

Before the first commit attempt, record the staged files (`git diff --cached --name-only`) and the files with unstaged changes (`git diff --name-only`).

If the commit fails because of git hooks:

1. **Auto-fixes only** (formatters or fixers rewrote files and nothing else failed): re-stage the rewritten files that were in the recorded staged set **and** had no unstaged changes before the attempt (re-adding a partially staged file would pull in hunks the user did not stage). Retry the commit **once**. This is the only case where `/commit` runs `git add`.
2. **Anything else** (lint or type errors, secret scan findings, a rewritten file that was partially staged, or the retry failed again):
   - Diagnose each failure and fix the affected files, except secret findings: never edit around those, report them
   - **Do NOT stage the fixes**
   - **Stop** and report which hooks failed, what was fixed and which files changed; ask the user to review, stage and re-run `/commit`

Never bypass hooks with `--no-verify`.

### GitHub MCP (if available)

If the GitHub MCP server is connected:

- After a successful commit, offer: "Create a PR for this branch?"
- If yes: use the MCP to create the PR with a generated title and description
- If the branch has no upstream yet, push it first
