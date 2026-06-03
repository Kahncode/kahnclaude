# Tech Stack Guide: Atlassian Jira

<!-- detection: opt-in | signal: jira in README, config, or CI references | prerequisite: none -->
<!-- prompt: "Do you use Jira for issue tracking?" -->

---

## Setup — Environment Variables

Store in `CLAUDE.local.md` (never committed).

### Required

> **Tip:** Just paste any Atlassian URL (e.g., `https://mycompany.atlassian.net/browse/PROJ-123`) and Claude will auto-extract the Cloud ID, project key, and other values.

| Variable | How to Obtain |
|----------|---------------|
| `JIRA_CLOUD_ID` | Paste any `https://<company>.atlassian.net/...` URL — Cloud ID is fetched automatically from `_edge/tenant_info` |
| `JIRA_PROJECT_KEY` | Paste any issue URL (e.g., `https://<company>.atlassian.net/browse/PROJ-123`) — project key is extracted from the issue key |
| `JIRA_ASSIGNEE_ACCOUNT_ID` | Auto-detected via MCP tool `atlassianUserInfo` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `JIRA_ACTIVE_EPIC` | _(none)_ | Key of the currently active epic (e.g., `PROJ-42`) |
| `JIRA_DEFAULT_ISSUE_TYPE` | `Task` | Default issue type for new issues |
| `JIRA_CONTENT_FORMAT` | `markdown` | Content format for descriptions (`markdown` or `adf`) |
| `JIRA_COMPONENTS` | `[]` | Default component(s) to assign to new issues |
| `JIRA_LABELS` | `["claude_generated"]` | Labels to apply to all Claude-created issues |
| `JIRA_ACTIVE_SPRINT_ID` | _(auto-detect)_ | ID of the currently active sprint |

---

## Setup — Auto-Detection + Confirmation

Most configuration is auto-detected via MCP. Only the active epic requires user input when multiple are found.

| Step | Method | CLAUDE.md Section |
|------|--------|-------------------|
| 1. Detect project | `getVisibleJiraProjects` MCP — list and let user pick | Service Ports |
| 2. Detect hierarchy | `getJiraProjectIssueTypesMetadata` MCP — infer from available types | Project Rules |
| 3. Detect transitions | `getTransitionsForJiraIssue` on any existing issue — discover IDs | Project Rules |
| 4. Detect components | JQL: `project = <KEY> AND component IS NOT EMPTY ORDER BY updated DESC` | Project Rules |

### Question (ask only if ambiguous) — multi-choice

When multiple in-progress epics are found via JQL `project = <KEY> AND issuetype = Epic AND status = "In Progress"`, present as a multi-choice selection (one choice only):

```
Multiple active epics found — select one:

  ( ) PROJ-42 — Sprint 12: Player Systems
  ( ) PROJ-78 — Sprint 12: World Building
  ( ) None — skip epic assignment
```

Populate options dynamically from the JQL results. Maps to **Service Ports** in CLAUDE.md.

### Defaults (no question needed)

- Always add `claude_generated` label to Claude-created issues
- Never close issues without user approval

---

## Operational Reference — Jira

### After Creating an Issue
Always reply with the link to the newly created ticket: `webUrl` from the response (e.g. `https://<COMPANY>.atlassian.net/browse/<PROJECT>-XXXXX`)

### Issue Hierarchy

Configure your issue hierarchy based on your project structure:

- **Initiative**: Top-level epic or initiative for your team's work
  - **Epics** represent a time-scoped workblock (Start Date -> Due Date). New tasks must be parented to the currently active epic.
  - **Tasks/Bugs** are children of the active epic — set via `parent` field

To find the current active epic:
```
parent = <INITIATIVE_KEY> AND issuetype = Epic AND status = "In Progress"
```

### Defaults

Configure these values in your CLAUDE.md or CLAUDE.local.md:

```
JIRA_CLOUD_ID: <your-cloud-id-uuid>
JIRA_PROJECT_KEY: <PROJECT>
JIRA_ASSIGNEE_ACCOUNT_ID: <your-account-id>
JIRA_ACTIVE_EPIC: <EPIC-KEY>
JIRA_DEFAULT_ISSUE_TYPE: Task
JIRA_CONTENT_FORMAT: markdown
JIRA_COMPONENTS: []
JIRA_LABELS: ["claude_generated"]
```

### Issue Fields
- **Component**: Set `additional_fields: { "components": [{ "name": "<ComponentName>" }] }`
- **Label**: Always add `claude_generated` to any issue created through Claude — set `additional_fields: { "labels": ["claude_generated"] }`
- When both apply, combine them: `additional_fields: { "components": [...], "labels": [...] }`

### Sprints

Sprint field: `customfield_10020` (standard Jira Cloud custom field).

**Detect active sprint:**
```
project = <KEY> AND sprint in openSprints()
```
Query with `maxResults: 1`, `fields: ["customfield_10020"]`. Extract from `customfield_10020[0]`:
- `id` — numeric sprint ID (use when setting)
- `name` — e.g., "13th April - 27th April 2026"
- `state` — "active" | "closed" | "future"

**Assign sprint:**
```
additional_fields: { "customfield_10020": <sprint_id> }
```

**Requirement:** Tasks in "In Progress" should be assigned to the active sprint. The `task-implementation` skill prompts for sprint assignment when starting work.

### Transitions
Use `transitionJiraIssue` with the transition `id`. Common global transitions:

| ID | Name | -> Status |
|----|------|-----------|
| 11 | To Do | Backlog |
| 21 | In Progress | In Progress |
| 31 | Done | Done |
| 41 | All | Blocked |
| 51 | Review Required | Review Required |

Note: Transition IDs vary by project. Use `getTransitionsForJiraIssue` to get available transitions for a specific issue.

### Saved Filters

Configure team-specific saved filters in CLAUDE.md for quick access.

### Query Defaults
- `responseContentFormat`: always `"markdown"` (never `"adf"`)
- `maxResults`: keep as low as needed — the `fields` parameter is **not respected** by the MCP server (full payload always returned), so tight JQL and low maxResults are the only real cost levers
- **Known bug**: [atlassian-mcp-server#17](https://github.com/atlassian/atlassian-mcp-server/issues/17) — fields filtering unimplemented, Atlassian acknowledged Feb 2026, no fix yet. Single issues can be 80k+ chars.

### External Documentation

- **Jira Cloud REST API v3**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
  - Use WebFetch to look up endpoints, parameters, and response formats when the info above is insufficient.
