---
description: Update project documentation from new knowledge. Accepts a git SHA, SHA range, a plain-text fact or decision, or no args to auto-detect from staged/unstaged/last commit.
scope: project
argument-hint: [sha | sha1..sha2 | message]
---

# Learn

Update project documentation based on what changed or what was learned.

**Source:** $ARGUMENTS

## Source Resolution

Resolve the source in this priority order:

### 1. Git SHA or range — `/learn <sha>` or `/learn <sha1>..<sha2>`

If `$ARGUMENTS` looks like a commit SHA (7–40 hex chars) or a `sha1..sha2` range:
- Run `git show <sha>` or `git log --patch <sha1>..<sha2>` to get the diff
- Include the SHA(s) in any Decisions log entries

### 2. Plain-text fact or decision — `/learn <message>`

If `$ARGUMENTS` is a human-readable statement (not a SHA):
- Treat it as a fact or decision to incorporate into docs
- If it conflicts with existing documentation, surface the conflict and ask the user to resolve it before writing

### 3. No arguments — Auto-detect

Check in order:
1. **Staged changes** — `git diff --cached`: if any exist, use those
2. **Unstaged changes** — `git diff`: if any exist, use those
3. **Last commit** — `git log -1 --patch`: fallback if the working tree is clean

## Behavior

After resolving the source:

1. Identify which parts of the codebase changed or which facts are new
2. Determine which documentation files are affected
3. **Ask the user to confirm before writing significant changes** (more than a few lines)
4. Update only the docs relevant to what changed — do not rewrite unrelated sections
5. Append a Decisions entry for non-trivial changes, facts, or tech choices
6. Scan commit messages for decision-worthy changes (non-trivial refactors, tech choices, removals)

## Delegation

Delegate to the `documenter` agent via the Agent tool, passing:

- The resolved diff, commit range, or plain-text fact as context
- The source type and any SHA(s) for Decisions log entries
- Instruction: "Update only the docs relevant to what changed. Ask the user before writing significant changes. Append Decisions entries where appropriate."
