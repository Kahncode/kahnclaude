---
name: swarm-review-shelve
description: "Perforce shelve + Swarm review. ALWAYS invoke when the user asks to shelve, checkpoint, save progress, or create a Swarm review. Resolves the active CL, writes the description, shelves, and reports the Swarm URL if #review is present."
---

# Shelve & Swarm Changelist

Use PROACTIVELY when user says `shelve`, `checkpoint`, `shelve for review`, `create swarm review`, `shelve progress`, or when another skill needs to save progress (e.g., after a successful build).

**Input:** $ARGUMENTS (optional -- CL number)

## Reference

- @project/docs/standards/swarm/swarm-review-shelve.md -- shelve commands, CL resolution, Swarm URL patterns

## allowed-tools

Read, Grep, Glob, Bash(p4 shelve:*), Bash(p4 describe:*), Bash(p4 changes:*), Bash(p4 opened:*), Bash(p4 change:*), Bash(p4 client:*), Bash(p4 diff:*)

## Step 1 -- Resolve Active CL

Resolve the CL in this order:

1. **Argument:** If CL number is in $ARGUMENTS, use it directly
2. **Context:** Scan the conversation for recently mentioned CL numbers (patterns: `CL 12345`, `CL#12345`, `changelist 12345`, `CL:12345`, `review 12345`). If found, confirm with user: "I see CL <number> mentioned — use that?"
3. **Query P4:** If not found above, detect the active CL:

```bash
p4 opened -c default
p4 changes -s pending -u $P4USER -c $P4CLIENT
```

If files are in the default changelist, warn the user and ask them to move files to a numbered CL first.

If multiple pending CLs, ask which one to shelve.

## Step 2 -- Write CL Description

**Invoke the `perforce-changelist-description` skill.** The CL description must be finalized before shelving because Swarm uses it as the review description.

**Skip this step if:** the caller explicitly requests a quick checkpoint (e.g., programmatic invocation from `unreal-project-compilation`), or the CL already has a properly formatted description (with `[TICKET]`, `[summary]`, and `#review`). If skipping, confirm with the user.

## Step 3 -- Shelve

```bash
p4 shelve -c <CL#>
```

If already shelved, force-update:

```bash
p4 shelve -f -c <CL#>
```

## Step 4 -- Report

Read the CL description to check for `#review`:

```bash
p4 describe -s <CL#>
```

**Always report:**
- CL number shelved
- Number of files in the shelf
- Timestamp of the checkpoint

**If `#review` is in the description, also report:**
- Swarm review URL: `$SWARM_URL/reviews/<CL#>`
- Reminder: assign reviewers in Swarm (no auto-assignment)

Determine the Swarm URL from `SWARM_URL` env var or `p4 property -l -n P4.Swarm.URL`. If neither found, ask the user.

## Integration

This skill is invoked by other skills (e.g., `unreal-project-compilation` on successful build, `task-implementation` after code-dev or blueprint-dev completes). When called programmatically for a quick checkpoint, skip Step 2 and shelve directly.

## Rules

- **Never run `p4 submit`** -- submitting is the user's responsibility
- Do not assign reviewers -- the user handles that in Swarm
- The `#review` tag in the description triggers Swarm to create the review automatically
- Do not shelve `.claude/`, `CLAUDE.local.md`, or `.env` files
