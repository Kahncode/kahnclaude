---
description: Review code changes for bugs, security issues, and best practices
scope: project
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git branch:*)
---

# Code Review

Delegate this task to the `code-reviewer` agent via the Agent tool.

Pass the following as context:
- Current branch: !`git branch --show-current`
- Unstaged changes: !`git diff HEAD`
- Staged changes: !`git diff --cached`

Warn in the output header if the current branch is `main` or `master`.
