---
name: perforce-get-latest
description: "Perforce sync expert. ALWAYS invoke when the user asks to get latest, sync, p4 sync, or update their workspace. Do not run p4 sync directly — this skill does dry-run preview, conflict detection, and guided resolution by file type."
---

# Sync Latest

Use PROACTIVELY when user says `get latest`, `sync latest`, `p4 sync`, or asks to update their workspace.

**Input:** $ARGUMENTS (optional -- CL number, `@latest`, or path filter)

## Reference

- @docs/standards/perforce/get-latest.md -- sync workflow, conflict resolution
- @project/docs/tech-stacks/helix_perforce.md -- full Perforce operational guide

## allowed-tools

Read, Grep, Glob, Bash(p4 sync:*), Bash(p4 reconcile:*), Bash(p4 opened:*), Bash(p4 client:*), Bash(p4 changes:*)

## Step 1 -- Check Open Files

```bash
p4 opened
```

If files are opened, warn the user with the list and CL numbers. The user is responsible for handling open file conflicts -- do NOT auto-shelve. Just inform and proceed if they confirm.

## Step 2 -- Dry-Run Preview

```bash
p4 sync -n ...
```

Summarize: total files, adds/updates/deletes, potential conflicts with opened files. If >500 files, warn and suggest a targeted sync by path.

Ask user to confirm before proceeding.

## Step 3 -- Execute Sync

Based on arguments or default to latest:

```bash
p4 sync              # latest
p4 sync @<CL>        # specific CL
p4 sync //path/...   # specific path
```

## Step 4 -- Resolve Conflicts

```bash
p4 resolve -n
```

If conflicts exist, guide by file type:

- **Binary files** (.uasset, .umap, images, audio): Never merge. Ask user to accept theirs (`-at`) or yours (`-ay`).
- **Text files** (.h, .cpp, .cs, .ini): Offer auto-merge (`-am`), accept theirs (`-at`), or accept yours (`-ay`). Analyze both versions if complex.

## Step 5 -- Report

```
Sync complete:
- Files updated: N
- Conflicts resolved: N (M auto-merged, K manual)
- Files still needing resolution: N
- Workspace is now at CL#XXXXX
```
