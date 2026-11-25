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
4. Verify hooks pass syntax check: `python -m py_compile .claude/hooks/*.py .agents/skills/*/scripts/*.py`
5. Commit with conventional format: `feat(skills): add review skill`

---

## What's Welcome

- New skills and slash commands (`.agents/skills/<name>/SKILL.md`)
- New agents (`.claude/agents/`)
- New hooks (`.claude/hooks/`)
- Improvements to `global/CLAUDE.md` or `project/AGENTS.md`
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
- Use `@path/to/file` syntax for absolute file path references in `.md` files (e.g. `@src/main.py`); relative or fuzzy references (e.g. `file.ext`) are fine as-is
- See `AGENTS.md` for the full standards

---

## Adding a Skill (or Slash Command)

Skills follow the Agent Skills format and are shared by every harness (Claude Code, Codex, OpenCode, pi). A slash command is a skill. Each skill is a folder `.agents/skills/<name>/SKILL.md` (plus any bundled files). **Never edit `.claude/skills/`: it is a gitignored projection created by the `.claude/hooks/link_skills.py` SessionStart hook.**

| Scope       | Location                              | Invocation   | Meaning                                  |
| ----------- | ------------------------------------- | ------------ | ---------------------------------------- |
| `project`   | `.agents/skills/<name>/SKILL.md`      | `/<name>`    | Installed into target projects.          |
| `framework` | `.agents/skills/<name>/SKILL.md`      | `/<name>`    | Framework management only. Never copied. |

```markdown
---
name: skill-name
description: What this skill does and when to use it
scope: project
disable-model-invocation: true
---

Instructions in imperative form. The user's argument, if any, follows the skill name.
```

- `name` must equal the folder name: lowercase letters, digits and hyphens (no `:`)
- Add `disable-model-invocation: true` for workflows with side effects that should only run when the user invokes them
- Claude-only frontmatter (`allowed-tools`, `argument-hint`) and `$ARGUMENTS` are allowed but ignored by other harnesses; the body must remain understandable without them
- Do not tell the agent to read `AGENTS.md`; harnesses load it automatically
- Description must be specific enough to avoid false activations
- Skills that manage KahnClaude itself use the `kc-` prefix (e.g. `/kc-install`); the prefix does not imply scope
- **Naming:** kebab-case, start with an action verb for workflows (`review`, `commit`, `refactor`)
- **Description limit:** must not exceed 400 characters
- **After adding:** update `README.md` (component listing) and this file if you introduced new conventions

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

Only add a hook for something Claude Code does not do natively. Safety rules go in `permissions.deny` in `project/settings.json` (avoid `ask` rules: they force a prompt even in auto mode); linting, formatting, secret scanning and branch policy belong to each project's git hooks and CI, not KahnClaude.

**Naming:** kebab-case describing the behavior; prefix `block-` when the hook denies or asks. `link_skills.py` keeps its snake_case name because skills invoke it as a script.

**Exit codes and output (Claude Code semantics):**

| Code | Effect |
| ---- | ------ |
| `0`  | Proceed. Print JSON on stdout to steer Claude: PreToolUse `hookSpecificOutput.permissionDecision` (`allow`/`deny`/`ask`) with `permissionDecisionReason`; PostToolUse/Stop `{"decision": "block", "reason": ...}`; `hookSpecificOutput.additionalContext` to inject context |
| `2`  | Block; stderr is fed back to Claude. On Stop this forces Claude to continue: check `stop_hook_active` to avoid loops |
| other | Non-blocking error shown to the user only; Claude never sees it. Never use `1` to "warn" |

A missing hook script makes `python3` exit 2, which blocks every matching tool call. When removing a hook, remove its wiring from every `settings.json` first.

**Required structure:**

```python
#!/usr/bin/env python3
"""
hook-name.py — Brief description.

Event: PreToolUse | PostToolUse | Stop | Notification | SessionStart
Matcher: Edit|Write|Bash  (tool events only)

Exit codes:
  0 — Proceed (decision, if any, returned as JSON on stdout)
  2 — Block (reason on stderr, fed back to Claude)
"""
import json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})

    # Your logic here. To ask the user:
    # print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
    #     "permissionDecision": "ask", "permissionDecisionReason": "why"}}))
    # To block: print("BLOCKED: reason", file=sys.stderr); sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

**After adding a hook:**

1. Wire it in `@.claude/settings.json`
2. Wire it in `@project/settings.json` (`$CLAUDE_PROJECT_DIR/.claude/hooks/...`) and, if it is useful globally, in `@global/settings.json` (`~/.claude/hooks/...`)
3. Syntax-check: `python -m py_compile .claude/hooks/your-hook.py`
4. Test with mock stdin: `echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/x"}}' | python3 .claude/hooks/your-hook.py`

---

## Adding a Tech Stack Guide

AGENTS.md generation templates and guides live in `project/` — the master template at `project/AGENTS.md` and per-stack Q&A guides in `project/tech-stacks/<name>.md` (e.g., `unreal.md`). Read `project/tech-stacks/unreal.md` for an example of the expected structure: detection pattern, numbered questions with AGENTS.md section mappings, and rationale for each question. Guides are Markdown only and are used by `/kc-generate-agents-md` from the KahnClaude source directory; they are never copied to target projects. After adding a guide, update `README.md` to list it.

**Create Project section (optional):** a guide that adds a `## Create Project` section becomes available to `/kc-create-project`. It must list, as literal bold-labelled bullets: the init command per package manager (non-interactive, no install, no git, `<target>` placeholder; write `none` when the stack has no scaffolder and the template repo is the whole project), `Template repo` (git URL of a functional, opinionated project; it overlays the init output, and the guide's `Auto-detection` rules are run against the result to skip already-answered questions, so keep those rules accurate), `Template ref`, `Default package manager` (the language's own default, e.g. npm for Node; never assume an alternative) and `Post-init` steps. Verify init flags against current docs (Context7) when adding or changing one. Helper scripts live in the skill's own folder (`.agents/skills/kc-create-project/scripts/`) (Python, stdlib only, type hints, cross-platform) and must pass `python -m py_compile`.

---

## Updating Templates

### `@project/AGENTS.md`

Starting point for a new project's `AGENTS.md` (`project/CLAUDE.md` is only the one-line `@AGENTS.md` shim). When editing:

- Keep rules numbered with clear labels
- Append new rules — never remove without discussion
- Each rule must explain **why**, not just what

### `@global/CLAUDE.md`

Installed at `@~/.claude/CLAUDE.md`. Keep it:

- Security and cross-project standards only
- Free of project-specific rules (those belong in `project/AGENTS.md`)
- Safe to merge into an existing global config without conflicts

---

## Checklist Before Committing

- [ ] Component in correct location (skills and slash commands in `.agents/skills/` with `kc-` prefix for `scope: framework`; agents and hooks in `.claude/`)
- [ ] `README.md` updated with description
- [ ] This file updated if new conventions introduced
- [ ] If hook: syntax-checked (`python -m py_compile`)
- [ ] If hook: wired in `@.claude/settings.json` and `@global/settings.json`
- [ ] No secrets, credentials, or personal data in any file

---

## License

By contributing, you agree your contributions will be licensed under the same license as this project (see [LICENSE](LICENSE)).
