---
name: task-implementation
description: "Unified implementation orchestrator. ALWAYS invoke when the user asks to implement, build, or modify C++ code, Blueprint assets, or both. Do not invoke sub-agents directly — this skill routes to the correct agents and drives the full implement-verify-review-shelve cycle."
disable-model-invocation: true
allowed-tools: Agent, Read, Grep, Glob, Skill, ToolSearch, mcp__atlassian__*
---

# Unified Implementation Workflow

Use PROACTIVELY when the user says: `implement this`, `implement feature`, `build this`, `code this up`, `modify blueprint`, `implement task`.

**Input:** $ARGUMENTS

## 0. Ticket Setup

If the input contains a Jira ticket reference (e.g., `CLTR-123`):

### 0a. Mark In Progress
1. Use `mcp__atlassian__getTransitionsForJiraIssue` to get available transitions
2. Find the "In Progress" transition (or similar: "Start Progress", "Begin Work")
3. Use `mcp__atlassian__transitionJiraIssue` to move the ticket to In Progress
4. If transition fails, warn the user but continue

Skip if: no ticket reference, or user says "don't update Jira".

## 0.5. Detect Pre-Approved Plan

Check if the input contains structured output from `/task-planning`:

**Has pre-approved plan if ALL of:**
- Contains `**Plan:**` section with a `| File | Change |` table
- Contains `**Acceptance Criteria:**` section

If pre-approved plan detected:
- Set `PLAN_APPROVED = true`
- Extract the Plan table and Acceptance Criteria for sub-agents
- Skip Stage 1 entirely

If no pre-approved plan:
- Set `PLAN_APPROVED = false`
- Proceed to Stage 1

## 1. Requirements Clarification

Before implementation, ask clarifying questions to reach shared understanding.

**Skip this step if:**
- `PLAN_APPROVED = true` (Stage 0.5 detected pre-approved plan)
- User says "just do it", "skip questions", "no questions".

## 2. Classify Work Type

From the input, determine:
- **cpp** — C++ files only -> code-dev + code-reviewer
- **blueprint** — Blueprint assets only -> blueprint-dev + blueprint-reviewer
- **both** — C++ and Blueprint -> all four agents, C++ first

If unclear, ask: "Does this involve C++ code, Blueprint assets, or both?"

## 3. C++ Track (if cpp or both)

**If `PLAN_APPROVED = true`:**
1. Delegate to `code-dev` agent via Agent tool with this prompt:
   > "The following task has an APPROVED implementation plan. Skip Step 2 (Plan) entirely — do NOT present a plan or wait for approval. Proceed directly to Step 1 (Gather Context), then Step 3 (Implement), then Step 4 (Validate).
   > 
   > [Include: Task title, Context, Scope, Acceptance Criteria, Plan table]"

**If `PLAN_APPROVED = false`:**
1. Delegate to `code-dev` agent via Agent tool — pass the full requirement
2. Wait for code-dev to present a plan and receive user approval before it proceeds

Proceed to Stage 4 if both, else proceed to Stage 5.

## 4. Blueprint Track (if blueprint or both)

**If `PLAN_APPROVED = true`:**
1. Delegate to `blueprint-dev` agent via Agent tool with this prompt:
   > "The following task has an APPROVED implementation plan. Skip Step 2 (Plan) entirely — do NOT present a plan or wait for approval. Proceed directly to Step 1 (Gather Context), then Step 3 (Implement), then Step 4 (Verify).
   > 
   > [Include: Task title, Context, Scope, Acceptance Criteria, Plan table, CL# from C++ track if both]"
2. After blueprint-dev completes, invoke `/unreal-asset-inspections` to verify properties
3. If verification fails: pass discrepancies back to blueprint-dev, re-verify (max 3 iterations)

**If `PLAN_APPROVED = false`:**
1. Delegate to `blueprint-dev` agent via Agent tool — pass the full requirement (and CL# from C++ track if both)
2. Wait for blueprint-dev to present a plan and receive user approval before it proceeds
3. After blueprint-dev completes, invoke `/unreal-asset-inspections` to verify properties
4. If verification fails: pass discrepancies back to blueprint-dev, re-verify (max 3 iterations)

Proceed to Stage 5.

## 5. Review

For **cpp** or **both**: invoke `/code-review` skill — pass CL#
For **blueprint** or **both**: delegate to `blueprint-reviewer` agent — pass asset paths

If CRITICAL or WARNING findings exist, proceed to Stage 6. Else skip to Stage 7.

## 6. Fix Review Findings

1. Report the findings to the user with severity counts
2. Delegate findings for fixing to `code-dev` agent or `blueprint-dev` agent (use `PLAN_APPROVED = true` skip instructions — these fixes are pre-approved)
3. Re-run review once (/code-review and/or blueprint-reviewer)

**After re-review, check remaining findings:**
- **No CRITICAL or WARNING remaining:** Proceed to Stage 7
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
Review: <X critical, Y warnings, Z info>
Shelved: Yes
```

## Rules

- For mixed tasks: C++ track completes before Blueprint track begins
- Never skip compile (C++) or asset verification (Blueprint)
- Single fix-review pass per track; user decides if more iterations needed
- Present review findings before applying fixes
