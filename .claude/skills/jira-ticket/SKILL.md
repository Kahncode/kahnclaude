---
name: jira-ticket
description: "Jira ticket expert. ALWAYS invoke when the user asks to create, update, or manage a Jira ticket. Do not call Jira MCP tools directly — this skill applies project conventions, auto-labels, and field defaults. For full requirements workflows, use the producer agent."
allowed-tools: Read, Grep, Glob, mcp__atlassian__*
---

# Create or Update Jira Tickets

Use PROACTIVELY when the user says: `create jira ticket`, `create ticket`, `update ticket`, `new jira issue`.

> **When to use this skill vs the `producer` agent:** This skill is the fast path for straightforward ticket creation — you already know what needs to be created. The `producer` agent adds requirements clarification, dependency analysis, and estimation on top. When requirements are unclear or cross-team coordination is needed, prefer the `producer` agent.

## Reference

See @docs/standards/jira/jira-ticket.md for issue types, fields, description format, and acceptance criteria patterns.

## Required Environment Variables

| Variable | Fallback |
|----------|----------|
| `JIRA_CLOUD_ID` | Ask user for any Atlassian URL, auto-extract |
| `JIRA_PROJECT_KEY` | Ask user |
| `JIRA_ASSIGNEE_ACCOUNT_ID` | Auto-detect via `atlassianUserInfo` MCP |

## Optional Environment Variables

| Variable | Default |
|----------|---------|
| `JIRA_ACTIVE_EPIC` | _(none)_ |
| `JIRA_DEFAULT_ISSUE_TYPE` | `Task` |
| `JIRA_LABELS` | `["claude_generated"]` |
| `JIRA_COMPONENTS` | `[]` |
| `JIRA_CONTENT_FORMAT` | `markdown` |
| `JIRA_ACTIVE_SPRINT_ID` | Auto-detect via JQL |

## Flow

### 0. Detect Active Sprint

1. Query: `project = $JIRA_PROJECT_KEY AND sprint in openSprints()` with `maxResults: 1`, `fields: ["customfield_10020"]`
2. Extract sprint ID from `customfield_10020[0].id`
3. If no active sprint, proceed without sprint assignment

Skip if: user says "no sprint" or "backlog".

### 1. Detect Mode

- If input contains `[A-Z]+-[0-9]+` pattern: **update mode** -- fetch issue with `getJiraIssue`
- Otherwise: **create mode**

### 2. Collect Information

For **create mode**, gather from the user (ask only what is missing):
- Summary (clear, imperative, max 100 chars)
- Description (use project template if available)
- Acceptance criteria (testable checkbox items)
- Issue type (default: `$JIRA_DEFAULT_ISSUE_TYPE`)
- Priority (default: Medium)

For **update mode**, ask what fields to change, then apply.

### 3. Create or Update

**Create:** Call `createJiraIssue` with:
- `project`: `$JIRA_PROJECT_KEY`
- `issueType`: `$JIRA_DEFAULT_ISSUE_TYPE`
- `summary`, `description` from collected info
- `parent`: `$JIRA_ACTIVE_EPIC` (if set)
- `additional_fields`: `{ "labels": ["claude_generated"], "components": [...], "customfield_10020": <sprint_id> }`
  - Only include `customfield_10020` if active sprint was detected

**Update:** Call `editJiraIssue` with only the changed fields.

### 4. Confirm

Always reply with the ticket URL: `https://<company>.atlassian.net/browse/<KEY>`

## Rules

- ALWAYS add `claude_generated` label to created issues
- Use `responseContentFormat: "markdown"` for all queries
- Keep `maxResults` low -- field filtering is unimplemented (known bug)
- Never close or transition issues without explicit user approval
- Acceptance criteria must be testable checkboxes, not vague statements
- Auto-add issues to the active sprint unless user says "no sprint" or "backlog"
