---
name: update
description: Update KahnClaude components in the current project to the latest versions
scope: framework
---

Update KahnClaude components in the current working directory from the framework source.

## Steps

1. **Read the install manifest** from `.claude/.kahnclaude`. If it does not exist, tell the user to run `/kc:install` first and stop.

2. **Resolve the KahnClaude source directory** from `manifest.source`. If the path no longer exists, ask the user for the current KahnClaude path and update `manifest.source` before continuing.

3. **Compute the diff scope**: run `git diff --name-only <manifest.commit>..HEAD` in the KahnClaude source directory to get the list of files changed since the last install/update. Only files in this diff are candidates for update — do not touch components that haven't changed.

4. **Get the current commit hash**: run `git rev-parse HEAD` in the KahnClaude source directory.

5. **Filter changed files by category** and determine what needs updating:

   - `commands/` files (excluding `scope: framework` commands) → candidates for `<target>/.claude/commands/`
   - `skills/` files → candidates for `<target>/.claude/skills/`
   - `agents/` files **that are listed in `manifest.agents`** → candidates for `<target>/.claude/agents/`
   - `hooks/` files → candidates for `<target>/.claude/hooks/`
   - `project/CLAUDE.md` or `project/CLAUDE.local.md` → skip (never overwrite)

   Ignore changed files outside these categories (e.g. `global/`, `inspiration/`, `README.md`).

6. **Check for new agents** in the diff (added agent files not currently in `manifest.agents`):
   - Group new agents by subfolder and present them to the user, asking which to add
   - Use `AskUserQuestion` for groups of ≤ 4; plain text description for larger groups
   - Add user-selected new agents to the candidate update list and to `manifest.agents`

7. **Show a summary** of candidates: new files, changed files, and any files in the diff that are not installed (skipped). Ask the user to confirm before applying.

8. **For each changed file that is installed**, show a diff and ask whether to update, skip, or merge. Offer a "confirm all" shortcut if there are many files.

9. **Apply updates**: copy confirmed files to the target, preserving subfolder structure. Create any needed subdirectories.

10. **Update the manifest** at `.claude/.kahnclaude`:
    - Set `commit` to the current KahnClaude commit hash
    - Set `installed_at` to the current ISO-8601 timestamp
    - Update `agents` to reflect any newly added agents
    - Append to `notes`: a one-line entry summarizing what was updated (e.g. `"2026-03-10: updated 3 commands, added react agent"`)

11. Report a summary of what was updated, what was skipped, and what new agents were added.

## Notes

- Never delete files that exist in the project but not in the framework (user may have added custom components)
- Never overwrite `CLAUDE.md` or `CLAUDE.local.md` (these are project-specific)
- Only update files that changed since `manifest.commit` — this keeps updates minimal and reviewable
- Always show diffs before applying changes
- If `manifest.commit` is not a valid commit in the KahnClaude repo (e.g. after a rebase), warn the user and fall back to comparing all installed files
