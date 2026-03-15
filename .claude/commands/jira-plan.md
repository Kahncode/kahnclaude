---
name: jira-plan
description: Brainstorm ideas with user and create or update Jira issues. Does not implement work, only plans and creates/updates tasks.
scope: project
argument-hint: "[idea or issue-key]"
---

# Plan and Create Jira Issues

**Input:** $ARGUMENTS (optional — can be a raw idea or an existing issue key)

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

Before using this command, set your Jira project and preferences below. Run the setup once, then the command will use your settings for all future invocations.

```
CONFIGURE_ME: true
JIRA_PROJECT_KEY: ""
JIRA_DEFAULT_ISSUE_TYPE: "Task"
JIRA_DEFAULT_PRIORITY: "Medium"
ISSUE_TEMPLATE: ""
```

If `CONFIGURE_ME: true`, this command will ask you to fill in your Jira settings and save them to this file.

---

## Setup Instructions (First Run)

When you first use this command, you'll be asked for:

1. **Jira Project Key** — The project key (e.g., `PROJ`, `ENG`, `PLATFORM`)
2. **Default Issue Type** — Type for new issues (e.g., `Task`, `Story`, `Bug`, `Subtask`)
3. **Default Priority** — Priority level (e.g., `Low`, `Medium`, `High`, `Urgent`)
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

> Your Jira planning isn't configured yet. Let's set it up once.
>
> 1. Go to your Jira workspace and find:
>    - Your **Project Key** (visible in issue URLs like `PROJ-123`)
>    - Your **Default Issue Type** (what type should new planning issues be? Task, Story, etc.)
>    - Your **Default Priority** (Low, Medium, High, Urgent?)
>    - Your **Issue Template** (paste your team's preferred format)
>
> Provide these values:

Collect:

- Project key
- Default issue type
- Default priority
- Issue template (paste multi-line template)

Then **self-edit this command file** to replace the configuration section with their values and set `CONFIGURE_ME: false`.

### Step 2: Parse Input

Determine the mode:

**Create mode**: If no issue key pattern found (no `[A-Z]+-[0-9]+`):

- Extract the raw idea from `$ARGUMENTS`
- Proceed to brainstorm

**Update mode**: If issue key found:

- Extract the issue key using this rule: find the segment matching `[A-Z]+-[0-9]+`
- Use `getJiraIssue` to fetch current issue
- Review existing summary, description, status
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

**Execution**: 17. Estimated complexity? (rough story points: 1-3 small, 5-8 medium, 13+ large) 18. Who should own this? (assign or keep unassigned) 19. Sprint or backlog? (is there an active sprint or is this backlog refinement?) 20. Any labels or components this belongs to? (team, platform, module, epic)

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
   - "Should priority or story points change?"
   - "Any related work that blocks or depends on this?"
3. Let user drive the refinement iteratively

---

### Step 4: Structure the Task

Use the stored `ISSUE_TEMPLATE` as the skeleton. Fill in:

**Summary**

- Clear, imperative, concise (max 100 chars)
- Examples: "Add dark mode toggle", "Fix N+1 queries in user listing"

**Description** (use template)

- Insert user's context and task into the template structure
- Ensure acceptance criteria are testable checkboxes

**Metadata**

- Project: Use `JIRA_PROJECT_KEY`
- Issue Type: Use `JIRA_DEFAULT_ISSUE_TYPE` (or ask user if they want different)
- Priority: Use `JIRA_DEFAULT_PRIORITY` (or infer from brainstorm)
- Story points: From brainstorm or leave unset
- Assignee: From discussion or unassigned
- Labels: From brainstorm
- Components: From brainstorm (if team uses them)
- Sprint: Ask if there's an active sprint

---

### Step 5: Create or Update

**For create mode:**

- Call the appropriate Jira MCP tool with:
  - `summary`: the cleaned-up title
  - `description`: filled template
  - `project`: `JIRA_PROJECT_KEY`
  - `issueType`: `JIRA_DEFAULT_ISSUE_TYPE`
  - `priority`: `JIRA_DEFAULT_PRIORITY` or inferred
  - storyPoints, assignee, labels, components as discussed

**For update mode:**

- Call the appropriate Jira MCP tool with:
  - `key`: the existing issue key
  - Updated fields only
  - Keep unchanged fields omitted

---

### Step 6: Confirm & Summarize

Display:

- Issue key and URL (if created)
- Summary / Title
- Status (newly created or updated)
- Next: "Ready to implement with `/jira <issue-key>` or plan more issues"

---

## Key Rules

- **Self-edit on first run** — update the configuration section, set `CONFIGURE_ME: false`
- **Use stored template** — all issues follow your team's structure
- **Respect project context** — project key ensures issues go to the right place
- **Acceptance criteria must be testable** — not vague ("make it better")
- **Keep descriptions concise** — use template slots, don't ramble
- **Sprint awareness** — ask if there's an active sprint before assigning to it
- **Labels and components** — ask user which ones apply (if your team uses them)
