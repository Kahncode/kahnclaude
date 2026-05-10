---
name: perforce-resolve-diff
description: "Perforce diff resolver. ALWAYS invoke when any skill or user needs a diff from a CL number, file, folder, system name, or Swarm review. Do not run p4 diff or p4 describe directly — this is the ONLY skill with P4 diff knowledge."
allowed-tools: Read, Grep, Glob, Bash(p4 diff:*), Bash(p4 describe:*), Bash(p4 opened:*), Bash(p4 changes:*), Bash(p4 client:*)
---

# Resolve Diff

@docs/standards/perforce/resolve-diff.md

**Input:** $ARGUMENTS

## Instructions

Resolve the review target using the priority order below. Stop at the first match.

### Priority 1 — Changelist Number
If `$ARGUMENTS` is all digits: run `p4 describe -du $ARGUMENTS`.

### Priority 2 — Swarm Review URL or ID
If `$ARGUMENTS` contains `reviews/` or starts with `r` followed by digits:
- Extract the review ID from the URL or `rNNNN` pattern
- Run `p4 describe -du <CL>` using the CL associated with that review

### Priority 3 — File Path
If `$ARGUMENTS` is a path to an existing file:
- Run `p4 diff -du "$ARGUMENTS"` for pending changes
- If no diff, read the file contents as the review target

### Priority 4 — Folder Path
If `$ARGUMENTS` is a path to an existing directory:
- Run `p4 diff -du "$ARGUMENTS/..."` for pending changes under that folder
- If no diff, list and summarize files in the folder

### Priority 5 — System or Module Name
If `$ARGUMENTS` is a non-path string (not digits, not a file/folder):
- Use Grep/Glob to find files related to that system name
- Run `p4 diff -du` and filter to matching files

### Priority 6 — Auto-Detect (no arguments)
If `$ARGUMENTS` is empty:
1. `p4 opened` — if files are opened, run `p4 diff -du`
2. `p4 changes -s pending -u $P4USER -c $P4CLIENT -m 1` — describe the latest pending CL
3. If nothing found, report no changes

## Output

Return the resolved diff content plus metadata:
- **Source**: how the diff was resolved (CL#, file, auto-detect, etc.)
- **Stream**: run `p4 client -o | grep "^Stream:" | awk '{print $2}'`
- **Mainline warning**: if the stream path contains `/main` or `/mainline`, warn prominently
- **Diff content**: the full unified diff text
