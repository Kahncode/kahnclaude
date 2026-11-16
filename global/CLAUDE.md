# Global Claude Rules

> Installed at `~/.claude/CLAUDE.md`. Applies to every project.
> Merge with `/kc-install-global` — never overwrites existing content.

---

## Absolute Rules — All Projects

### Never Publish Sensitive Data

- NEVER commit passwords, API keys, tokens, or secrets to version control
- NEVER commit `.env` files — always verify `.env` is in `.p4ignore` / `.gitignore`
- NEVER output secrets in responses, logs, or suggestions
- Before ANY commit or changelist: verify no secrets are staged or opened

### Never Auto-Submit

- NEVER submit to production without explicit user confirmation
- NEVER assume "fix it and submit" means submit automatically
- Always ask: "Do you want me to submit this now?"

### Never Rename Without a Plan

Renaming packages, modules, or key variables mid-project causes cascading failures. If renaming is needed:

1. List ALL files and references that will change
2. Use IDE semantic rename, not search-replace
3. Search the full project for the old name after renaming
4. Check: `.md`, `.txt`, `.env`, comments, strings, config files
5. Start a fresh Claude session after the rename

---

## New Project Standards

Every new project must have:

- `.env.example` — documented variable names (never values)
- `.p4ignore` / `.gitignore` — must include `.env`, `CLAUDE.local.md`, secrets
- `CLAUDE.md` — project-specific rules
- `CLAUDE.local.md` — personal overrides (ignored by VCS)

---

## Code Standards (Universal)

### Security

- Never hardcode credentials — always use environment variables
- Validate input at system boundaries (user input, external APIs)
- No SQL/command injection via string concatenation

### Error Handling

- Never swallow errors silently
- Log errors with enough context to diagnose them
- Distinguish between expected errors (user-facing) and unexpected errors (logged internally)

### Quality Gates

- No file > 300 lines — split if larger
- No function > 50 lines — extract helpers
- Tests must pass before committing or submitting

---

## Project Variables (`{{VAR}}`)

Shared skills, agents, commands and docs are project-agnostic and write project values as `{{NAME}}`.
- `{{NAME}}` = the value of `NAME` in the current project's `.claude/rules/project-vars.md` (auto-loaded). Substitute it before running anything.
- A needed var is missing or empty: stop, name it, and point to the KahnClaude template `project/templates/unreal-project/` (README = onboarding). Never guess a value.
- Overlay: when a shared skill, agent or standard `X` runs, also read `{{PROJECT_NOTES_DIR}}\X.md` if it exists; project-only rules live there and win over the generic file.
- `{{VAR}}` only in text Claude reads. Hook commands and script code use real env vars (`$CLAUDE_PROJECT_DIR`) and read vars through `.claude/scripts/lib/project_vars.py` / `ProjectVars.ps1`.
- Project values → `{{VAR}}` in `.claude/rules/project-vars.md`; project-only rules → the `{{PROJECT_NOTES_DIR}}\X.md` overlay. Secrets never go in the vars file.

---

## Communication

- Ask before taking irreversible actions
- When multiple valid approaches exist, present options with tradeoffs
- Plan first for non-trivial tasks — get agreement before writing code
