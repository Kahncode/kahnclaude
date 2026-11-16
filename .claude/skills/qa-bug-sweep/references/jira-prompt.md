# Jira check prompt (one agent for all bugs)

Send this as a `general-purpose` agent prompt.

---

Read-only Jira lookup. **Don't create, edit, comment on, or transition any
issue.**

Cloud ID `{{JIRA_CLOUD_ID}}`, project `{{JIRA_PROJECT_KEY}}`. Use
`mcp__atlassian__searchJiraIssuesUsingJql` (load it with ToolSearch first).

For each bug below, run 1–3 JQL text searches using the player-visible keywords
from the title (e.g. `project = {{JIRA_PROJECT_KEY}} AND text ~ "door open sound missing" ORDER BY
updated DESC`), plus the {{JIRA_PROJECT_KEY}} keys in the causing CL's description. Read the
summaries of the top results.

{for each bug: "<id> | <title> | CL <n> | CL's {{JIRA_PROJECT_KEY}} keys: <keys or none>"}

Return one line per bug:

```
<id>: new | ticketed {{JIRA_PROJECT_KEY}}-n | regressed {{JIRA_PROJECT_KEY}}-n | related {{JIRA_PROJECT_KEY}}-n[, {{JIRA_PROJECT_KEY}}-m] — <≤12-word note>
```

- `ticketed`: an open ticket describes this same symptom.
- `regressed`: a Done/closed ticket describes this symptom, so it's back.
- `related`: only the causing CL's own ticket or a nearby report matches.
- `new`: nothing matches.
