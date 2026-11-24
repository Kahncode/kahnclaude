---
name: github-issue
description: Implement a GitHub issue end-to-end — fetch details, assign and label In Progress, create branch, plan, code, test, then commit or PR. Uses the gh CLI.
scope: project
argument-hint: <issue-number or github-issue-url>
allowed-tools: Bash(gh issue:*), Bash(gh pr:*), Bash(gh repo view:*), Bash(gh auth status:*), Bash(git status:*), Bash(git branch:*), Bash(git checkout:*), Bash(git log:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# GitHub Issue Implementation

**Input:** the user's argument (issue number or URL)

Requires the `gh` CLI, authenticated (`gh auth status`). If missing or unauthenticated, stop and tell the user.

## Step 0 — Extract Issue Number

The input may be:

- A bare number: `42` or `#42`
- A URL: `https://github.com/owner/repo/issues/42`

Rules:

- URL: take the digits after `/issues/`, and the `owner/repo` before it. Store as `REPO`.
- Bare number: `REPO` is the current repo (`gh repo view --json nameWithOwner -q .nameWithOwner`).
- If the URL's repo differs from the current repo, stop and ask the user to run from the correct checkout.

Store the number as `ISSUE_NUMBER`. Use it in all subsequent steps — never use the raw argument after this point.

## Step 1 — Fetch Issue

```bash
gh issue view ISSUE_NUMBER --repo REPO --json number,title,body,state,labels,assignees,milestone,url,comments
```

Display: **Title**, **Body**, **State**, **Labels**, **Assignees**, **Milestone**. Read the comments for added context or decisions.

If the issue is not found, stop and report the error. If it is closed, ask the user whether to continue.

## Step 2 — Mark In Progress

GitHub issues have no built-in "In Progress" state. Do the following, skipping anything already true:

1. Assign to the current user: `gh issue edit ISSUE_NUMBER --add-assignee @me`
2. If the repo has an `in progress` label (`gh label list --search "in progress"`), add it: `gh issue edit ISSUE_NUMBER --add-label "in progress"`. Do not create labels.

If the issue uses a GitHub Project status field and the user asks for it to be updated, use `gh project item-edit`; otherwise skip it.

## Step 3 — Create Branch

Construct the branch name from issue type and title: `<type>/ISSUE_NUMBER-<slug>` where `type` is `fix` for a `bug` label and `feat` otherwise, and `slug` is the lowercase hyphenated title, max 40 chars.

```bash
git status --porcelain
```

If the working tree is dirty, stop and ask the user to stash or commit first.

```bash
git checkout -b <branchName>
```

If the branch already exists locally, check it out instead. Report the active branch.

## Step 4 — Plan

Enter plan mode now. Do not write any code until the plan is approved.

Explore the codebase to understand relevant files, the implementation approach, and the tests needed.

Present a step-by-step plan covering:
1. Files to create or modify
2. Implementation steps in order
3. Test files and scenarios
4. Risks or decisions for the user

**Wait for user approval before proceeding.**

## Step 5 — Implement

1. Make all code changes
2. Write tests for new or changed behavior
3. Run the project's test command if one is available

Keep commits off until Step 8 — implement fully first.

## Step 6 — Review

Self-review before finishing:
- No hardcoded secrets or credentials
- No debug or temporary code left behind
- Tests cover the main behavior and edge cases
- Changes match the issue scope — no scope creep

Show a summary:
```
Files changed: N
Tests added: N
```

## Step 7 — Learn

Invoke `/learn` with no arguments to capture knowledge from the implementation into project documentation before committing.

## Step 8 — Finish

Ask the user:

> Implementation complete. What would you like to do?
> 1. **Leave it** — I'll commit manually later
> 2. **Commit** — Stage and commit with a conventional message
> 3. **Commit + PR** — Commit, push branch, and open a pull request

### If "Commit":

Stage relevant files and commit:
```
feat: <concise imperative description> (#ISSUE_NUMBER)

Implements <issue title>
Closes #ISSUE_NUMBER
```

Use `fix:` for bugs. The `Closes #N` footer links the commit to the issue and closes it when merged into the default branch.

### If "Commit + PR":

Commit as above, then:
```bash
git push -u origin <branchName>
```

Create the PR with `gh pr create --title "<title>" --body "<body>"`. Body template:
```
## Summary
<what was implemented>

## Issue
Closes #ISSUE_NUMBER

## Test plan
- [ ] <test scenario 1>
- [ ] <test scenario 2>
```

GitHub links the PR to the issue automatically through `Closes #N`; no extra comment is needed.

### If "Leave it":

Report the branch name and remind the user:
```
Branch: <branchName>
When ready: /commit  or  git commit -m "feat: ... (#N)"
Issue link: include "Closes #N" in the commit or PR description
```
