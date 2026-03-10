---
name: install
description: Install KahnClaude components into the current project
scope: framework
---

Install KahnClaude components into a target project directory.

**Usage:** `/kc:install <project-path>`

The argument is the path to the project to install into. If omitted, ask the user for the target path before proceeding.

## Steps

1. Resolve the target project path from the argument (or ask if not provided)

2. Get the current KahnClaude git commit hash by running `git rev-parse HEAD` in the KahnClaude source directory. Save this for the manifest.

3. **Ask the user about their tech stack** before copying any agents or skills. Perform a quick research in the target project to determine the likely tech stack, then:

   a. **Always copy `core/` agents without asking** — they are universal. Do not present them as optional.

   b. **Auto-select agents that match detected technologies** — scan all subfolders under `.claude/agents/`, not just the obvious stack folder.

   c. **Present remaining agents grouped by subfolder** — ask the user which to include. Note: `AskUserQuestion` is capped at 4 options per question. When a subfolder group has more than 4 agents, do NOT use the structured UI for that group — instead describe the agents in plain text and ask the user to reply with which ones to include.

   d. Make clear that agents not relevant to the project should be excluded — a backend-only project doesn't need mobile or pure-frontend agents.

4. Create `.claude/` subdirectories in the target project if they don't exist: `commands/`, `skills/`, `agents/`, `hooks/`

5. Copy command files from `.claude/commands/` → `<target>/.claude/commands/`, **preserving subfolder structure** (e.g. `commands/kc/create-agent-skill.md` → `<target>/.claude/commands/kc/create-agent-skill.md`). Create any needed subdirectories.

6. Copy all files from `.claude/skills/` → `<target>/.claude/skills/`, **preserving subfolder structure**. Create any needed subdirectories.

7. Copy only the selected agents to `<target>/.claude/agents/`, **preserving subfolder structure** (e.g. `agents/python/fastapi-dev.md` → `<target>/.claude/agents/python/fastapi-dev.md`). Create any needed subdirectories.

8. Copy all files from `.claude/hooks/` → `<target>/.claude/hooks/`

9. If `CLAUDE.md` does not exist in the target project root, copy `project/CLAUDE.md` → `<target>/CLAUDE.md` and tell the user to customize it

10. If `CLAUDE.local.md` does not exist, copy `project/CLAUDE.local.md` → `<target>/CLAUDE.local.md`

11. Verify `<target>/.gitignore` includes `CLAUDE.local.md` and `.env` — add them if missing

12. **Write the install manifest** to `<target>/.claude/.kahnclaude` as JSON:
    ```json
    {
      "version": 1,
      "source": "<absolute-path-to-kahnclaude>",
      "commit": "<git-commit-hash>",
      "installed_at": "<ISO-8601-timestamp>",
      "agents": ["<relative-agent-path>", ...],
      "notes": "<one-line summary of stack detected and agent selections>"
    }
    ```
    - `agents` lists all agent paths that were copied (relative to `.claude/agents/`, e.g. `core/tech-lead-orchestrator.md`)
    - `notes` should capture what stack was detected and which optional agent groups the user chose
    - Add `.kahnclaude` to `<target>/.gitignore` if the user prefers not to commit it, but note that committing it allows teammates to know which version of KahnClaude is installed

13. Report a summary of what was installed and what was skipped

## Notes

- Never overwrite existing files without asking
- If a component already exists in the target project, show a diff and ask whether to replace, skip, or merge
- `scope: framework` commands are never copied to target projects
- Do not copy agents the user did not select — fewer irrelevant files means less context noise for Claude in the target project
- The `.kahnclaude` manifest is the source of truth for future `kc:update` runs
