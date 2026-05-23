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
3. Run `/code:review` in Claude Code on every file you changed
4. Verify hooks pass syntax check: `py -m py_compile .claude/hooks/*.py`
5. Commit with conventional format: `feat(commands): add review command`

---

## What's Welcome

- New slash commands (`.claude/commands/`)
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
- Run `/code:review` before committing
- Use `@path/to/file` syntax for absolute file path references in `.md` files (e.g. `@src/main.py`); relative or fuzzy references (e.g. `file.ext`) are fine as-is
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

Skills live in `.claude/skills/<theme>/<name>/SKILL.md`. Reference docs and scripts live separately:

```
.claude/skills/
  <theme>/                        # Group by theme: code, perforce, swarm, jira, etc.
    <skill-name>/
      SKILL.md                    # Skill definition (< 100 lines)

project/docs/standards/
  <theme>/
    <skill-name>.md               # Reference doc (criteria, patterns, formats)

project/scripts/
  <domain>/
    <script-name>.py|.ps1         # Reusable scripts for editor/build automation
```

SKILL.md example:

```markdown
---
name: skill-name
description: <Domain> expert. ALWAYS invoke when the user asks about <triggers>. Do not <alternative> directly — use this skill first.
---

@docs/standards/<theme>/<skill-name>.md

## Instructions

What Claude does when this skill activates.
```

### Description Tiers

Skill descriptions use one of three patterns depending on how the skill is invoked:

| Tier | Pattern | When to use |
|------|---------|-------------|
| **User-facing** | `<Domain> expert. ALWAYS invoke when the user asks about <triggers>. Do not <alternative> directly — this skill <value>.` | Skills invoked by user prompts |
| **Orchestrator** | `<Domain> orchestrator. ALWAYS invoke when the user asks to <triggers>. Do not invoke <sub-skills> directly — this skill <routing>.` | Skills that invoke sub-skills |
| **Sub-skill** | `Sub-skill of <orchestrator>. <What it does>. Invoked by the <orchestrator> orchestrator — do not invoke directly.` | Skills invoked only by orchestrators |

**Why:** Research shows directive descriptions ("ALWAYS invoke... Do not X directly") achieve 100% activation vs ~50% for passive descriptions ("Use when..."). Sub-skills use an anti-directive to prevent false activation from user prompts.

- **Line limit:** SKILL.md must be under 100 lines
- **Description limit:** Must not exceed 400 characters
- **Reference docs:** Each skill has a reference doc in `project/docs/standards/<theme>/` with focused criteria, patterns, or formats. Extract from existing coding standards or tech stack guides rather than duplicating. Use `@docs/standards/<theme>/<name>.md` to reference.
- **Scripts:** Reusable scripts live in `project/scripts/<domain>/` (source). After install, they're at `.claude/scripts/<domain>/`. Reference them with `$KC_PROJECT_ROOT/.claude/scripts/<domain>/<script>`.
- **Theme folders:** Group related skills by theme (`code/`, `perforce/`, `swarm/`, `jira/`, `confluence/`, `planning/`, `unreal/`)

### Code Review — Concern-Based Architecture

The `/code-review` skill uses 7 concern-based review categories, each with inline criteria in SKILL.md:

1. Architecture & Design — SOLID, coupling/cohesion, anti-patterns (ALWAYS)
2. Logic & Correctness — edge cases, null checks, race conditions (ALWAYS)
3. Security — input validation, injection, auth (conditional)
4. Performance — N+1, loops, memory leaks (conditional)
5. Maintainability — naming, comments, nesting (ALWAYS)
6. Reuse — existing utilities, over-engineering (conditional)
7. Standards — interface, networking, UE5 best practices (conditional)

Standards files in `project/docs/standards/code/` (interface, networking, ue-best-practice) are read by the Standards concern.

---

## Adding an Agent

Agents live in `.claude/agents/<name>.md`. They can be organized into subfolders:

| Path                               | Use for                                                        |
| ---------------------------------- | -------------------------------------------------------------- |
| `.claude/agents/<name>.md`         | General-purpose agents for any stack                           |
| `.claude/agents/core/<name>.md`    | Cross-cutting concerns (review, testing, docs)                 |
| `.claude/agents/core/<name>.md`    | Stack-specific agents that are broadly useful (e.g. UE5, Python) |

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

| Prefix    | Behavior                                           |
| --------- | -------------------------------------------------- |
| `block-`  | Blocks the operation (exit 2)                      |
| `check-`  | Checks condition, warns or blocks                  |
| `lint-`   | Lints after file write (PostToolUse) or at Stop    |
| `verify-` | Verifies at turn end (Stop)                        |
| `after-`  | Runs post-edit formatting (PostToolUse)            |
| `notify-` | Sends a desktop/system notification (Notification) |
| `force-`  | Injects context on prompt submit (UserPromptSubmit)|

**Required structure:**

```python
#!/usr/bin/env python3
"""
hook-name.py — Brief description.

Event: UserPromptSubmit | PreToolUse | PostToolUse | Stop | Notification
Matcher: Read|Write|Edit|Bash  (PreToolUse/PostToolUse only; none for UserPromptSubmit/Stop/Notification)

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

1. Wire it in `@.claude/settings.json`
2. Document the wiring example in `@global/settings.json`
3. Syntax-check: `py -m py_compile .claude/hooks/your-hook.py`
4. Test with mock stdin: `echo '{"tool_name":"Write","tool_input":{"file_path":".env"}}' | py .claude/hooks/your-hook.py`

---

## Adding a Tech Stack Guide

Guides live in `project/docs/tech-stacks/<name>.md`. Each guide must include:

1. **HTML comment metadata** in the header for detection and prerequisites:
   ```
   <!-- detection: auto|opt-in | signal: <what to look for> | prerequisite: <guide or none> -->
   <!-- prompt: "<question to ask user>" -->
   ```
2. **Setup section** (if env vars needed) — required/optional variable tables
3. **Compact Questions table** — columns: `#`, `Question`, `Answer Format`, `CLAUDE.md Section`
4. **Auto-Detection table** — columns: `#`, `Method`
5. **Operational Reference** — runtime knowledge for Claude (API refs, workflows, tool tables)

Shared boilerplate (all-optional, one-at-a-time, env-vars-in-local) is handled by `/tool:generate-claude-md` — do not repeat it in guides. Read `project/docs/tech-stacks/unreal.md` for a minimal example or `project/docs/tech-stacks/helix_perforce.md` for a full example with setup + reference. Guides are copied to target projects as part of the `project/docs/` tree. After adding a guide, update `README.md` to list it.

---

## Adding Review Criteria or Coding Standards

Coding standards live in `project/docs/standards/` reference docs and agent markdown — not inline in skills.

**Key principle:** Review criteria belong in the relevant `project/docs/standards/<theme>/<name>.md` file. Single-consumer standards belong embedded in their agent file. Multi-consumer standards that don't fit an existing review concern should become a new reference doc in `project/docs/standards/`.

When adding standards content:

1. Add review criteria to the appropriate `project/docs/standards/<theme>/<name>.md`
2. For single-consumer standards, embed directly in the consuming agent
3. Keep reference docs under 150 lines; agent files under 300 lines
4. Update `README.md` if a new skill is created

---

## Updating Templates

### `@project/CLAUDE.md`

Starting point for a new project's `CLAUDE.md`. When editing:

- Keep rules numbered with clear labels
- Append new rules — never remove without discussion
- Each rule must explain **why**, not just what

### `@global/CLAUDE.md`

Installed at `@~/.claude/CLAUDE.md`. Keep it:

- Security and cross-project standards only
- Free of project-specific rules (those belong in `project/CLAUDE.md`)
- Safe to merge into an existing global config without conflicts

---

## Checklist Before Committing

- [ ] Component in correct location (`scope: project` → `.claude/commands/`, `scope: framework` → `.claude/commands/kc/`, skills, agents, hooks in their respective dirs)
- [ ] `README.md` updated with description
- [ ] This file updated if new conventions introduced
- [ ] If hook: syntax-checked (`py -m py_compile`)
- [ ] If hook: wired in `@.claude/settings.json` and `@global/settings.json`
- [ ] No secrets, credentials, or personal data in any file

---

## License

By contributing, you agree your contributions will be licensed under the same license as this project (see [LICENSE](LICENSE)).
