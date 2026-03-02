# CLAUDE.md — KahnClaude Framework

This is the Claude Code configuration for working on the KahnClaude framework itself.

---

## Absolute Rules

### NEVER Modify the Inspiration Folder

`inspiration/` contains third-party reference projects. It is read-only.

- NEVER edit, delete, or create files in `inspiration/`
- NEVER commit changes inside `inspiration/`
- Read inspiration projects for reference only — extract ideas, never copy verbatim

### NEVER Commit Secrets

- NEVER commit `.env`, credentials, API keys, or tokens
- `.env` and `CLAUDE.local.md` must always be in `.gitignore`

---

## Framework Structure

| Folder | Purpose |
|--------|---------|
| `.claude/commands/` | Slash commands — `scope: project` ones are distributed to projects |
| `.claude/skills/` | Skills distributed to projects |
| `.claude/agents/` | Agents distributed to projects |
| `.claude/hooks/` | Hook scripts distributed to projects |
| `.claude/settings.json` | Hooks wiring for this framework repo |
| `templates/` | CLAUDE.md templates for new projects |
| `global/` | Global `~/.claude/` config templates |
| `inspiration/` | Read-only third-party references |

---

## Adding a New Component

When adding any component (command, skill, agent, hook), update ALL of:

1. The component file itself in `.claude/commands/`, `.claude/skills/`, `.claude/agents/`, or `.claude/hooks/`
2. `README.md` — component listing and description
3. `CONTRIBUTING.md` — any new conventions introduced

If adding a hook: also wire it in `.claude/settings.json` and document the wiring in `global/settings.json`.

---

## Hooks (Python Only)

All hooks in `hooks/` must be written in Python. No bash. Reasons:
- Cross-platform (Windows, macOS, Linux, WSL)
- No shell quoting edge cases
- Easier to test and maintain

Hooks must use only Python stdlib unless the dependency is explicitly documented and widely available.

---

## Code Style

This repo primarily contains Markdown and Python. Follow these conventions:

### Markdown (commands, skills, agents, templates)
- Use YAML frontmatter for metadata fields (name, description, scope, triggers)
- Keep command prompts actionable and specific
- No emojis unless the user explicitly requested them

### Python (hooks)
- Type hints on all functions
- Exit code semantics: `0` = allow, `2` = block with message, `1` = warn
- Print blocking reason to `stderr` when exiting with code 2
- No external dependencies without documentation

---

## Workflow

- Work on feature branches — `feat/<name>`, `fix/<name>`, `docs/<name>`
- Keep commits focused: one logical change per commit
- Run `python -m py_compile hooks/*.py` to syntax-check hooks before committing
