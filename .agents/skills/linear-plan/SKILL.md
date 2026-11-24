---
name: linear-plan
description: Brainstorm ideas with user and create or update Linear issues. Does not implement work, only plans and creates/updates tasks.
scope: project
argument-hint: "[idea or issue-id]"
---

# Plan and Create Linear Issues

**Input:** $ARGUMENTS (optional — can be a raw idea or an existing issue ID)

## About This Command

This command's **primary purpose is discovery and brainstorming**, not quick task creation. The goal is to thoroughly explore both the product need and technical design before writing the task description. Questions drive clarity. Expect to ask 15-20 questions and iterate until the idea is well-specified. This upfront work prevents scope creep, rework, and misaligned implementation.

**Don't rush to create the task.** Keep asking follow-up questions until you fully understand:

- The user problem being solved
- The business impact
- The technical approach and constraints
- What's in scope and what's not
- Potential risks or unknowns

The task itself is the **output** of thorough brainstorming, not the input.

## Configuration

Before using this command, set your Linear team and project IDs below. Run the setup once, then the command will use your settings for all future invocations.

```
CONFIGURE_ME: true
LINEAR_TEAM_ID:
LINEAR_PROJECT_ID:
LINEAR_DEFAULT_STATUS: "Backlog"
ISSUE_TEMPLATE: ""
```

If `CONFIGURE_ME: true`, this command will ask you to fill in your Linear settings and save them to this file.

---

## Setup Instructions (First Run)

When you first use this command, you'll be asked for:

1. **Linear Team ID** — The UUID of your Linear team
2. **Linear Project ID** — The UUID of your planning project
3. **Default Status** — Initial status for new issues (e.g., `Backlog`, `Todo`, `In Progress`)
4. **Issue Template** — Your team's issue template (Markdown format). Interactively ask the user to modify or accept the current template.

Example template:

```markdown
## Context

[Why is this work needed? What problem does it solve?]

## Task

[Specific work to be done. Keep it focused and scope-bounded.]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Out of Scope

[What should NOT be included in this issue?]
```

Once configured, this command remembers your settings and uses them automatically.

---

## Workflow

### Step 1: Check Configuration

If `CONFIGURE_ME: true`, ask the user:

> Your Linear planning isn't configured yet. Let's set it up once.
>
> 1. Go to your Linear workspace and find:
>    - Your **Team ID** (Settings → Team → copy from URL or API section)
>    - Your **Project ID** (Project → Settings → copy from URL or API section)
>
> Paste them here:

Collect:

- Team ID
- Project ID
- Default status (Backlog, Todo, etc.)
- Issue template (paste multi-line template)

Then **self-edit this command file** to replace the configuration section with their values and set `CONFIGURE_ME: false`.

### Step 2: Parse Input

Determine the mode:

**Create mode**: If no issue ID pattern found (no `[A-Z]+-[0-9]+`):

- Extract the raw idea from `$ARGUMENTS`
- Proceed to brainstorm

**Update mode**: If issue ID found:

- Extract the issue ID using this rule: find the segment matching `[A-Z]+-[0-9]+`
- Use `mcp__claude_ai_Linear__get_issue` to fetch current issue
- Review existing title, description, state
- Proceed to refinement

---

### Step 3: Brainstorm & Clarify (Deep Discovery Phase)

**This is the critical discovery phase. Do NOT rush to task creation.** Ask thorough questions to understand both the product need and technical design. Keep asking follow-up questions until the scope is crystal clear.

#### For **create mode**:

**Product & User Context** (understand the "why" and impact):

1. What's the user-facing problem this solves? (describe the user's pain point)
2. Who are the users affected? (primary users, secondary users, internal tools?)
3. What's the business impact? (revenue, retention, competitive advantage?)
4. How will you measure success? (concrete metrics, not vague goals)
5. Are there related features or dependencies in the product?
6. What's the priority? (nice-to-have, important, urgent, blocking other work?)

**Technical & Design Constraints**: 7. What's the technical scope? (new API endpoint, UI component, database migration, etc.) 8. Does this require changes to multiple systems? (frontend, backend, database, deployment?) 9. Are there performance or scalability concerns? (load, latency, storage?) 10. Security or compliance implications? (auth, data privacy, PCI, GDPR?) 11. Existing architecture considerations? (does this fit current patterns or require refactoring?) 12. Integration points? (with other services, third-party APIs, external systems?) 13. Browser/platform compatibility? (if user-facing, what versions?)

**Scope & Boundaries**: 14. What's NOT included? (explicitly state out-of-scope to avoid scope creep) 15. Are there phased approaches? (MVP vs polish vs future enhancements?) 16. Dependencies or blockers? (does this depend on other work?)

**Execution**: 17. Estimated complexity? (rough story points: 1-2 small, 3-5 medium, 8+ large) 18. Who should own this? (assign or keep unassigned) 19. Any labels or epic this belongs to? (team component, feature area, epic)

2. **Synthesize understanding**: Summarize back to user with:
   - Clear problem statement
   - User impact
   - Technical approach
   - Scope boundaries
   - Risks or unknowns

3. **Confirm before creating**: "Does this capture it correctly? Anything to adjust?"

#### For **update mode**:

1. Review the fetched issue carefully
2. Ask what needs to change and why:
   - "Is the scope unclear? Need better acceptance criteria?"
   - "Missing technical context? New constraints discovered?"
   - "Should priority or estimate change?"
   - "Any related work that blocks or depends on this?"
3. Let user drive the refinement iteratively

---

### Step 4: Structure the Task

Use the stored `ISSUE_TEMPLATE` as the skeleton. Fill in:

**Title**

- Clear, imperative, concise (max 80 chars)
- Examples: "Add dark mode toggle", "Fix N+1 queries in user listing"

**Description** (use template)

- Insert user's context and task into the template structure
- Ensure acceptance criteria are testable checkboxes

**Metadata**

- Status: Use `LINEAR_DEFAULT_STATUS` (or ask user if they want different)
- Team ID: Use `LINEAR_TEAM_ID`
- Project ID: Use `LINEAR_PROJECT_ID`
- Priority: Infer from brainstorm or default to 3 (Normal)
- Estimate: From brainstorm or leave unset
- Assignee: From discussion or null
- Labels: From brainstorm

---

### Step 5: Create or Update

**For create mode:**

- Call `mcp__claude_ai_Linear__save_issue` with:
  - `title`: the cleaned-up title
  - `description`: filled template
  - `team`: `LINEAR_TEAM_ID` (always required)
  - `project`: `LINEAR_PROJECT_ID` (always required)
  - `state`: `LINEAR_DEFAULT_STATUS` (always required)
  - Priority, estimate, assignee, labels as discussed

**For update mode:**

- Call `mcp__claude_ai_Linear__save_issue` with:
  - `id`: the existing issue ID
  - Updated fields only
  - Keep unchanged fields omitted

---

### Step 6: Confirm & Summarize

Display:

- Issue ID and URL (if created)
- Title
- Status (newly created or updated)
- Next: "Ready to implement with `/linear <issue-id>` or plan more issues"

---

## Key Rules

- **Self-edit on first run** — update the configuration section, set `CONFIGURE_ME: false`
- **Use stored template** — all issues follow your team's structure
- **Respect team context** — team and project IDs ensure issues go to the right place
- **Acceptance criteria must be testable** — not vague ("make it better")
- **Keep descriptions concise** — use template slots, don't ramble
- **Labels and epics** — ask user which epic (if your team uses them)
