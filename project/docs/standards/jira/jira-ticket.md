# Jira Ticket Reference

Extracted from @project/docs/tech-stacks/atlassian_jira.md -- do not edit directly.

---

## Issue Hierarchy

- **Initiative**: Top-level epic or initiative
  - **Epics**: Time-scoped workblock (Start Date -> Due Date). New tasks must be parented to the active epic.
  - **Tasks/Bugs**: Children of the active epic -- set via `parent` field

Find the current active epic:
```
parent = <INITIATIVE_KEY> AND issuetype = Epic AND status = "In Progress"
```

## Issue Fields

| Field | How to Set |
|-------|-----------|
| Component | `additional_fields: { "components": [{ "name": "<Name>" }] }` |
| Label | `additional_fields: { "labels": ["claude_generated"] }` |
| Sprint | `additional_fields: { "customfield_10020": <sprint_id> }` |
| Combined | `additional_fields: { "components": [...], "labels": [...], "customfield_10020": ... }` |

### Sprint Detection

To auto-detect the active sprint:
1. Query: `project = $KEY AND sprint in openSprints()` with `maxResults: 1`, `fields: ["customfield_10020"]`
2. Extract sprint ID from `customfield_10020[0].id`
3. If no active sprint found, omit the field (issue goes to backlog)

## Transitions

Use `transitionJiraIssue` with the transition `id`. Common global transitions:

| ID | Name | -> Status |
|----|------|-----------|
| 11 | To Do | Backlog |
| 21 | In Progress | In Progress |
| 31 | Done | Done |
| 41 | All | Blocked |
| 51 | Review Required | Review Required |

Note: IDs vary by project. Use `getTransitionsForJiraIssue` to get actual values.

## Description Format Template

```markdown
## Context

[Why is this work needed? What problem does it solve?]

## Task

[Specific work to be done. Keep it focused and scope-bounded.]

## Acceptance Criteria

- [ ] Criterion 1 -- specific, testable, measurable
- [ ] Criterion 2

## Out of Scope

[What should NOT be included in this issue?]
```

## Acceptance Criteria Patterns

Good criteria are:
- **Specific**: "User can toggle dark mode from Settings > Display"
- **Testable**: "API returns 200 with valid JSON body containing `id` field"
- **Measurable**: "Page load time under 2s on 3G connection"

Bad criteria:
- "Make it better" (vague)
- "Should work correctly" (untestable)
- "Improve performance" (unmeasurable)

## Query Defaults

- `responseContentFormat`: always `"markdown"`
- `maxResults`: keep low -- `fields` param is NOT respected by MCP server (known bug, full payload always returned)
- Single issues can be 80k+ chars

## Auto-Detection Steps

| Step | MCP Method |
|------|-----------|
| Detect project | `getVisibleJiraProjects` |
| Detect hierarchy | `getJiraProjectIssueTypesMetadata` |
| Detect transitions | `getTransitionsForJiraIssue` on any existing issue |
| Detect components | JQL: `project = <KEY> AND component IS NOT EMPTY ORDER BY updated DESC` |

## External Reference

- Jira Cloud REST API v3: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
