# New Unreal project: onboarding the user-level Claude setup

The UE skills, agents, hooks and standards live in `~/.claude` and read project values as `{{NAME}}` from the project's `.claude/rules/project-vars.md`.

1. **Vars.** Copy `project-vars.md` to `<project>/.claude/rules/project-vars.md` and fill it in. Set the four path values as real env vars too (scripts also fall back to the vars file): `<project>/.claude/settings.local.json` → `"env": { "PROJECT_ROOT": "...", "UE_ENGINE": "...", "UE_PROJECT": "...", "UE_SOLUTION": "..." }`.
2. **Permissions.** Copy `settings.json` to `<project>/.claude/settings.json` (or merge its `permissions` into an existing one). Hooks are already wired user-wide in `~/.claude/settings.json`; nothing to add.
3. **Check.** From the project root: `python -I -X utf8 .claude/scripts/lib/project_vars.py --check .claude/agents .claude/skills .claude/commands .claude/hooks .claude/scripts docs` lists every `{{VAR}}` the setup uses that this project hasn't defined. Empty is fine for services the project doesn't have.

Project-only rules for a user-level skill/agent/standard `X` go in `{{PROJECT_NOTES_DIR}}\X.md` (e.g. `docs/project-notes/test-dev.md`); the generic file reads it when present.
