---
name: task-implementation
description: "Implementation orchestrator. ALWAYS invoke when the user asks to implement, build, or code a feature. Do not invoke code-dev directly — this skill routes to the correct agents and drives the full implement-verify-review cycle."
disable-model-invocation: true
allowed-tools: Agent, Read, Grep, Glob, Skill, ToolSearch, AskUserQuestion, mcp__atlassian__*
---

# Implementation Workflow

Use PROACTIVELY when the user says: `implement this`, `implement feature`, `build this`, `code this up`, `implement task`.

**Input:** $ARGUMENTS

## 0. Ticket Setup (Optional)

If the input contains a Jira ticket reference (e.g., `PROJ-123`):

### 0a. Get Ticket Content
1. Use `mcp__atlassian__getJiraIssue` with:
   - `fields: ["summary", "status", "description", "assignee"]`
2. Extract the implementation plan from description

### 0b. Mark In Progress
1. Use `mcp__atlassian__transitionJiraIssue` to move the ticket to In Progress
2. If transition fails, warn the user but continue

Skip if: no ticket reference, or user says "don't update Jira".

## 1. Implement

1. Delegate to `code-dev` agent — pass the full input (ticket content, user prompt, and any context)
2. Proceed to Stage 2

## 2. Review

Invoke `/code-review` skill — pass the changelist/commit reference.

**Severity meanings:**
- CRITICAL/WARNING: Must fix before merge
- MINOR: Style/naming issues — should fix, not blockers
- SUGGESTION: Improvement ideas — optional
- INFO: Pre-existing issues — context only, ignore

If CRITICAL or WARNING findings exist, proceed to Stage 3. If only MINOR, ask user if they want to fix or proceed. Else skip to Stage 4.

## 3. Fix Review Findings

1. Report the findings to the user with severity counts (CRITICAL, WARNING, MINOR, INFO)
2. Delegate CRITICAL and WARNING findings for fixing to `code-dev` agent
3. For MINOR findings: ask user if they want to fix these too, or proceed without
4. Re-run review once (/code-review)

**After re-review, check remaining findings:**
- **No CRITICAL or WARNING remaining:** Proceed to Stage 4 (MINOR and INFO are acceptable)
- **CRITICAL or WARNING still present:** Ask the user:
  > "Review found [N CRITICAL, M WARNING] remaining after fixes. Options:
  > 1. Apply another round of fixes (specify which)
  > 2. Proceed with these findings
  > 3. Abandon the changelist"
  
  Then:
  - Option 1: Return to step 2 of this stage
  - Option 2: Proceed to Stage 4
  - Option 3: Report abandonment and exit workflow

## 4. Done

Report:
```
Implementation: Complete
Files changed: N (list)
Changelist/Commit: <identifier>
Build: Passed
Review: <X critical, Y warnings, Z minor, A suggestions, W info>
```

## Rules

- Never skip build/test validation
- Single fix-review pass; user decides if more iterations needed
- Present review findings before applying fixes
