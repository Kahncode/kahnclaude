---
name: swarm-review-shelve
description: "Perforce shelve + Swarm review. ALWAYS invoke when the user asks to shelve, checkpoint, save progress, or create a Swarm review. Resolves the active CL, writes the description, shelves, and reports the Swarm URL if #review is present."
---

# Shelve & Swarm Changelist

Use PROACTIVELY when user says `shelve`, `checkpoint`, `shelve for review`, `create swarm review`, `shelve progress`, or when another skill needs to save progress.

**Input:** $ARGUMENTS (optional -- CL number)

## Reference

- @docs/standards/swarm/swarm-review-shelve.md -- shelve commands, CL resolution, Swarm URL patterns

## allowed-tools

Read, Grep, Glob, Bash(p4 shelve:*), Bash(p4 describe:*), Bash(p4 changes:*), Bash(p4 opened:*), Bash(p4 change:*), Bash(p4 client:*), Bash(p4 diff:*)

## Step 1 -- Resolve Active CL

Resolve the CL in this order:

1. **Argument:** If CL number is in $ARGUMENTS, use it directly
2. **Context:** Scan the conversation for recently mentioned CL numbers (patterns: `CL 12345`, `CL#12345`, `changelist 12345`, `CL:12345`, `review 12345`). If found, confirm with user: "I see CL <number> mentioned — use that?"
3. **Query P4:** If not found above, detect the active CL:

```bash
p4 changes -s pending --me -c "$(p4 -ztag -F %clientName% info)"
```

The default changelist holds the user's unrelated work in this shared workspace: never shelve or move it.

If multiple pending CLs, ask which one to shelve.

## Step 2 -- Write CL Description

**Invoke the `perforce-changelist-description` skill.** The CL description must be finalized before shelving because Swarm uses it as the review description.

**Skip this step if:** the caller explicitly requests a quick checkpoint, or the CL already has a properly formatted description (with `[TICKET]`, `[summary]`, and `#review`). If skipping, confirm with the user.

## Step 3 -- Shelve

**First list what will be shelved** (parallel sessions move files between CLs, so files from an unrelated CL can end up in this one):

```bash
p4 opened -c <CL#>
```

Show the list. **Stop and ask** if any file is one the work didn't name, a binary (`.uasset`/`.umap` excepted when the work is content), a `Binaries/` file, a local-only path (`{{LOCAL_ONLY_PATHS}}`), or holds a secret (`p4 diff -du` on opened `.ini`/config files: look for `Token=`, `Key=`, `Password=`, `ATATT`, `Bearer`). Otherwise shelve:

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
- Swarm: `<SWARM_URL>/changes/<CL#>` (the change page links its review; review IDs differ from CL numbers, e.g. CL 1000 → review 1012)
- Reminder: assign reviewers in Swarm (no auto-assignment)

Determine the Swarm URL from .claude/rules/project-vars.md (`SWARM_URL`), or `p4 property -l -n P4.Swarm.URL`. If not found, ask the user.

## Integration

This skill is invoked by other skills (e.g., `task-implementation` after code-dev or blueprint-dev completes). When called programmatically for a quick checkpoint, skip Step 2 and shelve directly.

## Rules

- **Never run `p4 submit`** -- submitting is the user's responsibility
- Do not assign reviewers -- the user handles that in Swarm
- The `#review` tag in the description triggers Swarm to create the review automatically
- Do not shelve local-only paths (`{{LOCAL_ONLY_PATHS}}`)
