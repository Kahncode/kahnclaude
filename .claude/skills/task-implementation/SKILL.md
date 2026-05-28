---
name: task-implementation
description: "Unified implementation orchestrator. ALWAYS invoke when the user asks to implement, build, or modify C++ code, Blueprint assets, or both. Do not invoke sub-agents directly — this skill routes to the correct agents and drives the full implement-verify-review-shelve cycle."
disable-model-invocation: true
allowed-tools: Agent, Read, Grep, Glob, Skill, ToolSearch, AskUserQuestion, mcp__atlassian__*
---

# Unified Implementation Workflow

Use PROACTIVELY when the user says: `implement this`, `implement feature`, `build this`, `code this up`, `modify blueprint`, `implement task`.

**Input:** $ARGUMENTS

## 0. Ticket Setup

If the input contains a Jira ticket reference (e.g., `CLTR-123`):

### 0a. Fetch Ticket Context
1. Use `mcp__atlassian__getJiraIssue`
2. Extract from the response:
   - **Summary** — `fields.summary`
   - **Description** — `fields.description`
   - **Comments** — `renderedFields.comment.comments[]` (this is an ARRAY — iterate through each comment)
3. **Tech Plan Detection:** For EACH comment in the `comments[]` array, check if `body` (rendered HTML) or the ADF structure contains:
   - "Implementation Plan", "Tech Plan", "Technical Plan"
   - Structured sections: "## Approach", "## Files to Modify", "## Design"
   - A table with "File" and "Change" columns
   - Code blocks with implementation details
4. If a tech plan comment is found:
   - Set `TICKET_TECH_PLAN` = the comment body (use rendered HTML version for readability)
   - Set `PLAN_APPROVED = true` — ticket tech plans are pre-approved, skip planning stage
5. If no tech plan found, `TICKET_TECH_PLAN` = empty, `PLAN_APPROVED = false`

### 0b. Mark In Progress
1. Use `mcp__atlassian__getTransitionsForJiraIssue` to get available transitions
2. Find the "In Progress" transition (or similar: "Start Progress", "Begin Work")
3. Use `mcp__atlassian__transitionJiraIssue` to move the ticket to In Progress
4. If transition fails, warn the user but continue

Skip if: no ticket reference, or user says "don't update Jira".

## 0.5. Detect Pre-Approved Plan

A pre-approved plan can come from TWO sources:

**Source 1: Ticket comments (from Stage 0a)**
- If `TICKET_TECH_PLAN` is set and `PLAN_APPROVED = true` was set in Stage 0a, you already have a pre-approved plan
- Use `TICKET_TECH_PLAN` as the implementation plan

**Source 2: Input from `/task-planning`**
- Check if the input contains structured output with:
  - `**Plan:**` section with a `| File | Change |` table
  - `**Acceptance Criteria:**` section
- If found: Set `PLAN_APPROVED = true`, extract the Plan table for sub-agents

**Result:**
- If `PLAN_APPROVED = true` (from either source): Skip Stage 1, proceed directly to Stage 2
- If `PLAN_APPROVED = false`: Proceed to Stage 1

## 1. Requirements Clarification

Before implementation, ask clarifying questions to reach shared understanding.

**Skip this step if:**
- `PLAN_APPROVED = true` (pre-approved plan from ticket comments or /task-planning)
- User says "just do it", "skip questions", "no questions".

## 2. Classify Work Type

From the input, determine:
- **cpp** — C++ files only -> code-dev + code-reviewer
- **blueprint** — Blueprint assets only -> blueprint-dev + blueprint-reviewer
- **both** — C++ and Blueprint -> all four agents, C++ first

If unclear, ask: "Does this involve C++ code, Blueprint assets, or both?"

## 3. C++ Track (if cpp or both)

**If `PLAN_APPROVED = true`:**
1. Use the approved plan (either `TICKET_TECH_PLAN` from ticket comments or the plan from /task-planning input)
2. Report to user: "Using pre-approved tech plan from [ticket comments / input]. Delegating to code-dev."
3. Delegate to `code-dev` agent with the approved plan

**If `PLAN_APPROVED = false`:**
1. Spawn `code-planner` agent — pass the full requirement
2. Receive plan from code-planner
3. Present the plan to the user in the main context
4. Ask user via AskUserQuestion:
   - Question: "Approve this implementation plan?"
   - Options: "Approve", "Needs changes"
5. If "Needs changes": re-spawn `code-planner` with user feedback, repeat from step 2
6. If "Approve": delegate to `code-dev` agent with the approved plan

Proceed to Stage 4 if both, else proceed to Stage 5.

## 4. Blueprint Track (if blueprint or both)

**If `PLAN_APPROVED = true`:**
1. Use the approved plan (either `TICKET_TECH_PLAN` or the plan from input)
2. Report to user: "Using pre-approved tech plan. Delegating to blueprint-dev."
3. Delegate to `blueprint-dev` agent with the approved plan (include CL# from C++ track if both)
4. After blueprint-dev completes, invoke `/unreal-asset-inspections` to verify properties
5. If verification fails: pass discrepancies back to blueprint-dev, re-verify (max 3 iterations)

**If `PLAN_APPROVED = false`:**
1. Spawn `blueprint-planner` agent — pass the full requirement (include CL# from C++ track if both)
2. Receive plan from blueprint-planner
3. Present the plan to the user in the main context
4. Ask user via AskUserQuestion:
   - Question: "Approve this implementation plan?"
   - Options: "Approve", "Needs changes"
5. If "Needs changes": re-spawn `blueprint-planner` with user feedback, repeat from step 2
6. If "Approve": delegate to `blueprint-dev` agent with the approved plan
7. After blueprint-dev completes, invoke `/unreal-asset-inspections` to verify properties
8. If verification fails: pass discrepancies back to blueprint-dev, re-verify (max 3 iterations)

Proceed to Stage 5.

## 5. Review

For **cpp** or **both**: invoke `/code-review` skill — pass CL#
For **blueprint** or **both**: delegate to `blueprint-reviewer` agent — pass asset paths

**Severity meanings:**
- CRITICAL/WARNING: Must fix before merge
- MINOR: Style/naming issues — should fix, not blockers
- SUGGESTION: Improvement ideas — optional
- INFO: Pre-existing issues — context only, ignore

If CRITICAL or WARNING findings exist, proceed to Stage 6. If only MINOR, ask user if they want to fix or proceed. Else skip to Stage 7.

## 6. Fix Review Findings

1. Report the findings to the user with severity counts (CRITICAL, WARNING, MINOR, INFO)
2. Delegate CRITICAL and WARNING findings for fixing to `code-dev` agent or `blueprint-dev` agent (use `PLAN_APPROVED = true` skip instructions — these fixes are pre-approved)
3. For MINOR findings: ask user if they want to fix these too, or proceed without
4. Re-run review once (/code-review and/or blueprint-reviewer)

**After re-review, check remaining findings:**
- **No CRITICAL or WARNING remaining:** Proceed to Stage 7 (MINOR and INFO are acceptable)
- **CRITICAL or WARNING still present:** Ask the user:
  > "Review found [N CRITICAL, M WARNING] remaining after fixes. Options:
  > 1. Apply another round of fixes (specify which)
  > 2. Proceed to shelve with these findings
  > 3. Abandon the changelist"
  
  Then:
  - Option 1: Return to step 2 of this stage
  - Option 2: Proceed to Stage 7
  - Option 3: Report abandonment and exit workflow

## 7. Update review description

1. Invoke `/perforce-changelist-description`

Proceed to Stage 8.

## 8. Shelve the review

1. Invoke `/swarm-review-shelve`

Proceed to Stage 9.

## 9. Done

Report:
```
Implementation: Complete
Work type: <cpp|blueprint|both>
Files changed: N (list)
Assets modified: N (list /Game/... paths)
Changelist: CL# <number>
Build: Passed (if C++)
Verification: Passed (if Blueprint)
Review: <X critical, Y warnings, Z minor, A suggestions, W info>
Shelved: Yes
```

## Rules

- For mixed tasks: C++ track completes before Blueprint track begins
- Never skip compile (C++) or asset verification (Blueprint)
- Single fix-review pass per track; user decides if more iterations needed
- Present review findings before applying fixes
