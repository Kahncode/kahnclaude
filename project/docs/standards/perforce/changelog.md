# Changelog Reference

## Commit-Type Classification

Classify each CL by scanning the description for these keywords:

| Type | Keywords |
|------|----------|
| **feat** | add, implement, new, create |
| **fix** | fix, bug, patch, resolve, hotfix |
| **refactor** | refactor, cleanup, extract, reorganize |
| **perf** | optimize, performance, cache, speed |
| **docs** | doc, readme, comment |
| **test** | test, spec, coverage |
| **chore** | everything else |

## CodeSystem Path Mappings

When filtering by CodeSystem, match these path patterns in the CL file list:

| System | Path Patterns |
|--------|--------------|
| AI system | `Source/**/AI/`, `Source/**/Bot/`, `Source/**/NPC/` |
| Weapons | `Source/**/Weapon/`, `Source/**/Combat/` |
| Networking | `Source/**/Net/`, `Source/**/Replication/` |
| Inventory | `Source/**/Inventory/`, `Source/**/Item/` |
| UI | `Source/**/UI/`, `Source/**/HUD/`, `Source/**/Widget/` |

Also match the system name (case-insensitive) against CL description text as a fallback.

## Output Format

```markdown
# Changelog — <User> (<StartDate> to <EndDate>)

## Features
- **<Module>**: <Summary> (CL#12345) — YYYY-MM-DD

## Bug Fixes
- **<Module>**: <Summary> (CL#12346) — YYYY-MM-DD

## Refactors
- **<Module>**: <Summary> (CL#12348) — YYYY-MM-DD

## Performance
- **<Module>**: <Summary> (CL#12349) — YYYY-MM-DD

## Other
- <Summary> (CL#12350) — YYYY-MM-DD

---
Total: N changelists | Date range: YYYY-MM-DD to YYYY-MM-DD
```

Omit sections with no entries.

## Output Routing

| Option | Tool | Notes |
|--------|------|-------|
| Done | _(none)_ | Display in conversation only |
| Save | Write | Write to `CHANGELOG.md` in project root |
| Confluence | `mcp__claude_ai_Atlassian__createConfluencePage` | Requires Confluence MCP configured |
| Jira comment | `mcp__claude_ai_Atlassian__addCommentToJiraIssue` | Ask for issue key first |
