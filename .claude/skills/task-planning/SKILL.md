---
name: task-planning
description: "Task planner. ALWAYS invoke when the user says: plan task, clarify requirements, break down ticket, structure this, scope this work, what needs to happen, turn this into a Jira ticket. Also invoke for raw/unstructured requests that need scoping before implementation. Do not delegate to code-dev or producer without first structuring the requirements."
allowed-tools: Read, Agent, SendMessage, EnterPlanMode, ExitPlanMode
---

# Task Planning

Takes raw, unstructured task descriptions and produces structured, actionable breakdowns — **without filling the main conversation's context with codebase exploration.**

## The core idea: you orchestrate, agents explore

This skill exists to produce a plan while keeping the main conversation lean. Exploration — grepping, reading files, tracing dependencies — burns the main context window fast, and once it's gone it's gone for the rest of the session (implementation, review, follow-ups all share it).

So the division of labor is strict: **you (the main agent) never explore the codebase yourself.** You triage the request, hand it to `code-planner`, and assemble the plan from what that agent returns. The planner reads the files; you read its summary. That's the whole point — don't defeat it by "just quickly checking one file." You have no `Grep`/`Glob` here precisely so this stays honest.

If you find yourself wanting to read source to answer a question, that's a signal to send the question to the planner, not to open the file.

## Reference

See @docs/standards/planning/task-clarification.md for acceptance criteria patterns and the ambiguity checklist.

## Flow

### 0. Enter Plan Mode

Start by calling `EnterPlanMode`. This enables the formal planning system with a dedicated plan file and a user approval gate. Write all plan content to the plan file named in the system message, not as chat output.

### 1. Triage the request (from the task text only)

Read the user's request and pull out, *without touching the codebase*:
- **Core intent** — what needs to happen, in one line.
- **Obvious unknowns** — vague scope, undefined boundaries, terms only the user can define.
- **Any constraints the user already gave** — ticket IDs, file hints, "must not break X."

Keep this to a few seconds of thought. You are not solving the task here — you're packaging it for the planner.

### 2. Delegate exploration and drafting to `code-planner`

Spawn `code-planner` and let it do the heavy lifting: find related code, read the relevant implementations, trace dependencies, and draft the plan. It is read-only and returns a structured result — exactly what you need.

Give it a prompt shaped like this:

```
Plan this task. Explore the codebase and return a structured result.

TASK: <the user's request, verbatim or lightly cleaned up>
KNOWN CONSTRAINTS: <anything the user already specified — files, tickets, must-nots>

Return:
1. Investigation Summary — relevant files (with paths), existing patterns this
   touches, dependencies, and any TODO/FIXME constraints you found.
2. Complexity — Trivial (single file, <20 lines) / Standard (multiple files,
   clear scope) / Complex (cross-module, public APIs, replication, new
   inheritance, Public/ headers). Say which and why.
3. Draft Implementation Plan — phased table of {step, file, change, why}.
4. New Dependencies — your `### New Dependencies` section, or `none`.
5. Open Questions — only things that genuinely need the user's judgment and that
   you could NOT answer from the code. For each, state what you found and what's
   still ambiguous.
```

When it returns, you have the investigation, the draft plan, a complexity verdict, and a clean list of questions — all without spending your own context on file reads.

> Do not second-guess the planner by re-exploring. If its result looks thin or wrong, send it back more specifics (Step 3 mechanism), don't open the files yourself.

### 3. Clarify with the user

Take the planner's **Open Questions** and ask the user. Batch genuinely related questions into a single `AskUserQuestion` call (it's fine to ask 2–4 at once when they're tightly related); don't drip one-at-a-time if it wastes the user's time. Only ask what the planner couldn't resolve from the code — scope boundaries, success criteria, business context.

If the answers materially change scope, **continue the same planner via `SendMessage`** (it still holds all the context it gathered) rather than spawning a fresh one or exploring inline:

```
SendMessage to the code-planner: "User clarified: <answers>. Update the plan and
open questions accordingly."
```

Loop here until there are no blocking questions left.

### 4. Architecture review (Complex only)

If the planner flagged the task **Complex** — public APIs, module boundaries, replication/networking, `Public/` headers, or new inheritance hierarchies — spawn `code-reviewer` with the dimension "architecture" and the draft plan. Fold any critical findings into the plan before showing the user. Skip this entirely for Trivial/Standard work.

### 5. Write the plan

Write the plan to the plan file, assembled from the planner's return. Be thorough — this is the user's approval checkpoint.

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
[From the planner — relevant files, patterns, constraints]

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

## New Dependencies
[From the planner, with its WARNING table, or `none`]

## Acceptance Criteria
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## Risks & Mitigations
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| [Only genuine risks] | Low/Med/High | [How to handle] |

## Open Questions (if any)
- [Questions still needing user input before implementation]

## Estimate
[T-shirt size: XS/S/M/L/XL with brief justification]
```

**Rules:**
- Every file change needs a "Why" — forces you to justify each modification.
- Max 5 acceptance criteria — if more, split the task.
- Risks only for genuine concerns, not boilerplate.
- Estimate helps the user decide if scope is right.

### 6. Exit Plan Mode

Call `ExitPlanMode` immediately after writing the plan. Do not ask "does this look right?" — calling `ExitPlanMode` *is* the approval request; the plan mode UI shows your plan and handles approval.

Offer routing:
- **Implement** — hand off to `code-dev` with the approved plan.
- **Create Jira ticket** — hand off to `producer`.
- **Adjust** — re-enter plan mode and revise.
