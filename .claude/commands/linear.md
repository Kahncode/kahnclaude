---
description: Implement a Linear issue end-to-end — fetch details, set In Progress, create branch, plan, code, test, then commit or PR
scope: project
argument-hint: <issue-id or linear-url>
allowed-tools: mcp__claude_ai_Linear__get_issue, mcp__claude_ai_Linear__save_issue, mcp__claude_ai_Linear__create_comment, Bash(git status:*), Bash(git branch:*), Bash(git checkout:*), Bash(git log:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Linear Issue Implementation

**Input:** $ARGUMENTS

## Step 0 — Extract Issue ID

Parse the issue ID from `$ARGUMENTS`. The input may be:

- A bare ID: `ENG-42`
- A Linear URL: `https://linear.app/team/issue/ENG-42/some-title-slug`

Extract the ID using this rule: find the segment matching `[A-Z]+-[0-9]+` (uppercase letters, hyphen, digits). This is always the issue ID.

Examples:
- `ENG-42` → `ENG-42`
- `https://linear.app/acme/issue/ENG-42/fix-login` → `ENG-42`
- `https://linear.app/acme/issue/BACKEND-123/add-endpoint` → `BACKEND-123`

Store the extracted value as `ISSUE_ID`. Use it in all subsequent steps — never use the raw `$ARGUMENTS` after this point.

## Step 1 — Fetch Issue

Call `mcp__claude_ai_Linear__get_issue` with id=`ISSUE_ID`.

Extract and display:
- **Title**, **Description**, **State**, **Priority**, **Assignee**
- **branchName** (Linear's suggested git branch name — use this verbatim for the branch)
- **Labels**, **Estimate**

If the issue is not found, stop and report the error.

## Step 2 — Set In Progress

If the issue state is NOT already "In Progress" (or equivalent started state):
- Call `mcp__claude_ai_Linear__save_issue` with `id=ISSUE_ID` and `state="In Progress"`
- Confirm the update

If already in progress, note it and continue.

## Step 3 — Create Branch

Use the `branchName` returned by Linear in Step 1. If the API did not return one, construct it as `linear-task/ISSUE_ID` (e.g., `linear-task/ENG-42`).

```bash
git status --porcelain
```

If the working tree is dirty, stop and ask the user to stash or commit first before continuing.

```bash
git checkout -b <branchName>
```

If the branch already exists locally, check it out:
```bash
git checkout <branchName>
```

Report the active branch after checkout.

## Step 4 — Plan

Enter plan mode now. Do not write any code until the plan is approved.

Thoroughly explore the codebase to understand:
- What files are relevant to this issue
- What the implementation approach should be
- What tests will be needed

Present a step-by-step plan that covers:
1. Files to create or modify
2. Implementation steps in order
3. Test files and scenarios to cover
4. Any risks or decisions the user should make

**Wait for user approval before proceeding.**

## Step 5 — Implement

Execute the approved plan:

1. Make all code changes
2. Write tests for new/changed behavior
3. Verify tests pass if a test runner is available:
   ```bash
   # Run appropriate test command for the project
   ```

Keep commits off until Step 6 — implement fully first.

## Step 6 — Review

Run a self-review before finishing:
- No hardcoded secrets or credentials
- No debug/temporary code left behind
- Tests cover the main behavior and edge cases
- Changes match the issue scope — no scope creep

Show a summary:
```
Files changed: N
Tests added: N
```

## Step 7 — Learn

Before committing, capture knowledge from the implementation using `/learn`. This auto-detects changes and updates project documentation (ARCHITECTURE.md, subsystems, etc.) for future reference.

Invoke `/learn` with no arguments — it will inspect staged changes and auto-detect learnings.

## Step 8 — Finish

Ask the user what to do next:

> Implementation complete. What would you like to do?
> 1. **Leave it** — I'll commit manually later
> 2. **Commit** — Stage and commit with a conventional message
> 3. **Commit + PR** — Commit, push branch, and open a pull request

### If "Commit":

Stage relevant files and commit using conventional format:
```
feat(ENG-42): <concise imperative description>

Implements <Linear issue title>
Fixes ENG-42
```

The `Fixes ENG-42` footer links the commit to Linear and triggers the GitHub integration.

### If "Commit + PR":

Commit as above, then:
```bash
git push -u origin <branchName>
```

Then create a PR with title and description that references the Linear issue ID so Linear auto-links it.

PR description template:
```
## Summary
<what was implemented>

## Linear
Fixes ISSUE_ID

## Test plan
- [ ] <test scenario 1>
- [ ] <test scenario 2>
```

Add a comment on the Linear issue linking to the PR URL using `mcp__claude_ai_Linear__create_comment`.

### If "Leave it":

Report the branch name and remind the user:
```
Branch: <branchName>
When ready: /commit  or  git commit -m "feat(ID): ..."
PR link trigger: include "Fixes ENG-42" in commit or PR description
```
