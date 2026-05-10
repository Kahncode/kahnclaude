---
description: Update project documentation from new knowledge. Accepts a P4 changelist number, CL range, a plain-text fact or decision, or no args to auto-detect from opened/pending/last submit.
scope: project
argument-hint: [CL# | CL#,CL# | message]
---

# Learn

Update project documentation based on what changed or what was learned.

**Source:** $ARGUMENTS

## Source Resolution

Resolve the source in this priority order:

### 1. Changelist number or range — `/learn <CL#>` or `/learn <CL1>,<CL2>`

If `$ARGUMENTS` looks like a changelist number (all digits) or a comma-separated pair of CL numbers:
- Run `p4 describe -du <CL#>` to get the diff for a single CL
- For a range, run `p4 describe -du <CL>` for each CL in the range
- Include the CL number(s) in any Decisions log entries

### 2. Plain-text fact or decision — `/learn <message>`

If `$ARGUMENTS` is a human-readable statement (not a CL number):
- Treat it as a fact or decision to incorporate into docs
- If it conflicts with existing documentation, surface the conflict and ask the user to resolve it before writing

### 3. No arguments — Auto-detect

Check in order:
1. **Opened files** — `p4 diff`: if any diffs exist, use those
2. **Pending changelists** — `p4 changes -s pending -u $P4USER -c $P4CLIENT`: if any exist, describe the most recent
3. **Last submitted change** — `p4 changes -m 1 -u $P4USER -s submitted`: fallback if nothing is opened or pending

## Behavior

After resolving the source:

1. Identify which parts of the codebase changed or which facts are new
2. Determine which documentation files are affected
3. **Ask the user to confirm before writing significant changes** (more than a few lines)
4. Update only the docs relevant to what changed — do not rewrite unrelated sections
5. Append a Decisions entry for non-trivial changes, facts, or tech choices
6. Scan changelist descriptions for decision-worthy changes (non-trivial refactors, tech choices, removals)

## Delegation

**ALWAYS** delegate to the `documenter` agent via the Agent tool. Do not handle documentation updates inline — even if other work (code fixes, memory saves) is also requested.

Pass to the agent:

- The resolved diff, changelist description, or plain-text fact as context
- The source type and any CL number(s) for Decisions log entries
- Instruction: "Update only the docs relevant to what changed. Ask the user before writing significant changes. Append Decisions entries where appropriate. Target project files (CLAUDE.md, docs/*.md, README.md) — auto-memory files are not a substitute."
