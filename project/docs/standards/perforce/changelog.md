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
| "Fix AI patrol logic not respecting threat radius" | "Cops no longer attack players defending themselves" |
| "Add 10m spawn exclusion zone around pawns" | "We now avoid spawning bots too close to players (10m)" |
| "Reduce Gunner HP 80→60 in Dungeon_A, disable sprint" | "Lowered the difficulty of Gunners in Dungeon_A" |
| "Implement play-dead detection in AIController" | "Playing dead will cause Rats to lose interest in you" |
| "Add corner clearance to pathfinding" | "Bots no longer collide with walls when turning corners" |
| "Hook up God PA system to bot waves events" | "Added God announcement to bot wave events" |

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
