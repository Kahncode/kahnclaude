---
name: kc-install
description: Install KahnClaude components into the current project
scope: framework
---

Install KahnClaude components into a target project directory.

**Usage:** `/kc-install <project-path>`

The argument is the path to the project to install into. If omitted, ask the user for the target path before proceeding.

All harnesses (Claude Code, Codex, OpenCode, pi) are supported by default; do not ask which harnesses the user runs. Shared components go under `.agents/`; Claude-specific components (agents, hooks, settings) go under `.claude/`.

## Steps

1. Resolve the target project path from the argument (or ask if not provided)

   **Git preflight:** run `git --version`; if it fails, abort with "git is required to install KahnClaude." Then check the target is a git repo (`git -C <target> rev-parse --git-dir`). If not, offer to run `git init`; abort if the user declines.

   **Layout preflight:** if `<target>/.claude/.kahnclaude` exists (v1 manifest), stop and tell the user to run `/kc-update <target>`, which migrates the layout first.

2. Get the current KahnClaude git commit hash by running `git rev-parse --verify HEAD^{commit}` in the KahnClaude source directory. This expands to the canonical (full 40-char) hash and validates it's a real commit. Save this for the manifest.

3. **Ask the user about their tech stack** (skip the question if `/kc-create-project` passed the stack) before copying any agents or skills. Perform a quick research in the target project to determine the likely tech stack, then:

   a. **Always copy `core/` agents without asking** — they are universal. Do not present them as optional.

   b. **Auto-select agents that match detected technologies** — scan all subfolders under `.claude/agents/`, not just the obvious stack folder.

   c. **Present remaining agents grouped by subfolder** — ask the user which to include. If the harness has a structured question tool capped at 4 options and a group has more than 4 agents, describe the agents in plain text and ask the user to reply with which ones to include.

   d. Make clear that agents not relevant to the project should be excluded — a backend-only project doesn't need mobile or pure-frontend agents.

4. **Ask the Claude-specific questions** (two short questions, defaults in brackets):

   a. Create a `CLAUDE.local.md` for personal, gitignored overrides? [no]

   b. How should Claude Code see the skills: link `.claude/skills` to `.agents/skills` (symlink, or junction on Windows), falling back to a copy if linking fails [link], or always copy? Note that a copy must be re-synced when skills change (the SessionStart hook does this automatically).

5. Create the target directories if they don't exist: `.agents/skills/`, `.claude/agents/`, `.claude/hooks/`

6. Copy skills from `.agents/skills/` → `<target>/.agents/skills/`, one folder per skill (`<name>/SKILL.md` plus any bundled files). **Skip skills whose frontmatter has `scope: framework`.**

7. Copy only the selected agents to `<target>/.claude/agents/`, **preserving subfolder structure** (e.g. `agents/python/fastapi-dev.md` → `<target>/.claude/agents/python/fastapi-dev.md`). Create any needed subdirectories.

8. Copy all files from `.claude/hooks/` → `<target>/.claude/hooks/`, except `notify.py` (global-only: it is about the user's machine, installed by `/kc-install-global`)

9. **Migrate existing project skills, then project.** The projection script is the `link_skills.py` hook (copied in step 8).

   a. **Scan** `<target>/.claude/skills/` and `<target>/.claude/commands/`. Skip `.claude/skills` if it is already a link or a managed copy (it contains `.kahnclaude-copy`). Everything found is the project's own: projects are expected to hold more skills than KahnClaude ships, and a skill whose name differs from a KahnClaude one (e.g. renamed) is treated as custom. Never modify, delete or overwrite its content.

   b. **Offer to migrate** (default yes): "Move N existing skills/commands into `.agents/skills/` so Claude Code, Codex, OpenCode and pi all share them?" If yes, use `git mv`:
      - `.claude/skills/<name>/` → `.agents/skills/<name>/`, unchanged
      - `.claude/commands/<n>.md` → `.agents/skills/<n>/SKILL.md`; `.claude/commands/<ns>/<n>.md` → `.agents/skills/<ns>-<n>/SKILL.md`. The only edit is setting `name:` in the frontmatter to the folder name (lowercase, hyphens), which the skill format requires. Add nothing else; in particular do not add `disable-model-invocation`.
      - **Name collision** with a skill already in `.agents/skills/`: touch neither; ask for a new folder name, or leave the item in place and skip the projection (c) with a warning.

   c. **Clean up and project.** If `.claude/skills` and `.claude/commands` are now empty, remove them. If the user declined (b), skip the projection and tell them Claude Code will not see the skills in `.agents/skills/` until they migrate and run `python .claude/hooks/link_skills.py .`. Otherwise run `python <target>/.claude/hooks/link_skills.py <target> --mode <auto|copy>` (per question 4b) and record the `PROJECTION=` value for the manifest.

10. **Handle settings.json**:

    a. If `<target>/.claude/settings.json` does NOT exist: copy `project/settings.json` → `<target>/.claude/settings.json`

    b. If it already exists: deep-merge — add any `permissions.allow`, `permissions.deny`, and `hooks` entries from `project/settings.json` that are not already present; a hook counts as present when an existing entry's command references the same script file name (quoting and path style differ between versions); in that case update the existing entry's `matcher` to the shipped one instead of adding a second entry. Never remove existing entries. Show the user what will be added and confirm before applying.

11. **Handle AGENTS.md generation** (run from the KahnClaude working directory; guides in `project/tech-stacks/` are used here and never copied to the target). When invoked by `/kc-create-project`, skip this step: create-project generates `AGENTS.md` itself afterwards with the interview answers.

    a. If `AGENTS.md` does not exist in the target project:
    - Run `/kc-generate-agents-md` with the target project path
    - The skill scans the target for tech stack manifests, consults the appropriate guide in `project/tech-stacks/`, asks guided questions, and writes a complete `AGENTS.md` plus the one-line `CLAUDE.md` shim (`@AGENTS.md`)
    - Report success with section count to the user

    b. If `AGENTS.md` already exists in the target project:
    - Ask the user: "Your project already has an AGENTS.md. Enhance it with missing sections?"
    - If yes: run `/kc-generate-agents-md` in enhance mode for the target
    - If no: skip to step 12

    c. If only a `CLAUDE.md` exists (not yet migrated): `git mv CLAUDE.md AGENTS.md`, then write the shim `CLAUDE.md` containing `@AGENTS.md`, then continue with (b).

12. If the user said yes to 4a, copy `project/CLAUDE.local.md` → `<target>/CLAUDE.local.md`.

13. Verify `<target>/.gitignore` includes `CLAUDE.local.md`, `.claude/settings.local.json`, `.claude/skills`, `.claude/skills.bak-*` (the projection, recreated by the SessionStart hook, and its backups) and `.env` — add them if missing

14. **Write the install manifest** to `<target>/.agents/.kahnclaude` as JSON:

    ```json
    {
      "version": 2,
      "layout": "agents",
      "source": "<absolute-path-to-kahnclaude>",
      "commit": "<validated-git-commit-hash>",
      "installed_at": "<ISO-8601-timestamp>",
      "updated_at": "<ISO-8601-timestamp>",
      "projection": "<symlink|junction|copy>",
      "agents": ["<relative-agent-path>", ...],
      "notes": "<one-line summary of stack detected and agent selections>",
      "scaffold": { "stack": "<stack>", "template_repo": "<url>", "template_ref": "<ref>" }
    }
    ```

    - `scaffold` is optional: written only when invoked by `/kc-create-project`; omit otherwise
    - `commit` is the canonical commit hash from step 2
    - `installed_at` is when this manifest was first created
    - `updated_at` is set equal to `installed_at` at creation time; it will be updated by `/kc-update` and used for recovery if the commit hash becomes invalid
    - `projection` is the value reported by `link_skills.py` (a hook in `.claude/hooks/`), or `none` if the projection was skipped
    - `agents` lists all agent paths that were copied (relative to `.claude/agents/`, e.g. `core/tech-lead-orchestrator.md`)
    - `notes` should capture what stack was detected and which optional agent groups the user chose
    - Add `.kahnclaude` to `<target>/.gitignore` if the user prefers not to commit it, but note that committing it allows teammates to know which version of KahnClaude is installed

15. Report a summary of what was installed and what was skipped

## Notes

- Never overwrite existing files without asking
- If a component already exists in the target project, show a diff and ask whether to replace, skip, or merge
- `scope: framework` skills are never copied to target projects
- `CLAUDE.local.md` is never copied unless the user opted in (step 4a) — it is gitignored and personal to each developer
- Do not copy agents the user did not select — fewer irrelevant files means less context noise in the target project
- Agents and hooks are Claude Code only; other harnesses get the skills and `AGENTS.md`
- The `.agents/.kahnclaude` manifest is the source of truth for future `kc-update` runs
