# Contributing to KahnClaude

---

## Reporting Issues

Use GitHub Issues. Include:

- Claude Code version (`claude --version`)
- OS and shell environment (Windows, WSL2, macOS, Linux)
- Steps to reproduce
- Expected vs actual behavior

---

## Submitting Changes

1. Create a branch from `main` (`git checkout -b feat/your-change`)
2. Make your changes
3. Run `/review` in Claude Code on every file you changed
4. Verify hooks pass syntax check: `python -m py_compile .claude/hooks/*.py`
5. Commit with conventional format: `feat(commands): add review command`

---

## What's Welcome

- New slash commands (`.claude/commands/`)
- New skills (`.claude/skills/<name>/SKILL.md`)
- New agents (`.claude/agents/`)
- New hooks (`.claude/hooks/`)
- Improvements to `global/CLAUDE.md` or `project/CLAUDE.md`
- Documentation improvements

## What's NOT Welcome

- Bash or DOS scripts — Python only, always
- External library dependencies in hooks without documentation
- Removing existing rules without opening an issue first
- Stack-specific opinions baked into generic components (keep it language-agnostic where possible)
- Large refactors without prior discussion

---

## Code Style

- Python strict typing for all hook scripts. NO BASH OR DOS.
- No file > 300 lines, no function > 50 lines
- Hooks use stdlib only unless dependency is clearly documented
- Run `/review` before committing
- See `CLAUDE.md` for the full standards

---

## Adding a Slash Command

Commands are Markdown files with YAML frontmatter. **Location depends on scope:**

| Scope       | Location                        | Invocation   | Meaning                                  |
| ----------- | ------------------------------- | ------------ | ---------------------------------------- |
| `project`   | `.claude/commands/<name>.md`    | `/<name>`    | Installed into target projects.          |
| `framework` | `.claude/commands/kc/<name>.md` | `/kc:<name>` | Framework management only. Never copied. |

Project command example:

```markdown
---
name: command-name
description: One-line description of what this command does
scope: project
---

Your command prompt here. Write in imperative form — instructions Claude follows
when the user runs `/command-name`.
```

Framework command example (inside `.claude/commands/kc/`):

```markdown
---
name: command-name
description: One-line description of what this command does
scope: framework
---

Your command prompt here. Invoked as `/kc:command-name`.
```

**Naming:** kebab-case, start with an action verb (`review`, `commit`, `check-`, `refactor`).

**Description limit:** Must not exceed 400 characters.

**After adding:** Update `README.md` (component listing) and this file if you introduced new conventions.

---

## Adding a Skill

Skills live in `.claude/skills/<name>/SKILL.md`:

```markdown
---
name: skill-name
description: What this skill does
triggers:
  - keyword one
  - keyword two
---

# Skill: Name

Structured template Claude follows when trigger keywords are detected in conversation.
```

- Trigger keywords must be specific enough to avoid false activations
- Each skill gets its own subdirectory: `.claude/skills/code-review/SKILL.md`
- **Description limit:** Must not exceed 400 characters.

---

## Adding an Agent

Agents live in `.claude/agents/<name>.md`. They can be organized into subfolders:

| Path                               | Use for                                                        |
| ---------------------------------- | -------------------------------------------------------------- |
| `.claude/agents/<name>.md`         | General-purpose agents for any stack                           |
| `.claude/agents/core/<name>.md`    | Cross-cutting concerns (review, testing, docs)                 |
| `.claude/agents/<stack>/<name>.md` | Tech-stack specific agents (e.g. `react/`, `django/`, `rust/`) |

```markdown
---
name: agent-name
description: What this specialist does. Use PROACTIVELY when [condition].
tools:
  - Read
  - Grep
  - Glob
---

# Agent: Name

You are a specialist in [domain]. Your job is to [specific goal].

[Behavioral instructions, output format, constraints]
```

- **Tool access principle:** Default to minimum necessary. Reviewers get `Read/Grep/Glob` only — never `Write` or `Bash`.
- **Description limit:** Must not exceed 400 characters.
- **Proactive agents:** Only add `Use PROACTIVELY when [condition]` to agents that would otherwise be skipped — e.g. a reviewer that should run after every feature. Do NOT add it to agents users will always invoke explicitly (test writers, scaffolders). The condition must be specific.
- **Color:** Keep the following convention, you may create unique shades to differenciate: green for authoring code, blue for review, research or audit, purple for testing.

---

## Adding a Hook

Hooks live in `.claude/hooks/<name>.py`. **Python only — no bash.**

**Naming conventions:**

| Prefix    | Behavior                             |
| --------- | ------------------------------------ |
| `block-`  | Blocks the operation (exit 2)        |
| `check-`  | Checks condition, warns or blocks    |
| `lint-`   | Lints after file write (PostToolUse) |
| `verify-` | Verifies at turn end (Stop)          |

**Required structure:**

```python
#!/usr/bin/env python3
"""
hook-name.py — Brief description.

Event: PreToolUse | PostToolUse | Stop
Matcher: Read|Write|Edit|Bash  (PreToolUse/PostToolUse only)

Exit codes:
  0 — Allow / no action
  1 — Warning (printed, continues)
  2 — Block (printed to stderr, operation stopped)
"""
import json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})

    # Your logic here.
    # To block: print("BLOCKED: reason", file=sys.stderr); sys.exit(2)


if __name__ == "__main__":
    main()
```

**After adding a hook:**

1. Wire it in `.claude/settings.json`
2. Document the wiring example in `global/settings.json`
3. Syntax-check: `python -m py_compile .claude/hooks/your-hook.py`
4. Test with mock stdin: `echo '{"tool_name":"Write","tool_input":{"file_path":".env"}}' | python3 .claude/hooks/your-hook.py`

---

## Updating Templates

### `project/CLAUDE.md`

Starting point for a new project's `CLAUDE.md`. When editing:

- Keep rules numbered with clear labels
- Append new rules — never remove without discussion
- Each rule must explain **why**, not just what

### `global/CLAUDE.md`

Installed at `~/.claude/CLAUDE.md`. Keep it:

- Security and cross-project standards only
- Free of project-specific rules (those belong in `project/CLAUDE.md`)
- Safe to merge into an existing global config without conflicts

---

## Checklist Before Committing

- [ ] Component in correct location (`scope: project` → `.claude/commands/`, `scope: framework` → `.claude/commands/kc/`, skills, agents, hooks in their respective dirs)
- [ ] `README.md` updated with description
- [ ] This file updated if new conventions introduced
- [ ] If hook: syntax-checked (`python -m py_compile`)
- [ ] If hook: wired in `.claude/settings.json` and `global/settings.json`
- [ ] No secrets, credentials, or personal data in any file

---

## License

By contributing, you agree your contributions will be licensed under the same license as this project (see [LICENSE](LICENSE)).
