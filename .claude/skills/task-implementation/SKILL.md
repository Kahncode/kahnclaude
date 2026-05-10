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

## 1. Requirements Clarification

Before implementation, ask clarifying questions to reach shared understanding.

**Skip this step if:**
- Input already contains structured clarification (Context / Task / Acceptance Criteria / Assumptions / Out of Scope from `/task-clarification`). Extract directly and proceed.
- User says "just do it", "skip questions", "no questions".

## 2. Classify Work Type

From the input, determine:
- **cpp** — C++ files only -> code-dev + code-reviewer
- **blueprint** — Blueprint assets only -> blueprint-dev + blueprint-reviewer
- **both** — C++ and Blueprint -> all four agents, C++ first

If unclear, ask: "Does this involve C++ code, Blueprint assets, or both?"

## 3. C++ Track (if cpp or both)

1. Delegate to `code-dev` agent via Agent tool — pass the full requirement, ask it to gather context, plan, and implement without asking the user.

## 4. Blueprint Track (if blueprint or both)

1. Delegate to `blueprint-dev` agent via Agent tool — pass the full requirement (and CL# from C++ track if both)
2. Wait for user approval of the plan before blueprint-dev proceeds
3. After blueprint-dev completes, invoke `/unreal-asset-inspections` to verify properties
4. If verification fails: pass discrepancies back to blueprint-dev, re-verify (max 3 iterations)

## 5. Review

For **cpp** or **both**: invoke `/code-review` skill — pass CL#
For **blueprint** or **both**: delegate to `blueprint-reviewer` agent — pass asset paths

Present all findings to the user.

## 6. Fix Review Feedback Loop

If CRITICAL or WARNING findings:
2. Route findings to appropriate agent for fixing (code-dev for C++, blueprint-dev for Blueprint)
3. Repeat /code-review or/and /blueprint-review
4. Repeat until clean or user says stop (max 3 iterations then escalate)

## 7. Update review description
1. Invoke `/perforce-changelist-description`

## 10. Shelve the review
1. Invoke `/swarm-review-shelve`

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
- Max 3 fix iterations per track before escalating to user
- Present review findings before applying fixes
