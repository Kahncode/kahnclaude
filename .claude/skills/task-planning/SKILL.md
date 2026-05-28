---
name: task-planning
description: "Task planner. ALWAYS invoke when the user says: plan task, clarify requirements, break down ticket, structure this, scope this work, what needs to happen, turn this into a Jira ticket. Also invoke for raw/unstructured requests that need scoping before implementation. Do not delegate to code-dev or producer without first structuring the requirements."
allowed-tools: Read, Grep, Glob, Agent, EnterPlanMode, ExitPlanMode
---

# Task Planning

Takes raw, unstructured task descriptions and produces structured, actionable breakdowns.

## Reference

See @docs/standards/planning/task-clarification.md for acceptance criteria patterns and ambiguity checklist.

## Flow

### 0. Enter Plan Mode

**ALWAYS start by calling EnterPlanMode.** This enables the formal planning system with a dedicated plan file and user approval gate. Write all plan content to the plan file specified in the system message, not as chat output.

### 1. Analyze Raw Input

Read the task description and identify:
- Core intent (what needs to happen)
- Missing context (who, why, when, where)
- Ambiguous terms (vague scope, undefined boundaries)

### 2. Explore Before Asking

Before asking the user anything, gather context from the codebase:

1. **Find related code** — grep for keywords from the task, check file structure
2. **Check existing patterns** — read implementations the task might extend or modify
3. **Trace dependencies** — check includes, module boundaries, .Build.cs files
4. **Identify constraints** — look for TODOs, FIXMEs, or comments about the area

Use what you find to:
- Answer your own questions when possible (state what you found)
- Make questions specific ("I see XModule handles Y — does the new feature go there or in a new module?")
- Reduce questions to only those requiring human judgment

### 3. Ask Clarifying Questions

Ask ONE question at a time. Only ask what the codebase couldn't answer:
- Scope boundaries ("Does X include Y?")
- Success criteria ("How will you know this is done?")
- Business context ("Who is this for?")

### 4. Assess Complexity

- **Trivial** (single file, <20 lines) — skip to Step 7
- **Standard** (multiple files, clear scope) — proceed to Step 5, skip Step 6
- **Complex** (cross-module, architectural changes) — proceed to Steps 5 + 6

Indicators of complexity:
- New public APIs or module boundaries
- Changes to header files in Public/
- Cross-module dependencies
- Replication or networking changes

### 5. Plan Implementation (Standard/Complex Code Only)

Spawn `code-planner` with the structured requirements.

Include in the prompt:
- The structured output you drafted
- File paths identified during exploration
- Specific questions about implementation approach

If code-planner surfaces new scope questions, return to Step 3.

### 6. Architecture Review (Complex Only)

Only for tasks touching:
- Public APIs or module boundaries
- Replication/networking
- Header files in Public/
- New inheritance hierarchies

Spawn `code-reviewer` with dimension "architecture" and the implementation plan. Incorporate critical findings before presenting to user.

### 7. Write the Plan

Write the plan to the plan file. Use this format — be thorough since this is the user's approval checkpoint.

```markdown
# [Task Title]

## Context
[Why this matters — 2-3 sentences connecting to project goals]

## Scope
**In scope:**
- [Specific item 1]
- [Specific item 2]

**Out of scope:**
- [Explicitly excluded item]

## Investigation Summary
[What you found exploring the codebase — relevant files, patterns, constraints]

## Implementation Plan

### Phase 1: [Name]
| Step | File | Change | Why |
|------|------|--------|-----|
| 1 | path/to/file.h | Add X method declaration | Enables Y |
| 2 | path/to/file.cpp | Implement X | Core logic |

### Phase 2: [Name] (if applicable)
| Step | File | Change | Why |
|------|------|--------|-----|
| ... | ... | ... | ... |

## Acceptance Criteria
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## Risks & Mitigations
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| [Only genuine risks] | Low/Med/High | [How to handle] |

## Open Questions (if any)
- [Questions requiring user input before implementation]

## Estimate
[T-shirt size: XS/S/M/L/XL with brief justification]
```

**Rules:**
- Every file change needs a "Why" — forces you to justify each modification
- Max 5 acceptance criteria — if more, split the task
- Risks only for genuine concerns, not boilerplate
- Estimate helps user decide if scope is right

### 8. Request Approval

Call **ExitPlanMode** to submit the plan for user approval. Do NOT ask "does this look right?" in chat — the plan mode UI handles approval.

After approval, offer routing:
- **Implement** — hand off to `code-dev` agent with the approved plan
- **Create Jira ticket** — hand off to `producer` agent
- **Adjust** — re-enter plan mode and revise
