---
name: kc-update
description: Update KahnClaude components in the current project to the latest versions
scope: framework
---

Update KahnClaude components in the current working directory from the framework source.

## Steps

1. Identify the KahnClaude source directory (ask the user if not already known)
2. For each component category (`commands/`, `skills/`, `agents/`, `hooks/`):
   - Compare source files to installed files
   - Show a summary: new files, changed files, removed files
3. Ask the user to confirm before applying changes
4. For changed files: show a diff, ask whether to update each one (or confirm all)
5. Copy updated/new files, skip unchanged files
6. Report a summary of what was updated

## Notes

- Never delete files that exist in the project but not in the framework (user may have added custom components)
- Never overwrite `CLAUDE.md` or `CLAUDE.local.md` (these are project-specific)
- Always show diffs before applying changes
