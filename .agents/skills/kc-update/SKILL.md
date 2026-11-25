---
name: kc-update
description: Update KahnClaude components in a target project to the latest versions. Migrates Claude-only (v1) installs to the harness-neutral .agents/ layout first.
scope: framework
---

Push KahnClaude updates to a target project that was previously installed with `/kc-install` (or the older `/kc:install`).

**Usage:** `/kc-update <project-path>`

The argument is the path to the target project. If omitted, ask the user for it before proceeding.

## Steps

1. Resolve the target project path from the argument (or ask if not provided).

   **Git preflight:** run `git --version`; if it fails, abort with "git is required to update KahnClaude." If `<target>` is not a git repo (`git -C <target> rev-parse --git-dir`), abort and tell the user to run `/kc-install` first. Require a clean working tree in `<target>` (`git status --porcelain`); if dirty, ask the user to commit or stash first, because migration makes one commit per phase.

2. **Detect the layout:**
   - `<target>/.agents/.kahnclaude` exists (`version: 2`): current layout, continue to step 3.
   - `<target>/.claude/.kahnclaude` exists (`version: 1`, no `layout`): Claude-only layout. Run **Migration** (below), then continue to step 3 in **compare-all mode** (step 4 note).
   - Neither exists: tell the user to run `/kc-install <project-path>` first and stop.

3. **Read the manifest** and validate the stored commit: run `git rev-parse --verify <manifest.commit>^{commit}` in the KahnClaude directory.
   - If validation fails, attempt recovery:
     - Run `git log --before="<manifest.updated_at>" --max-count=1 --format=%H` to find the closest commit at/before that timestamp
     - Ask the user: "Manifest commit `<stored>` is invalid. Last updated `<manifest.updated_at>`. Use closest commit `<inferred-hash>`? [Y/n]"
     - If no: error with "Manifest is corrupted. Run `/kc-install <project-path>` to reinitialize."

4. **Compute the diff scope**: run `git diff --name-only <manifest.commit>..HEAD` in the KahnClaude directory. Only files in this diff are candidates.
   - **Compare-all mode** (after migration, or if the commit is unusable and the user declines recovery): the layout changed, so commit diffs no longer map to target paths. Treat every installed component as a candidate and decide by content comparison only.

5. **Get the current commit hash**: run `git rev-parse --verify HEAD^{commit}` in the KahnClaude directory. If validation fails, error with "Could not resolve HEAD to a valid commit."

6. **Filter changed files by category:**
   - `.agents/skills/<name>/**` (excluding skills with `scope: framework`) → candidates for `<target>/.agents/skills/<name>/`
   - `.claude/agents/` files **listed in `manifest.agents`** → candidates for `<target>/.claude/agents/`
   - `.claude/hooks/` files (except `notify.py`, global-only) → candidates for `<target>/.claude/hooks/`
   - `project/settings.json` → candidate for `<target>/.claude/settings.json` (**merge only** — never overwrite; add any `permissions.allow`, `permissions.deny`, and `hooks` entries not already present; a hook counts as present when an existing entry's command references the same script file name (quoting and path style differ between versions); in that case update the existing entry's `matcher` to the shipped one instead of adding a second entry; show diff and confirm before applying)
   - `project/AGENTS.md`, `project/CLAUDE.md` or `project/CLAUDE.local.md` → skip (never overwrite)

   Ignore changed files outside these categories (e.g. `global/`, `inspiration/`, `README.md`, `CONTRIBUTING.md`).

6a. **Remove retired hooks.** KahnClaude no longer ships these hooks: `after-edit.py`, `block-dangerous-commands.py`, `block-secrets.py`, `check-branch.py`, `check-env-sync.py`, `lint-on-stop.py`, `verify-no-secrets.py` (replaced by `permissions` deny rules, auto mode, and the project's own git hooks). For each one present in `<target>/.claude/settings.json` or `<target>/.claude/hooks/`:
   - Remove every `hooks` entry whose command references it from `<target>/.claude/settings.json` (and `settings.local.json`), dropping matcher groups and events left empty. Do this **before** deleting the script: a hook pointing at a missing script makes `python3` exit 2, which blocks every matching tool call.
   - Delete the script from `<target>/.claude/hooks/` if it is identical to the last version KahnClaude shipped (`git show <manifest.commit>:.claude/hooks/<name>`, CRLF normalised); if the project modified it, ask before deleting.
   - Mention that the project's linting, formatting and secret scanning should live in its own git hooks or CI.
   - Offer to remove the `mcp__filesystem__*` allow entry if present: MCP tools bypass `Read`/`Edit` deny rules, and `--add-dir` or `additionalDirectories` replace it.
   - `notify.py` moved to global-only: remove its `Notification` entry and the script the same way, and suggest `/kc-install-global` so notifications keep working.
   Show the list with the step 8 summary; this is the one exception to "never delete files".

7. **Check for new agents** in the diff (added agent files not in `manifest.agents`): group by subfolder, ask which to add (plain text for groups larger than a question tool allows), and add the selection to the candidates and to `manifest.agents`.

8. **Show a summary** of candidates (new, changed, not installed). Ask the user to confirm before applying.

9. **For each candidate that is installed**, compare the target and KahnClaude versions (normalise CRLF to LF first):
   - **Identical**: note "No changes" and skip
   - **Differ**: show a full diff and ask: update, skip, or merge
   - **Never assume files are unchanged** — always compare before skipping
   - Offer a "confirm all" shortcut if there are many changes

10. **Apply updates**: copy confirmed files, preserving subfolder structure. Create needed subdirectories.

11. **Re-project skills** (skip if `manifest.projection` is `none`): run `python <target>/.claude/hooks/link_skills.py <target> --mode <manifest.projection is "copy" ? copy : auto>`.

12. **Update the manifest** at `<target>/.agents/.kahnclaude`:
    - Re-verify the new commit hash with `git rev-parse --verify <new-hash>^{commit}`; abort if invalid
    - Set `commit` to the new full hash, keep `installed_at`, set `updated_at` to now
    - Update `agents` and `projection`
    - Append to `notes` a one-line entry (e.g. `"2026-03-10: updated 3 skills, added react agent"`)

13. Report what was updated, skipped, and added.

## Migration (v1 Claude-only layout to v2 `.agents/` layout)

Make a dry-run summary first and wait for confirmation. Then run each phase as its own commit in `<target>`; skip phases that have nothing to do (idempotent). Never overwrite without a diff and a question.

1. **Instructions** — `git mv CLAUDE.md AGENTS.md`, then write `CLAUDE.md` containing the single line `@AGENTS.md`. If `AGENTS.md` already exists, show a diff and ask how to merge. If `CLAUDE.md` is already only `@AGENTS.md`, skip. Replace "Claude Code" wording in the file only if the user agrees. Leave `CLAUDE.local.md` alone.
2. **Skills and commands** — classify every item in `<target>/.claude/skills/` and `<target>/.claude/commands/` (command names converted as in `/kc-install` step 9b), then handle each class:
   - **Shipped by KahnClaude** (the name matches a `scope: project` skill in KahnClaude's `.agents/skills/`): the source is KahnClaude's `.agents/skills/<name>/`, not the target's old copy. Compare the old copy with it (normalise CRLF). Identical: `git rm` the old copy. Different: show the diff and ask, replace with KahnClaude's version or keep the local version as the project's own (moved unchanged into `.agents/skills/`, and later updates will diff it as usual). Then copy KahnClaude's version into `<target>/.agents/skills/<name>/` unless the local version was kept.
   - **Anything else** (custom, including a renamed KahnClaude skill): the project's own. Ask once, then move it using `/kc-install` step 9a-9b (same conversion, same name-collision handling, `git mv`, no content changes beyond `name:`, never add `disable-model-invocation`). If the user declines, leave these in place; phase 3 skips the projection.
   - Nothing is rewritten or deleted other than the replaced KahnClaude copies above.
3. **Projection** — ensure `<target>/.claude/hooks/link_skills.py` is present (copy it from KahnClaude if missing), ask the Claude-specific question (link, or copy), then do `/kc-install` step 9c (remove the now-empty `.claude/skills` and `.claude/commands`, then project, or skip with a warning if phase 2 left custom items behind).
4. **Settings and ignore** — merge the `SessionStart` hook from `project/settings.json` into `<target>/.claude/settings.json` (merge rules as in step 6). If the target has the older wiring that points at `.agents/skills/link-skills/scripts/link_skills.py`, replace that command with `.claude/hooks/link_skills.py` and remove the leftover `.agents/skills/link-skills/` folder (a KahnClaude-shipped skill that no longer exists). Add `.claude/skills` to `.gitignore`.
5. **Manifest** — write `<target>/.agents/.kahnclaude` as `version: 2`, `layout: "agents"`, with the existing fields carried over plus `projection` (`"none"` if the projection was skipped). Delete `.claude/.kahnclaude`. Keep the old `commit` for now.

## Notes

- Never delete files that exist in the target but not in KahnClaude (the project may have custom components), except the retired hooks in step 6a
- Skills in `<target>/.agents/skills/` that KahnClaude does not ship, including renamed or removed KahnClaude skills, are the project's own: never modify, delete or flag them as stale
- Never overwrite `AGENTS.md`, `CLAUDE.md` or `CLAUDE.local.md` (project-specific), except for the migration steps above
- Only update files that changed since `manifest.commit` — keeps updates minimal and reviewable (except compare-all mode)
- **Always verify differences by actual comparison**; never conclude "no changes" from skimming
- If `manifest.commit` is not a valid commit in the KahnClaude repo (e.g. after a rebase), warn the user and use compare-all mode
