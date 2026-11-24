---
name: github-issue-plan
description: Brainstorm ideas with user and create or update GitHub issues via the gh CLI. Does not implement work, only plans and creates/updates issues.
scope: project
argument-hint: "[idea or issue-number]"
allowed-tools: Bash(gh issue:*), Bash(gh label:*), Bash(gh repo view:*), Bash(gh project:*), Bash(gh auth status:*), Read, Edit, Glob, Grep, AskUserQuestion
---

# Plan and Create GitHub Issues

**Input:** the user's argument (optional — a raw idea, an issue number like `42` / `#42`, or an issue URL)

Requires the `gh` CLI, authenticated (`gh auth status`).

## About This Command

This command's **primary purpose is discovery and brainstorming**, not quick issue creation. Explore both the product need and the technical design before writing the issue. Expect to ask 15-20 questions and iterate until the idea is well-specified.

**Don't rush to create the issue.** Keep asking follow-up questions until you fully understand:

- The user problem being solved
- The business impact
- The technical approach and constraints
- What's in scope and what's not
- Potential risks or unknowns

The issue is the **output** of thorough brainstorming, not the input.

## Configuration

```
CONFIGURE_ME: true
GITHUB_REPO:            # owner/repo; blank = current repo
GITHUB_PROJECT:         # optional: project number to add new issues to
GITHUB_PROJECT_OWNER:   # owner of that project (user or org)
DEFAULT_LABELS: ""      # comma-separated, applied to every new issue
ISSUE_TEMPLATE: ""
```

If `CONFIGURE_ME: true`, ask the user to fill these in on first run and save them to this file.

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

---

## Workflow

### Step 1: Check Configuration

If `CONFIGURE_ME: true`, ask the user for:

- Repository (offer the current repo from `gh repo view --json nameWithOwner -q .nameWithOwner` as the default)
- Project number and owner (optional)
- Default labels (optional; show `gh label list` to help choose)
- Issue template (interactively accept or modify the example)

Then **edit this skill file** to replace the configuration block with their values and set `CONFIGURE_ME: false`.

### Step 2: Parse Input

**Update mode**: the input contains an issue number or `/issues/<n>` URL.

- Run `gh issue view <n> --repo REPO --json number,title,body,state,labels,assignees,milestone,comments`
- Review the existing title, body, labels, and comments
- Proceed to refinement

**Create mode**: otherwise.

- Treat the input as the raw idea
- Proceed to brainstorm

---

### Step 3: Brainstorm & Clarify (Deep Discovery Phase)

Ask thorough questions. Keep going until the scope is clear.

#### For create mode:

**Product & User Context:**

1. What's the user-facing problem this solves?
2. Who are the users affected? (primary, secondary, internal)
3. What's the business impact? (revenue, retention, competitive advantage)
4. How will you measure success? (concrete metrics)
5. Are there related features or dependencies in the product?
6. What's the priority? (nice-to-have, important, urgent, blocking)

**Technical & Design Constraints:**

7. What's the technical scope? (API endpoint, UI component, migration, etc.)
8. Does this touch multiple systems? (frontend, backend, database, deployment)
9. Performance or scalability concerns?
10. Security or compliance implications?
11. Does this fit current architecture patterns or require refactoring?
12. Integration points? (other services, third-party APIs)
13. Browser/platform compatibility, if user-facing?

**Scope & Boundaries:**

14. What's explicitly out of scope?
15. Phased approach? (MVP vs polish vs future)
16. Dependencies or blockers on other issues?

**Execution:**

17. Estimated complexity? (small / medium / large)
18. Who should own this? (assign or leave unassigned)
19. Which labels or milestone apply?

Then:

1. **Synthesize**: summarize the problem statement, user impact, technical approach, scope boundaries, and risks
2. **Confirm**: "Does this capture it correctly? Anything to adjust?"

#### For update mode:

1. Review the fetched issue carefully
2. Ask what needs to change and why (unclear scope, weak acceptance criteria, missing technical context, changed priority, related work)
3. Let the user drive refinement iteratively

---

### Step 4: Structure the Issue

Use `ISSUE_TEMPLATE` as the skeleton.

**Title:** clear, imperative, max 80 chars (e.g. "Add dark mode toggle").

**Body:** fill the template. Acceptance criteria must be testable checkboxes. Reference related issues as `#N`.

**Metadata:**

- Labels: `DEFAULT_LABELS` plus those from the brainstorm. Only use labels that exist (`gh label list`); ask before creating new ones.
- Assignee: from discussion, or none
- Milestone: from discussion, or none
- Priority and estimate: GitHub has no native fields; express them as labels if the repo has them, otherwise in the body

---

### Step 5: Create or Update

Write the body to a temporary file and pass it with `--body-file` to avoid shell quoting issues.

**Create mode:**

```bash
gh issue create --repo REPO --title "<title>" --body-file <file> --label "<a>,<b>" [--assignee <user>] [--milestone "<name>"] [--project "<project title>"]
```

Use `--project` only when `GITHUB_PROJECT` is set. `gh issue create` prints the issue URL.

**Update mode:**

```bash
gh issue edit <n> --repo REPO [--title "<title>"] [--body-file <file>] [--add-label ...] [--remove-label ...] [--add-assignee ...] [--milestone ...]
```

Pass only the fields that change.

---

### Step 6: Confirm & Summarize

Display:

- Issue number and URL
- Title
- Whether it was created or updated
- Next: "Ready to implement with `/github-issue <issue-number>` or plan more issues"

---

## Key Rules

- **Self-edit on first run** — update the configuration block, set `CONFIGURE_ME: false`
- **Use the stored template** — all issues follow the same structure
- **Acceptance criteria must be testable** — not vague
- **Keep bodies concise** — use template slots, don't ramble
- **Never create labels or milestones without asking**
