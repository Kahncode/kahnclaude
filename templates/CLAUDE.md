# CLAUDE.md — [Project Name]

> Project instructions for Claude Code. Customize this for your project.
> Keep team-shared rules here. Put personal preferences in `CLAUDE.local.md`.

---

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/review` | Code review against project rules |
| `/commit` | Smart commit with conventional commit message |
| `/security-check` | Scan for secrets and vulnerabilities |
| `/refactor <file>` | Audit and refactor a file against all rules |

---

## Critical Rules

### 0. Never Publish Sensitive Data

- NEVER commit passwords, API keys, tokens, or secrets
- NEVER commit `.env` files — always verify `.env` is in `.gitignore`
- Before ANY commit: verify no secrets are staged

### 1. Ask Before Deploying

- NEVER auto-deploy, even if the fix seems simple
- Always wait for explicit confirmation: "yes, deploy this"

### 2. Quality Gates

- No file > 300 lines (split if larger)
- No function > 50 lines (extract helpers)
- All tests must pass before committing

### 3. Never Work Directly on Main

```bash
# Always branch first — before editing any files
git checkout -b feat/<task-name>
```

- `feat/<name>` — new features
- `fix/<name>` — bug fixes
- `docs/<name>` — documentation
- `refactor/<name>` — refactors

---

## Project-Specific Rules

<!-- Add your project's rules here. Examples: -->

<!-- ### API Versioning
All endpoints must use `/api/v1/` prefix. -->

<!-- ### Database Access
Always use [your ORM/library]. Never import raw drivers in business logic. -->

<!-- ### Language/Framework Rules
[TypeScript strict mode, Python type hints, etc.] -->

---

## When Something Seems Wrong

Before assuming something is broken:

- Missing feature? → Check feature flags / config BEFORE assuming bug
- Empty data? → Check if services are running BEFORE assuming broken
- Auth failing? → Check which auth system is active BEFORE debugging
- Test failing? → Read the full error message BEFORE changing code

---

## Service Ports

<!-- Document your project's ports here -->

| Service | Dev Port | Test Port |
|---------|----------|-----------|
| [Service] | [port] | [port] |

---

## Project Structure

<!-- Document your project structure here -->

```
project/
├── CLAUDE.md
├── CLAUDE.local.md     (gitignored)
├── .claude/
│   ├── commands/
│   ├── skills/
│   ├── agents/
│   └── hooks/
└── ...
```

---

## CLAUDE.md Is Team Memory

Every time Claude makes a mistake, add a rule to prevent it from recurring.
Tell Claude: "Update CLAUDE.md so this doesn't happen again."
The whole team benefits from every lesson learned — this file is in git.
