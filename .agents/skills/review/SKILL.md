---
name: review
description: Review code changes for bugs, security issues, and best practices. Use for code audits, security checks, or quality reviews.
scope: project
allowed-tools: Read, Grep, Glob, Bash
---

# Code Review

Warn if on `main` or `master`, then delegate to the `code-reviewer` agent.

Pass the user's argument (if any) to the agent as context:
- Current branch: !`git branch --show-current`
- User argument: (if provided, e.g., `HEAD~3..HEAD` or `bd-73`)

The agent determines what to review based on priority (staged → unstaged → argument → branch vs main).
