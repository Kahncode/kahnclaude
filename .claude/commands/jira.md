---
description: Implement a Jira issue end-to-end — fetch details, transition to In Progress, create branch, plan, code, test, then commit or PR
scope: project
argument-hint: <issue-key or jira-url>
allowed-tools: getJiraIssue, getTransitionsForJiraIssue, transitionJiraIssue, addCommentToJiraIssue, editJiraIssue, Bash(git status:*), Bash(git branch:*), Bash(git checkout:*), Bash(git log:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Jira Issue Implementation

**Input:** $ARGUMENTS

## Step 0 — Extract Issue Key

Parse the issue key from `$ARGUMENTS`. The input may be:

- A bare key: `PROJ-42`
- A Jira browse URL: `https://company.atlassian.net/browse/PROJ-42`
- A Jira issue URL with title: `https://company.atlassian.net/browse/PROJ-42/some-title`

Extract the key using this rule: find the segment matching `[A-Z]+-[0-9]+` (uppercase letters, hyphen, digits). This is always the issue key.

Examples:
- `PROJ-42` → `PROJ-42`
- `https://acme.atlassian.net/browse/PROJ-42` → `PROJ-42`
- `https://acme.atlassian.net/browse/BACKEND-123` → `BACKEND-123`

Store the extracted value as `ISSUE_KEY`. Use it in all subsequent steps — never use the raw `$ARGUMENTS` after this point.

## Step 1 — Fetch Issue

Call `getJiraIssue` with the issue key `ISSUE_KEY`.

Extract and display:
- **Summary** (title), **Description**, **Status**, **Priority**, **Assignee**
- **Issue Type** (Bug, Story, Task, etc.)
- **Labels**, **Story Points / Estimate**
- **Reporter**, **Sprint** (if present)

If the issue is not found, stop and report the error.

## Step 2 — Transition to In Progress

Call `getTransitionsForJiraIssue` with `ISSUE_KEY` to list available transitions.

Find the transition whose name contains "In Progress" (case-insensitive). If none matches exactly, look for "Start", "Begin", or "Active" — pick the closest equivalent and confirm with the user if ambiguous.

If the issue is NOT already in an in-progress state:
- Call `transitionJiraIssue` with the matching transition ID
- Confirm the update

If already in progress, note it and continue.

## Step 3 — Create Branch

Construct a branch name from the issue key and summary:
1. Lowercase the summary
2. Replace spaces and special characters with hyphens
3. Truncate to keep the full segment under 50 characters
4. Format: `jira/ISSUE_KEY-slugified-summary`

Example: `PROJ-42` + "Fix login timeout" → `jira/PROJ-42-fix-login-timeout`

```bash
git status --porcelain
```

If the working tree is dirty, stop and ask the user to stash or commit first.

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
3. Verify tests pass if a test runner is available

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

Stage relevant files and commit. Include `ISSUE_KEY` in the commit message — Jira's GitHub integration auto-links commits and PRs that contain the issue key in the branch name or message:

```
feat(PROJ-42): <concise imperative description>

Implements <Jira issue summary>

PROJ-42
```

The trailing `PROJ-42` on its own line is recognized by Jira's GitHub integration and Smart Commits to link the commit to the issue.

### If "Commit + PR":

Commit as above, then:
```bash
git push -u origin <branchName>
```

Create a PR. The branch name already contains `ISSUE_KEY` (`jira/PROJ-42-...`), which Jira's GitHub integration uses to auto-link the PR. Use this PR description template:

```
## Summary
<what was implemented>

## Jira
PROJ-42

## Test plan
- [ ] <test scenario 1>
- [ ] <test scenario 2>
```

After the PR is created, add a comment on the Jira issue linking to the PR URL:
```
addCommentToJiraIssue(ISSUE_KEY, "PR opened: <PR URL>")
```

### If "Leave it":

Report the branch name and remind the user:
```
Branch: <branchName>
When ready: /commit  or  git commit -m "feat(PROJ-42): ..."
Jira link: include PROJ-42 in commit message or PR title/description
```
