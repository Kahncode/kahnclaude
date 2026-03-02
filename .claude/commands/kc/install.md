---
name: install
description: Install KahnClaude components into the current project
scope: framework
---

Install KahnClaude components into the current working directory.

## Steps

1. Identify the KahnClaude source directory (ask the user if not already known)
2. Create `.claude/` subdirectories if they don't exist: `commands/`, `skills/`, `agents/`, `hooks/`
3. Copy command files from `commands/` → `.claude/commands/` (scope: project only; skip the `kc/` subfolder — those are framework-only)
4. Copy all files from `skills/` → `.claude/skills/`
5. Copy all files from `agents/` → `.claude/agents/`
6. Copy all files from `hooks/` → `.claude/hooks/`
7. If `CLAUDE.md` does not exist in the project root, copy `@project/CLAUDE.md` → `./CLAUDE.md` and tell the user to customize it
8. If `CLAUDE.local.md` does not exist, copy `@project/CLAUDE.local.md` → `./CLAUDE.local.md`
9. Verify `.gitignore` includes `CLAUDE.local.md` and `.env` — add them if missing
10. Report a summary of what was installed

## Notes

- Never overwrite existing files without asking
- If a component already exists in the target project, show a diff and ask whether to replace, skip, or merge
- `scope: framework` commands are never copied to target projects
