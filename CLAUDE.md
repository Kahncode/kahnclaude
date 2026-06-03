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
| `.claude/commands/kc/` | Framework-only commands (`scope: framework`), invoked as `/kc:<name>` |
| `.claude/skills/` | Focused skills (SKILL.md only) — organized by theme (`code/`, `perforce/`, etc.) |
| `project/docs/standards/` | Shared reference docs (standards, checklists, formats) loaded by agents and skills |
| `project/scripts/` | Reusable scripts (Python, PowerShell) for editor and build automation |
| `.claude/agents/` | Agents distributed to projects (subfolder: `core/`) |
| `.claude/hooks/` | Hook scripts distributed to projects |
| `.claude/settings.json` | Hooks wiring for this framework repo |
| `project/` | CLAUDE.md templates and `settings.json` template for new projects |
| `project/docs/` | Docs distributed to target projects via `/kc:install` (tech-stack guides) |
| `global/` | Global `~/.claude/` config templates |
| `inspiration/` | Read-only third-party references |

---

## Adding a New Component

When adding any component (command, agent, hook), update ALL of:

1. The component file itself in `.claude/commands/` (project) or `.claude/commands/kc/` (framework), `.claude/agents/`, or `.claude/hooks/`
2. `README.md` — component listing and description
3. `CONTRIBUTING.md` — any new conventions introduced

If adding a hook: also wire it in `@.claude/settings.json` and document the wiring in `@global/settings.json`.

If adding coding standards content: add it to the relevant reference doc under `project/docs/standards/` (for review criteria) or embed it in the consuming agent (for single-consumer standards). Update `README.md` if the change adds a new skill.

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
- No file > 300 lines
- `description` fields must not exceed 400 characters
- Use `@path/to/file` syntax for absolute file path references in `.md` files (e.g. `@src/main.py`, `@.claude/settings.json`); relative or fuzzy references (e.g. `file.ext`, `commands/`) are fine as-is
- Agents that should auto-trigger must include `Use PROACTIVELY when [specific condition]` in their description — only for agents users would otherwise skip, not for agents users always invoke explicitly
- Agents may be organized in subfolders: `core/` for cross-cutting concerns, `<stack>/` for tech-specific agents

### Python (hooks)
- Type hints on all functions
- Exit code semantics: `0` = allow, `2` = block with message, `1` = warn
- Print blocking reason to `stderr` when exiting with code 2
- No external dependencies without documentation

---

## References

- [Architecture](docs/ARCHITECTURE.md) — system overview, component map, technology choices, and subsystem links

---

## Workflow

- Work on feature branches — `feat/<name>`, `fix/<name>`, `docs/<name>`
- Keep commits focused: one logical change per commit
- Run `python3 -m py_compile hooks/*.py` to syntax-check hooks before committing (Windows: use `py -m py_compile`)
