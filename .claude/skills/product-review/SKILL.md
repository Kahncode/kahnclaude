---
name: product-review
description: "Meeting prep orchestrator. ALWAYS invoke when the user asks to prepare for a product review, standup, status update, or sprint demo. Do not call changelog or Jira tools directly — this skill compiles recent work and upcoming tasks into a non-technical summary."
allowed-tools: Skill, mcp__atlassian__searchJiraIssuesUsingJql, mcp__atlassian__getJiraIssue
---

# Product Review Prep

**Input:** $ARGUMENTS

Prepares a meeting-ready summary of completed work and upcoming tasks.

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `JIRA_PROJECT_KEY` | Jira project key for sprint queries |
| `JIRA_ASSIGNEE_ACCOUNT_ID` | Your Jira account ID |
| `P4USER` | Perforce username (for changelog) |

## Flow

### 1. Parse Arguments

Optional argument: **days** — Number of days to look back (default: 7).

### 2. Gather Recent Work

Invoke the `perforce-changelog` skill with the days argument:

```
/perforce-changelog <days>
```

Capture the changelog output. Do NOT present the raw changelog to the user yet.

### 3. Translate to Plain Language

Rewrite each changelog entry:
- Remove technical jargon (CL numbers, file paths, module names)
- Focus on user-visible outcomes: "Added X feature", "Fixed bug where Y happened"
- Group by theme/feature rather than by commit type
- Skip internal refactors and test-only changes unless they're significant

### 4. Fetch Sprint Tasks

Query Jira for your in-progress and upcoming tasks:

```
project = $JIRA_PROJECT_KEY AND assignee = currentUser() AND sprint in openSprints() AND status != Done ORDER BY status DESC, priority DESC
```

For each task, extract: key, summary, status, priority.

### 5. Categorize Tasks

Group tasks into:
- **In Progress** — actively being worked on
- **Up Next** — to-do items in the current sprint
- **Blocked** (if any) — note the blocker

### 6. Present Summary

Output in this format:

---

## What I've Done (Last X Days)

- [Plain language summary of each completed item]
- [Grouped by feature/theme, not by commit type]

## What I'm Working On

- [In-progress task summaries]

## What's Next

- [Upcoming task summaries]

## Blockers (if any)

- [Any blocked items with context]

---

### 7. Optional: Offer Export

Ask:
> Would you like me to copy this to your clipboard, or save it somewhere?
