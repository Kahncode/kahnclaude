---
description: Smart commit — generates a conventional commit message from staged changes
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

## Pre-Commit Checks

Before committing:
1. Verify `.env` is in `.gitignore`
2. Verify no sensitive files are staged (`.env`, `secrets.json`, private keys)
3. If on `main` or `master`: warn the user — suggest creating a feature branch first

## Task

Review the staged changes and create a commit.

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

Generate an appropriate message based on the diff content.

### GitHub MCP (if available)

If the GitHub MCP server is connected:
- After a successful commit, offer: "Create a PR for this branch?"
- If yes: use the MCP to create the PR with a generated title and description
- If the branch has no upstream yet, push it first
