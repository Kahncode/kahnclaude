---
description: Smart commit — runs pre-commit checks, fixes issues, then commits with a conventional message
scope: project
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git branch:*), Bash(git log:*), Bash(pre-commit run:*)
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

1. Verify `.env` is in `.gitignore`
2. Verify no sensitive files are staged (`.env`, `secrets.json`, private keys) — **abort and warn if found**
3. If on `main` or `master`: warn the user and suggest creating a feature branch first

## Step 2 — Pre-Commit Checks (REQUIRED)

Run pre-commit hooks **before** committing:

Invoke `/pre-commit-check` logic to diagnose and fix pre-commit check failure, then re-run hooks until they all pass.

When pre-commit fixes modify files, **stage them before proceeding** (so they're included in the commit). If the user should review them separately, ask first.

## Step 3 — Commit

### Rules

1. Use **conventional commit** format: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore, perf
   - Scope: optional, identifies the area changed
2. Description: concise, max 72 characters, imperative mood
3. If changes span multiple unrelated concerns: suggest splitting into multiple commits
4. NEVER commit `.env` or secret files — abort and warn if found staged

### If message provided

Use `$ARGUMENTS` as the commit message (still apply conventional format if it fits).

### If no message provided

Generate an appropriate message based on **only the staged changes** (use `git diff --cached` to analyze what will be committed). Do not include information about unstaged changes or files modified by pre-commit fixes that weren't staged.

### GitHub MCP (if available)

If the GitHub MCP server is connected:

- After a successful commit, offer: "Create a PR for this branch?"
- If yes: use the MCP to create the PR with a generated title and description
- If the branch has no upstream yet, push it first
