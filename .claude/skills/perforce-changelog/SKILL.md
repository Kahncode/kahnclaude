---
name: perforce-changelog
description: "Perforce changelog → player-facing patch notes. ALWAYS invoke when the user asks for a changelog, patch notes, release notes, or recent changes summary. Transforms technical CL descriptions into conversational player-friendly language."
allowed-tools: Bash(p4 *), Read, Grep, Glob, mcp__atlassian__createConfluencePage, mcp__atlassian__addCommentToJiraIssue, AskUserQuestion
---

# P4 Changelog → Patch Notes

**Input:** $ARGUMENTS

Generates **player-facing patch notes** from Perforce history. Transforms technical CL descriptions into conversational language focused on gameplay impact.

## Flow

### 1. Parse Arguments

Optional arguments from `$ARGUMENTS`:

| Arg | Default | Example |
|-----|---------|---------|
| days | 7 | `14` |
| user | current P4 user | `jsmith` |
| system | all | `"AI system"` |

### 2. Fetch Changelists

```bash
p4 changes -s submitted -u <user> -l @<YYYY/MM/DD>,@now
```

For each CL, get details with `p4 describe -s <CL>`.

### 3. Filter and Transform

For each CL:

1. **Skip internal-only changes** — pure refactors, test-only, CI/build, code cleanup with no gameplay effect
2. **Classify** into: Features | Improvements | Fixes
3. **Rewrite** the description into player-facing language

#### Classification Rules

| Category | Use when... |
|----------|-------------|
| **Features** | New capability players can use or experience (new system, new content, new mode) |
| **Improvements** | Enhancement to existing feature (balance, UX, polish, quality-of-life) |
| **Fixes** | Bug fix that players could have encountered |

#### Rewriting Rules

Transform technical descriptions into player-facing language.

### 4. Generate Patch Notes

```markdown
# Patch Notes — <Date Range>

## Features
- <New thing players can do>

## Improvements
- <Enhancement to existing feature>
- <Another improvement>

## Fixes
- Fixed <bug description>
- Fixed <another bug>
```

Omit empty sections. No CL numbers in the output (too technical).

### 5. Output Routing

Present the patch notes, then ask:

> What would you like to do with these patch notes?
> 1. **Done** — just show it here
> 2. **Save** — write to `PATCH_NOTES.md`
> 3. **Confluence** — post as a Confluence page
> 4. **Jira comment** — add as a comment on a Jira issue
