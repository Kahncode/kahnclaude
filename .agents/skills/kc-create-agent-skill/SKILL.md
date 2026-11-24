---
name: kc-create-agent-skill
description: Create a new skill (including slash commands) or agent in KahnClaude following framework conventions.
argument-hint: "[describe what you want to create: agent for X, skill for Y, command to Z]"
scope: project
allowed-tools: Read, Write, Glob, Grep, Bash(ls *)
---

# Create Agent / Skill

## Target

$ARGUMENTS

## Step 1: Determine Component Type

From the argument, identify what to create:

- **Skill** — a shared, harness-neutral workflow or expertise (`.agents/skills/<name>/SKILL.md`). Slash commands are skills too: a user-invoked workflow is a skill with `disable-model-invocation: true`.
- **Agent** — specialist subagent, Claude Code only (`.claude/agents/`)

If unclear, ask: "Are you creating a skill (or slash command), or an agent?"

## Step 2: Check for Overlap

```bash
ls .claude/agents/ .claude/agents/core/ .claude/agents/python/ .claude/agents/web/ .claude/agents/mobile/ 2>/dev/null
ls .agents/skills/ 2>/dev/null
```

If a similar component already exists, ask whether to extend it or create a new one.

## Step 3: Create the File

### Agent format (`.claude/agents/[subfolder/]<name>.md`)

```markdown
---
name: <kebab-case-name>
description: "<What it does>. Use when <specific trigger condition>."
model: inherit
tools: Read, Grep, Glob[, ...]
---

# <Role Title>

<Core instructions — what the agent does, how it thinks, what it produces>

## Guidelines

- <Key constraint or behavior>
- <Key constraint or behavior>
```

Rules:

- `description` ≤ 400 characters, must include "Use when..."
- No `scope` field on agents
- Subfolder: `core/` (cross-cutting), `python/`, `web/`, `mobile/`, or root (universal)
- Claude Code only: `tools`, `model` and `color` are Claude fields; other harnesses do not read this folder

### Skill format (`.agents/skills/<name>/SKILL.md`)

```markdown
---
name: <kebab-case-name>
description: "<What it does and when to use it>"
scope: project   # or: framework
[argument-hint: "[optional argument description]"]
[disable-model-invocation: true]
[allowed-tools: Bash(git *), Read, ...]
---

# <Skill Title>

<Detailed process, patterns, and expertise to apply>

## $ARGUMENTS handling

...
```

Rules:

- `name` must equal the folder name: lowercase letters, digits and hyphens only (no `:`). Skills that manage KahnClaude itself use the `kc-` prefix, e.g. `kc-install`, invoked as `/kc-install`; the prefix does not imply scope.
- `scope: project` → distributed to target projects; `scope: framework` → KahnClaude management only, never copied
- `description` ≤ 400 characters
- Add `disable-model-invocation: true` for skills with side effects or that should only run explicitly
- `argument-hint`, `allowed-tools` and `$ARGUMENTS` are Claude Code extensions; other harnesses ignore them, so the body must still make sense without them (say "the user's argument, if any")
- Do not instruct the agent to read `AGENTS.md`; harnesses load it automatically
- File ≤ 500 lines; bundle long references in the skill folder

## Step 4: Update Docs

After creating the component:

1. Add it to the appropriate table in `README.md`
2. Update counts in the summary table if needed

Ask: "Update README.md? (y/n)"
