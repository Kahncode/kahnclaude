---
name: perforce-changelist-description
description: "Changelist description writer. ALWAYS invoke when the user asks to write, update, or generate a CL description. Do not run p4 change directly — this skill enforces [TICKET][Summary] Tech #review format with Jira context."
allowed-tools: Read, Grep, Glob, Bash(p4 diff:*), Bash(p4 describe:*), Bash(p4 opened:*), Bash(p4 change:*), Bash(p4 changes:*), Bash(p4 client:*), ToolSearch, mcp__atlassian__getJiraIssue
---

# Write Changelist Description

Use PROACTIVELY when user says `write cl description`, `write changelist description`, `update cl description`, or asks to describe a changelist.

**Input:** $ARGUMENTS (optional -- CL number)

## Reference

- @docs/standards/perforce/perforce-changelist-description.md -- CL format, validation rules, stream discipline

## Step 1 -- Resolve Changelist

Resolve the CL in this order:

1. **Argument:** If CL number is in $ARGUMENTS, use it directly
2. **Context:** Scan the conversation for recently mentioned CL numbers (patterns: `CL 12345`, `CL#12345`, `changelist 12345`, `CL:12345`, `review 12345`). If found, confirm with user: "I see CL <number> mentioned — use that?"
3. **Query P4:** If not found above, run:

```bash
p4 changes -s pending -u $P4USER -c $P4CLIENT
```

If multiple CLs, ask user which one. If one, confirm it.

## Step 2 -- Read the Diff

```bash
p4 describe -s <CL#>
p4 diff -du //...@=<CL#>
```

Analyze the changes: what files changed, what code was added/modified/removed, and why.

## Step 3 -- Pull Jira Context

Extract ticket ID from any existing CL description or branch name. If found, fetch the Jira ticket via MCP tools for additional context (summary, acceptance criteria, description).

If no ticket is found, ask the user for one. Every CL MUST have a Jira ticket.

## Step 4 -- Generate Description

Generate the changelist description. @docs/standards/perforce/perforce-changelist-description.md

## Step 5 -- Apply the Description

Apply the generated description directly (do not ask for approval):

```bash
p4 change -o <CL#> | sed "s/\t<enter description here>/<description>/" | p4 change -i
```

Or use `p4 change -o` to get the spec, replace the description field, and pipe back via `p4 change -i`.
