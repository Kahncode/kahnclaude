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

### 0a. Get Ticket Content
1. Use `mcp__atlassian__getJiraIssue` with:
   - `fields: ["summary", "status", "description", "assignee"]`
2. Extract the implementation plan from description

### 0b. Mark In Progress
1. Use `mcp__atlassian__transitionJiraIssue` to move the ticket to In Progress (transition ID 21)
2. If transition fails, warn the user but continue

Skip if: no ticket reference, or user says "don't update Jira".

## 1. Classify Work Type

From the input, determine:
- **cpp** — C++ files only -> code-dev + code-reviewer
- **blueprint** — Blueprint assets only -> blueprint-dev + blueprint-reviewer
- **both** — C++ and Blueprint -> all four agents, C++ first

If unclear, ask: "Does this involve C++ code, Blueprint assets, or both?"

## 2. C++ Track (if cpp or both)

1. Delegate to `code-dev` agent — pass the full input (ticket content, user prompt, and any context)
2. Proceed to Stage 3 if both, else proceed to Stage 4

## 3. Blueprint Track (if blueprint or both)

1. Delegate to `blueprint-dev` agent — pass the full input (include CL# from C++ track if both)
2. After blueprint-dev completes, invoke `/unreal-asset-inspections` to verify properties
3. If verification fails: pass discrepancies back to blueprint-dev, re-verify (max 3 iterations)
4. Proceed to Stage 4

## 4. Review

For **cpp** or **both**: invoke `/code-review` skill — pass CL#
For **blueprint** or **both**: delegate to `blueprint-reviewer` agent — pass asset paths

**Severity meanings:**
- CRITICAL/WARNING: Must fix before merge
- MINOR: Style/naming issues — should fix, not blockers
- SUGGESTION: Improvement ideas — optional
- INFO: Pre-existing issues — context only, ignore

If CRITICAL or WARNING findings exist, proceed to Stage 5. If only MINOR, ask user if they want to fix or proceed. Else skip to Stage 6.

## 5. Fix Review Findings

1. Report the findings to the user with severity counts (CRITICAL, WARNING, MINOR, INFO)
2. Delegate CRITICAL and WARNING findings for fixing to `code-dev` agent or `blueprint-dev` agent
3. For MINOR findings: ask user if they want to fix these too, or proceed without
4. Re-run review once (/code-review and/or blueprint-reviewer)

**After re-review, check remaining findings:**
- **No CRITICAL or WARNING remaining:** Proceed to Stage 6 (MINOR and INFO are acceptable)
- **CRITICAL or WARNING still present:** Ask the user:
  > "Review found [N CRITICAL, M WARNING] remaining after fixes. Options:
  > 1. Apply another round of fixes (specify which)
  > 2. Proceed to shelve with these findings
  > 3. Abandon the changelist"
  
  Then:
  - Option 1: Return to step 2 of this stage
  - Option 2: Proceed to Stage 6
  - Option 3: Report abandonment and exit workflow

## 6. Update review description

1. Invoke `/perforce-changelist-description`

Proceed to Stage 7.

## 7. Shelve the review

1. Invoke `/swarm-review-shelve`

Proceed to Stage 8.

## 8. Done

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
