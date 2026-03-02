# Global Claude Rules

> Installed at `~/.claude/CLAUDE.md`. Applies to every project.
> Merge with `/kc-install-global` — never overwrites existing content.

---

## Absolute Rules — All Projects

### Never Publish Sensitive Data

- NEVER commit passwords, API keys, tokens, or secrets to git
- NEVER commit `.env` files — always verify `.env` is in `.gitignore`
- NEVER output secrets in responses, logs, or suggestions
- Before ANY commit: verify no secrets are staged

### Never Auto-Deploy

- NEVER deploy to production without explicit user confirmation
- NEVER assume "fix it and deploy" means deploy automatically
- Always ask: "Do you want me to deploy this now?"

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
- `.gitignore` — must include `.env`, `CLAUDE.local.md`, secrets
- `CLAUDE.md` — project-specific rules
- `CLAUDE.local.md` — personal overrides (gitignored)

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
- Tests must pass before committing

---

## Communication

- Ask before taking irreversible actions
- When multiple valid approaches exist, present options with tradeoffs
- Plan first for non-trivial tasks — get agreement before writing code
