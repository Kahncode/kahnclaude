# AGENTS.md — KahnClaude Framework

Instructions for coding agents (Claude Code, Codex, OpenCode, pi) working on the KahnClaude framework itself. `CLAUDE.md` is a one-line shim that imports this file.

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
| `.agents/skills/` | Skills, including slash-command workflows — harness-neutral (Agent Skills format). `scope: project` ones are distributed to projects; `scope: framework` ones are never distributed. Skills that manage KahnClaude itself use the `kc-` prefix (`/kc-<name>`); the prefix does not imply scope |
| `.claude/skills/` | Gitignored projection of `.agents/skills/` for Claude Code (junction/symlink/copy, created by the `link_skills.py` SessionStart hook) |
| `.claude/agents/` | Agents distributed to projects (Claude Code only) |
| `.claude/hooks/` | Hook scripts distributed to projects (Claude Code only) |
| `.claude/settings.json` | Hooks wiring for this framework repo |
| `project/` | `AGENTS.md`, `CLAUDE.md` shim and `settings.json` templates for new projects |
| `global/` | Global `~/.claude/` config templates |
| `inspiration/` | Read-only third-party references |

---

## Adding a New Component

When adding any component (skill or slash command, agent, hook), update ALL of:

1. The component file itself in `.agents/skills/<name>/SKILL.md` (skills and slash commands; KahnClaude-management ones use the `kc-` prefix), `.claude/agents/`, or `.claude/hooks/`
2. `README.md` — component listing and description
3. `CONTRIBUTING.md` — any new conventions introduced

If adding a hook: also wire it in `@.claude/settings.json` and document the wiring in `@global/settings.json`.

---

## Hooks (Python Only)

All hooks in `.claude/hooks/` must be written in Python. No bash. Reasons:
- Cross-platform (Windows, macOS, Linux, WSL)
- No shell quoting edge cases
- Easier to test and maintain

Hooks must use only Python stdlib unless the dependency is explicitly documented and widely available.

---

## Code Style

This repo primarily contains Markdown and Python. Follow these conventions:

### Markdown (skills, agents, templates)
- Use YAML frontmatter for metadata fields (name, description, scope)
- Shared components (`.agents/`) must not depend on Claude-only features; Claude-specific frontmatter (`allowed-tools`, `argument-hint`) is allowed but optional to the body's meaning
- Do not tell agents to read `AGENTS.md`; harnesses load it automatically
- Skill `name` must equal its folder name (lowercase, digits, hyphens; no `:`)
- Keep skill prompts actionable and specific
- No emojis unless the user explicitly requested them
- No file > 300 lines
- `description` fields must not exceed 400 characters
- Use `@path/to/file` syntax for absolute file path references in `.md` files (e.g. `@src/main.py`, `@.claude/settings.json`); relative or fuzzy references (e.g. `file.ext`, `skills/`) are fine as-is
- Agents that should auto-trigger must include `Use PROACTIVELY when [specific condition]` in their description — only for agents users would otherwise skip, not for agents users always invoke explicitly
- Agents may be organized in subfolders: `core/` for cross-cutting concerns, `<stack>/` for tech-specific agents

### Python (hooks and skill scripts)
- Scripts a skill needs live in that skill's `scripts/` folder (e.g. `.agents/skills/kc-create-project/scripts/`), never in a top-level `scripts/`; they are copied with the skill
- Type hints on all functions
- Exit code semantics: `0` = allow, `2` = block with message, `1` = warn
- Print blocking reason to `stderr` when exiting with code 2
- No external dependencies without documentation

---

## Workflow

- Work on feature branches — `feat/<name>`, `fix/<name>`, `docs/<name>`
- Keep commits focused: one logical change per commit
- Run `python -m py_compile .claude/hooks/*.py .agents/skills/*/scripts/*.py` to syntax-check hooks and scripts before committing
