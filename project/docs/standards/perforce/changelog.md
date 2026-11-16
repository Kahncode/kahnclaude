# Patch Notes Reference

## Classification

| Category | Use when... | Skip when... |
|----------|-------------|--------------|
| **Features** | New capability players can use or experience | — |
| **Improvements** | Enhancement to existing feature, balance, QoL | — |
| **Fixes** | Bug fix players could have encountered | — |
| _(skip)_ | — | Pure refactor, test-only, CI/build, no gameplay effect |

## CodeSystem Path Mappings

Filter CLs by matching these path patterns:

| System | Path Patterns |
|--------|--------------|
| AI system | `Source/**/AI/`, `Source/**/Bot/`, `Source/**/NPC/` |
| Weapons | `Source/**/Weapon/`, `Source/**/Combat/` |
| Networking | `Source/**/Net/`, `Source/**/Replication/` |
| Inventory | `Source/**/Inventory/`, `Source/**/Item/` |
| UI | `Source/**/UI/`, `Source/**/HUD/`, `Source/**/Widget/` |

Also match system name (case-insensitive) in CL description.

## Transformation Examples

| Technical CL | Player-facing |
|--------------|---------------|
| "Fix AI ignoring cover when under fire" | "Enemies now take cover when you shoot at them" |
| "Add 10m spawn exclusion zone around pawns" | "Enemies no longer spawn right next to you" |
| "Reduce EnemyA HP on Easy" | "Basic enemies are easier on Easy difficulty" |
| "Add footstep audio to NPC movement component" | "You can now hear enemies walking nearby" |
| "Add corner clearance to pathfinding" | "Enemies no longer get stuck on corners" |
| "Show match timer in HUD" | "You can now see how much time is left in a match" |

## Output Format

```markdown
# Patch Notes — <Date Range>

## Features
- <New thing players can do>

## Improvements
- <Enhancement>

## Fixes
- Fixed <bug>
```

Omit empty sections. No CL numbers (too technical for players).

## Output Routing

| Option | Tool | Notes |
|--------|------|-------|
| Done | _(none)_ | Display in conversation |
| Save | Write | Write to `PATCH_NOTES.md` |
| Confluence | `mcp__atlassian__createConfluencePage` | Requires Confluence MCP |
| Jira comment | `mcp__atlassian__addCommentToJiraIssue` | Ask for issue key |
