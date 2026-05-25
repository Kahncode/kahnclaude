---
name: task-planning
description: "Task planner. ALWAYS invoke when the user says: plan task, clarify requirements, break down ticket, structure this, scope this work, what needs to happen, turn this into a Jira ticket. Also invoke for raw/unstructured requests that need scoping before implementation. Do not delegate to code-dev or producer without first structuring the requirements."
allowed-tools: Read, Grep, Glob, Agent
---

# Task Planning

Takes raw, unstructured task descriptions and produces structured, actionable breakdowns.

## Reference

See @docs/standards/planning/task-clarification.md for acceptance criteria patterns and ambiguity checklist.

## Flow

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

### 5. Plan Implementation (Standard/Complex Only)

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

### 7. Produce Structured Output

Use this minimal format. Every line must be actionable.

**For trivial tasks:**

```
## [Task Title]
**Do:** [What to change]
**Done when:** [Single testable criterion]
```

**For standard/complex tasks:**

```
## [Task Title]

**Context:** [1 sentence — why this matters]

**Scope:**
- In: [What's included]
- Out: [What's explicitly excluded]

**Acceptance Criteria:**
- [ ] [Specific, testable — 3-5 items max]

**Plan:** (if non-trivial)
| File | Change |
|------|--------|
| path/to/file.h | Add X method |
| path/to/file.cpp | Implement X |

**Risks:** [Only if real risks exist — omit if none]
```

**Rules:**
- No "Assumptions" section — state facts or ask questions instead
- Max 5 acceptance criteria — if more, the task should be split
- Risks only for genuine concerns, not boilerplate

### 8. Present and Offer Next Steps

Present the structured output directly. Don't ask "does this look right?" — if wrong, user will say so.

Offer routing: "Ready to implement, create a Jira ticket, or adjust something?"

- **Implement** — hand off to `/task-implementation` with the approved output
- **Create Jira ticket** — hand off to `producer` agent with the approved output
- **Adjust** — iterate on the output
