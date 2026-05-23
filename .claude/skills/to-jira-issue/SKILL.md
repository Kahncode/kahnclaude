---
name: to-jira-issue
description: "Create a Jira issue from a plan. Defaults to ONE issue; suggests splitting only if estimate is XL (1-2 weeks) or larger. ALWAYS invoke when user says: 'create issue from plan', 'turn this into a ticket', 'create jira issue'. Delegates to producer agent for ticket creation."
allowed-tools: Read, Grep, Glob, Agent
---

# Create Jira Issue from Plan

Use PROACTIVELY when the user says: `create issue from plan`, `turn this into a ticket`, `create jira issue`, `make a jira ticket`.

> **Single-issue default**: Start with one comprehensive issue. Only suggest splitting into vertical slices if the estimate exceeds XL (1-2 weeks).

## Step 1: Gather Context

Collect the plan or specification:

- From the current conversation (user described a feature or plan)
- From a referenced document or file
- From a Jira epic or initiative (fetch with producer agent if needed)

Identify:
- The overall goal and deliverable
- Any existing constraints or deadlines
- Who the stakeholders are

## Step 2: Explore Codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code.

Spawn an **Explore agent** to investigate:
   - Current architecture and naming conventions
   - Integration points (schema, API, UI layers)
   - Existing patterns to follow
   - Related code that will be affected
   
## Step 3: Draft Single Issue

Create one comprehensive issue for the entire plan:

| Field | Description |
|-------|-------------|
| **Summary** | Clear, imperative title (max 100 chars) |
| **What to build** | Specific scope — what's included, what's not |
| **Acceptance criteria** | Testable checkboxes (not vague statements) |
| **Estimate** | T-shirt size: S (<1d), M (1-3d), L (3-5d), XL (1-2w) |

## Step 4: Evaluate Size

Check if the estimate exceeds the threshold:

- **S, M, or L** → Proceed with single issue (go to Step 5)
- **XL or larger** → Present the estimate to the user and suggest splitting:

> "This is estimated at XL (1-2 weeks). Would you like to:
> 1. Keep as a single issue
> 2. Split into smaller vertical slices"

If user chooses to split, create vertical slices (tracer bullets):
- Each slice is end-to-end (not horizontal layers)
- Each slice is independently mergeable
- Order by dependency (foundational first)

## Step 5: Quiz User

Before creating ticket(s), validate:

1. **Scope**: Is the issue (or slices) correctly scoped?
   - Anything missing or extra?

2. **Acceptance criteria**: Are they testable?
   - No vague statements

3. **Dependencies** (if split): Is the ordering correct?

Present the issue (or slice list) and ask for confirmation before proceeding.

## Step 6: Delegate to Producer

Spawn the **producer agent** with the validated issue(s):

**For a single issue:**
```
Create a Jira issue:
- Summary: [title]
- Description: [what to build]
- Acceptance criteria: [checkboxes]
- Estimate: [size]

Add to the active sprint unless specified otherwise.
```

**For multiple slices (if user chose to split):**
```
Create the following Jira issues in dependency order:

[For each slice:]
- Summary: [title]
- Description: [what to build]
- Acceptance criteria: [checkboxes]
- Blocked by: [dependencies]
- Estimate: [size]

Link issues with "blocks" / "is blocked by" relationships.
Add all issues to the active sprint unless specified otherwise.
```

The producer agent handles all Jira technicalities:
- Environment variable resolution
- Sprint detection and assignment
- Field defaults and labels
- Issue creation and linking

## Output Format

After the producer completes, summarize:

**Single issue:**
```
## Issue Created

**PROJ-123** — [title]
**Estimate:** M
**Sprint:** [sprint name or "Backlog"]
```

**Multiple slices:**
```
## Issues Created

| Key | Summary | Estimate | Blocked By |
|-----|---------|----------|------------|
| PROJ-123 | [title] | M | - |
| PROJ-124 | [title] | S | PROJ-123 |

**Total:** [count] issues, [total estimate]
**Sprint:** [sprint name or "Backlog"]
```

## Rules

- Never create issues without user confirmation
- Default to a single issue — only suggest splitting if estimate is XL or larger
- If splitting, use vertical slices (end-to-end), not horizontal (layer-by-layer)
- Each issue must have testable acceptance criteria
- User decides whether to keep as one issue or split
