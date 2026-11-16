---
name: perforce-changelist-description
description: "Changelist description writer. ALWAYS invoke when the user asks to write, update, or generate a CL description. Do not run p4 change directly — this skill enforces [TICKET][Summary] Tech #review format with Jira context."
allowed-tools: Read, Grep, Glob, Bash(p4 describe:*), Bash(p4 opened:*), Bash(p4 change:*), Bash(p4 changes:*), Bash(p4 client:*), Agent, ToolSearch, mcp__atlassian__getJiraIssue
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
p4 changes -s pending --me -c "$(p4 -ztag -F %clientName% info)"
```
(`$P4USER`/`$P4CLIENT` are empty in the shell; the values live in `.p4config`.)

If multiple CLs, ask user which one. If one, confirm it.

## Step 2 -- Analyze Diff via Subagent

**Do NOT read the diff directly.** Spawn a general-purpose agent to analyze it and return a summary.

```
Agent(
  subagent_type: "general-purpose",
  description: "Analyze CL diff for description",
  prompt: """
    Analyze the code changes in Perforce changelist <CL#>.

    Run these commands to get the diff:
    - p4 describe -s <CL#>
    - p4 diff -du //...@=<CL#>

    Return a numbered list of technical changes (MAX 30 items). Use technical jargon appropriate to this UE5 C++ codebase:
    - Be specific: class names, function names, UE5 patterns (GAS, replication, UPROPERTY)
    - Group related changes (e.g., "Added getter/setter for X" not two separate lines)
    - Include: what was added, modified, removed, and why (if inferable)
    - Omit: formatting-only changes, whitespace, include reordering

    Format:
    FILES: <list of affected files, short paths>

    CHANGES:
    1. <technical change>
    2. <technical change>
    ...

    INFERRED PURPOSE: <one sentence summarizing the overall goal>
  """
)
```

The agent returns a concise summary. This keeps the main context lean.

## Step 3 -- Pull Jira Context

Extract ticket ID from any existing CL description or branch name. If found, fetch the Jira ticket via MCP tools for additional context (summary, acceptance criteria, description).

If no ticket is found, use `[NOTICKET]` as the ticket tag and continue; don't ask. (The user answers "no ticket" almost every time.)

## Step 4 -- Generate Description

Combine the agent's technical summary with the Jira context to generate the description.

Use the Jira ticket's user story / acceptance criteria to inform the NON-TECHNICAL summary (the benefit, not the implementation). Use the agent's technical changes list to write the Changes section.

@docs/standards/perforce/perforce-changelist-description.md

## Step 5 -- Apply the Description

Apply the generated description directly (do not ask for approval):

```bash
p4 --field "Description=<description, real newlines allowed>" change -o <CL#> | p4 change -i
```

This replaces the whole Description of an existing CL (a `sed` on `<enter description here>` only matches a brand-new CL and silently changes nothing otherwise). Check with `p4 describe -s <CL#>` that it took.
