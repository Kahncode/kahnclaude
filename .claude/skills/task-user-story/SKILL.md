---
name: task-user-story
description: "User story writer. ALWAYS invoke when the user asks to write a user story, create a story, turn this into a user story, or format as user story. Do not use task-planning or search the codebase — this skill reads only local docs to produce a formatted user story."
allowed-tools: Read, Glob
---

# User Story Writer

Transforms a user prompt into a well-structured user story using only local project context.

## Inputs

- **User prompt:** The raw request or feature description
- **Local context:** Architecture.md, CLAUDE.md files (no codebase searching)

## Instructions

### 1. Gather Local Context

Read available context files (don't search the codebase):

```
docs/ARCHITECTURE.md
CLAUDE.md
CLAUDE.local.md (if exists)
```

Extract: project domain, key terminology, user roles mentioned, existing patterns.

### 2. Identify Story Elements

From the user's prompt, extract:

- **Role** — who benefits (user, admin, developer, system)
- **Goal** — what they want to do
- **Benefit** — why it matters (business value)

If the role is unclear, infer from context or default to "user".

### 3. Draft Acceptance Criteria

Write 3-5 specific, testable criteria. Each should be:

- Observable (can be verified)
- Scoped (not vague)
- Independent (doesn't duplicate others)

### 4. Add Technical Context

If Architecture.md or CLAUDE.md mention relevant:

- Components or modules
- Patterns to follow
- Constraints or dependencies

Include a brief "Technical Context" section referencing these.

### 5. Output Format

```markdown
## [Story Title]

**As a** [role]
**I want** [goal]
**So that** [benefit]

### Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Technical Context

[Relevant info from Architecture.md/CLAUDE.md, or "None identified" if docs unavailable]
```

### 6. Present and Offer Next Steps

Output the formatted user story directly. Don't ask for confirmation — the user will adjust if needed.

After presenting the story, offer:

> "Story ready. Next step?
> - `/to-jira-issue` — create a Jira ticket from this story
> - `/task-planning` — break down into implementation tasks"
