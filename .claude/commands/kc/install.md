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

2. **Ask the user about their tech stack** before copying any agents or skills. Perform a quick research in the target project to determine the likely tech stack. Present the available tech-stack-specific agents and generic developer agents, and ask which ones apply to this project. For example:
   - "Which of these agents do you want to include?"
   - Generic (applicable to most projects): `code-reviewer`, `test-writer`, `documenter`
   - Tech-stack specific: list all agents found in subfolders under `.claude/agents/` (e.g. `mobile/react-native-expo-dev`, `python/fastapi-dev`), grouped by subfolder
   - Make clear that agents not relevant to the project should be excluded — a backend-only project doesn't need a mobile or frontend agent, a game project may not need any web agents at all
   - Only install the agents the user confirms as relevant

3. Create `.claude/` subdirectories in the target project if they don't exist: `commands/`, `skills/`, `agents/`, `hooks/`

4. Copy command files from `.claude/commands/` → `<target>/.claude/commands/`

5. Copy all files from `.claude/skills/` → `<target>/.claude/skills/`

6. Copy only the selected agents to `<target>/.claude/agents/`, preserving subfolder structure for tech-stack-specific agents

7. Copy all files from `.claude/hooks/` → `<target>/.claude/hooks/`

8. If `CLAUDE.md` does not exist in the target project root, copy `project/CLAUDE.md` → `<target>/CLAUDE.md` and tell the user to customize it

9. If `CLAUDE.local.md` does not exist, copy `project/CLAUDE.local.md` → `<target>/CLAUDE.local.md`

10. Verify `<target>/.gitignore` includes `CLAUDE.local.md` and `.env` — add them if missing

11. Report a summary of what was installed and what was skipped

## Notes

- Never overwrite existing files without asking
- If a component already exists in the target project, show a diff and ask whether to replace, skip, or merge
- `scope: framework` commands are never copied to target projects
- Do not copy agents the user did not select — fewer irrelevant files means less context noise for Claude in the target project
