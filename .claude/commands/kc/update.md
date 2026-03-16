---
name: update
description: Update KahnClaude components in a target project to the latest versions
scope: framework
---

Push KahnClaude updates to a target project that was previously installed with `/kc:install`.

**Usage:** `/kc:update <project-path>`

The argument is the path to the target project. If omitted, ask the user for it before proceeding.

## Steps

1. Resolve the target project path from the argument (or ask if not provided).

2. **Read the install manifest** from `<target>/.claude/.kahnclaude`. If it does not exist, tell the user to run `/kc:install <project-path>` first and stop.
   - **Validate the stored commit**: Run `git rev-parse --verify <manifest.commit>^{commit}` in the KahnClaude directory
   - If validation fails, attempt recovery:
     - Run `git log --before="<manifest.updated_at>" --max-count=1 --format=%H` to find the closest commit at/before that timestamp
     - Ask the user: "Manifest commit `<stored>` is invalid. Last updated `<manifest.updated_at>`. Use closest commit `<inferred-hash>`? [Y/n]"
     - If yes: use `<inferred-hash>` as the baseline for the diff
     - If no: error with "Manifest is corrupted. Run `/kc:install <project-path>` to reinitialize."

3. **Compute the diff scope**: run `git diff --name-only <manifest.commit>..HEAD` in the KahnClaude directory to get all files changed since the last install/update. Only files in this diff are candidates — do not touch components that haven't changed.

4. **Get the current commit hash**: run `git rev-parse --verify HEAD^{commit}` in the KahnClaude directory. This expands HEAD to its canonical (full) commit hash and validates it's a real commit. If validation fails, error with "Could not resolve HEAD to a valid commit."

5. **Filter changed files by category** and determine what needs updating:
   - `.claude/commands/` files (excluding `scope: framework` commands) → candidates for `<target>/.claude/commands/`
   - `.claude/skills/` files → candidates for `<target>/.claude/skills/`
   - `.claude/agents/` files **that are listed in `manifest.agents`** → candidates for `<target>/.claude/agents/`
   - `.claude/hooks/` files → candidates for `<target>/.claude/hooks/`
   - `project/settings.json` → candidate for `<target>/.claude/settings.json` (**merge only** — never overwrite; add any `permissions.allow`, `permissions.deny`, and `hooks` entries not already present; show diff and confirm before applying)
   - `project/CLAUDE.md` or `project/CLAUDE.local.md` → skip (never overwrite)

   Ignore changed files outside these categories (e.g. `global/`, `inspiration/`, `README.md`, `CONTRIBUTING.md`).

6. **Check for new agents** in the diff (added agent files not currently in `manifest.agents`):
   - Group new agents by subfolder and present them to the user, asking which to add
   - Use `AskUserQuestion` for groups of ≤ 4; plain text description for larger groups
   - Add user-selected new agents to the candidate update list and to `manifest.agents`

7. **Show a summary** of candidates: new files, changed files, and any diff files that are not installed (skipped). Ask the user to confirm before applying.

8. **For each changed file that is installed**, compare the target and KahnClaude versions:
   - If they are **identical**: explicitly note "No changes" and skip
   - If they **differ**: show a full diff (using `git diff` or side-by-side comparison) and ask: update, skip, or merge
   - **Never assume files are unchanged** — always verify by actual comparison before skipping
   - Offer a "confirm all" shortcut if there are many files with changes

9. **Apply updates**: copy confirmed files from KahnClaude to `<target>`, preserving subfolder structure. Create any needed subdirectories.

10. **Update the manifest** at `<target>/.claude/.kahnclaude`:
    - **Before writing**, verify the new commit hash: Run `git rev-parse --verify <new-hash>^{commit}` one more time
    - If validation fails, abort with error: "Internal error: new commit hash is invalid. Changes aborted."
    - Set `commit` to the validated canonical commit hash (full 40-char SHA-1)
    - Set `installed_at` to the original installation timestamp (do not modify)
    - Set `updated_at` to the current ISO-8601 timestamp (use for future recovery if commit hash becomes invalid)
    - Update `agents` to reflect any newly added agents
    - Append to `notes`: a one-line entry summarizing what was updated (e.g. `"2026-03-10: updated 3 commands, added react agent"`)

11. Report a summary of what was updated, what was skipped, and what new agents were added.

## Notes

- Never delete files that exist in the target but not in KahnClaude (the project may have custom components)
- Never overwrite `CLAUDE.md` or `CLAUDE.local.md` (these are project-specific)
- Only update files that changed since `manifest.commit` — this keeps updates minimal and reviewable
- **Always verify file differences by actual comparison** — never assume files are identical based on reading or skimming. Use `git diff`, `diff`, or explicit line-by-line comparison before concluding "no changes"
- Always show diffs for files with actual changes before applying updates
- If `manifest.commit` is not a valid commit in the KahnClaude repo (e.g. after a rebase), warn the user and fall back to comparing all installed files against the current KahnClaude versions
