---
description: Create a git worktree + branch for isolated task work
scope: project
argument-hint: <branch-name> [base-branch]
allowed-tools: Bash, Read, AskUserQuestion
---

# Git Worktree — Isolated Task Branch

Create a new git worktree so this task runs on its own branch in its own directory. The main branch stays untouched. If anything goes wrong, delete the branch — zero risk.

**Arguments:** $ARGUMENTS

## Step 0 — Parse Arguments

- **First argument:** branch name (required). If not provided, ask the user.
- **Second argument:** base branch to branch from (optional, defaults to `main` or `master`)

Branch naming convention: `task/<descriptive-name>`
- If the user provides just a name like `auth-fix`, prefix it: `task/auth-fix`
- If they already include a prefix like `feat/login`, use as-is

## Step 1 — Verify Git State

```bash
git rev-parse --git-dir
git status --porcelain
```

**If there are uncommitted changes:** warn the user and ask whether to:
- Stash changes first (`git stash`)
- Commit changes first
- Abort

**Never create a worktree with dirty state** — changes could bleed between worktrees.

## Step 2 — Determine Base Branch

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

If no remote, check whether `main` or `master` exists locally. Use the second argument if provided, otherwise use the detected default branch.

## Step 3 — Create Branch + Worktree

The worktree directory goes next to the current repo as `../<repo-name>--<branch-name>`:

```bash
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
BRANCH_NAME="<branch>"
WORKTREE_DIR="../${REPO_NAME}--${BRANCH_NAME//\//-}"

git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" "$BASE_BRANCH"
```

## Step 4 — Verify

```bash
git worktree list
```

## Step 5 — Report

```
Git Worktree Created
====================
Branch:    task/auth-fix
Base:      main
Directory: ../my-app--task-auth-fix
Main repo: ../my-app (untouched)

Next steps:
  cd ../my-app--task-auth-fix
  claude                          # start a new Claude session here

When done:
  cd ../my-app
  git merge task/auth-fix         # or open a PR
  git worktree remove ../my-app--task-auth-fix
  git branch -d task/auth-fix

If something went wrong:
  git worktree remove ../my-app--task-auth-fix --force
  git branch -D task/auth-fix     # main was never touched
```

## When the Task Is Done

When the user says they're done with work on a worktree branch:

1. Show `git diff main...HEAD` summary (files changed, insertions, deletions)
2. Ask: "Ready to merge into main, or do you want to open a PR?"

## Quick Reference

```bash
git worktree list                             # see all active worktrees
git worktree remove ../my-app--branch-name   # clean up finished task
git worktree prune                            # remove stale entries
```
