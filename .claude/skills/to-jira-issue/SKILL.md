---
name: to-jira-issue
description: "Creates a Jira issue from a plan, one issue by default (suggests a split only at XL, 1-2 weeks, or larger). ALWAYS invoke for 'create issue from plan', 'turn this into a ticket', 'create jira issue'. Delegates to the producer agent. With an approved plan, the ticket description is that plan verbatim."
allowed-tools: Read, Grep, Glob, Agent
---

# Create Jira Issue from Plan

Use PROACTIVELY when the user says: `create issue from plan`, `turn this into a ticket`, `create jira issue`, `make a jira ticket`.

> **Single-issue default**: Start with one comprehensive issue. Only suggest splitting into vertical slices if the estimate exceeds XL (1-2 weeks).

## Step 0: Detect a Validated Plan

A plan is **validated** when either:
- a plan file was written this session (`~/.claude/plans/*.md`) and the user approved it (ExitPlanMode accepted), or
- the user points at it: "this plan", "the plan", "exact plan", or a plan file path.

**Found** → follow **Plan Mode** below and skip Steps 1–5. The user already reviewed that text; rewording it throws the review away.
**Not found** → continue with Step 1.

## Plan Mode

1. **Re-read the plan file from disk** with Read right before delegating. Never reconstruct it from memory, because memory drifts from the exact text. If the plan only exists in conversation (no file), copy it exactly as last shown.
2. **Derive metadata; never edit the plan:**
   - **Summary**: imperative title ≤100 chars, from the plan's H1/Context.
   - **Estimate**: S/M/L/XL.
   - **Acceptance criteria**: testable checkboxes drawn from the plan's Verification/Change sections, appended *after* the plan. If the plan already has acceptance criteria, add none.
3. **Keep the plan intact.** Don't trim, reorder, summarize or tidy it, and that includes sections like "Unresolved questions" or "Not recommended". "Exact" means exact.
4. **Size**: if XL, offer a split as in Step 4. Each slice quotes its plan section verbatim.
5. **Confirm (lightweight)**: show only Summary, Estimate, Epic, Sprint, AC and `Description: plan verbatim (N lines, from <path>)`. If the invocation already states placement (epic, sprint/backlog) and asks to create it, that is the confirmation, so skip the quiz.
6. Delegate with the **Plan Mode producer template** in Step 6.

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

**Plan Mode (validated plan, verbatim):**
```
Create a Jira issue:
- Summary: [title]
- Estimate: [size]
- Parent epic: [key, or default]
- Sprint: [active sprint | backlog / no sprint]

Description: the text between the markers, VERBATIM. Keep headings, code blocks
and lists as markdown. Do not reword, trim, reorder or summarize. Append the
Acceptance Criteria block after it.

--- PLAN START ---
[plan file contents, exactly as read from disk]
--- PLAN END ---

## Acceptance Criteria
[checkboxes]

If Jira/Atlassian tools are unavailable, stop and say so. Never report a fake key.
If the parent epic can't be set, say so explicitly.
```

If the producer reports missing Atlassian tools, relay that to the user: the Atlassian MCP likely needs signing in via `/mcp`. Don't retry blindly.

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
**Epic:** [key or "none"]
**Sprint:** [sprint name or "Backlog"]
**Description:** [drafted | plan verbatim from <path>]
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

After presenting the created issue(s), offer:

> "Ticket created. Ready to implement? Use `/task-implementation` to start the build-verify-review cycle."

## Rules

- Never create issues without user confirmation. Explicit placement plus "create it" in the invocation args counts as confirmation.
- A validated plan goes into the description verbatim; add metadata and AC around it, never edit it
- Default to a single issue — only suggest splitting if estimate is XL or larger
- If splitting, use vertical slices (end-to-end), not horizontal (layer-by-layer)
- Each issue must have testable acceptance criteria
- User decides whether to keep as one issue or split
