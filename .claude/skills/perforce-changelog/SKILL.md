---
name: perforce-changelog
description: "Perforce changelog generator. ALWAYS invoke when the user asks for a changelog, commit history, or recent changes summary. Do not run p4 changes directly — this skill classifies by type, groups by module, and routes to Confluence/Jira."
allowed-tools: Bash(p4 *), Read, Grep, Glob, mcp__claude_ai_Atlassian__createConfluencePage, mcp__claude_ai_Atlassian__addCommentToJiraIssue, AskUserQuestion
---

# P4 Changelog

**Input:** $ARGUMENTS

## Tech-Stack Context

Load if it exists in the project:
- `@docs/tech-stacks/helix_perforce.md` — P4 CLI workflow, changelist conventions, stream paths

## Reference

See @docs/standards/perforce/changelog.md for commit-type classification, CodeSystem path mappings, and output format.

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `P4USER` | Perforce username (fallback: `p4 set P4USER` or `p4 info`) |
| `P4CLIENT` | Perforce workspace |

## Flow

### 1. Parse Arguments

Parse up to 3 optional arguments from `$ARGUMENTS`:

1. **days** — Number of days to look back (default: 7)
2. **user** — P4 username (default: current user via `p4 set P4USER` or `p4 info`)
3. **CodeSystem** — Module name filter (e.g. "AI system", "Weapons"). If omitted: all systems.

Examples:
- `7` — last 7 days, current user, all systems
- `30 jsmith` — last 30 days, user jsmith, all systems
- `30 jsmith "inventory system"` — last 30 days, user jsmith, inventory system

### 2. Fetch Changelists

```bash
p4 changes -s submitted -u <user> -l @<YYYY/MM/DD>,@now
```

Calculate start date: today minus `days` in `YYYY/MM/DD` format.

If **CodeSystem** is provided, fetch file lists per CL and filter by relevant paths (see reference.md for mappings), or match the system name against CL description text.

### 3. Classify and Group

For each CL, extract: CL number, date, description (first line = summary), files changed (`p4 describe -s <CL>`).

Classify by conventional commit type using description keywords (see reference.md). Group by module/component based on the primary path changed.

### 4. Generate Changelog

Format as markdown with sections: Features, Bug Fixes, Refactors, Performance, Docs, Tests, Other. Include CL numbers and dates. Add a total/date-range summary line.

### 5. Output Routing

Present the changelog, then ask:

> What would you like to do with this changelog?
> 1. **Done** — just show it here
> 2. **Save** — write to `CHANGELOG.md` in the project
> 3. **Confluence** — post as a Confluence page
> 4. **Jira comment** — add as a comment on a Jira issue
