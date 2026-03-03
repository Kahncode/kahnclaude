---
name: kc:create-agent-skill
description: Create a new agent, skill, or slash command in KahnClaude following framework conventions.
argument-hint: "[describe what you want to create: agent for X, skill for Y, command to Z]"
scope: framework
allowed-tools: Read, Write, Glob, Grep, Bash(ls *)
---

# Create Agent / Skill / Command

## Target

$ARGUMENTS

## Step 1: Determine Component Type

From the argument, identify what to create:
- **Agent** — specialist subagent invoked via the Agent tool (`.claude/agents/`)
- **Skill** — trigger-activated expertise template (`.claude/skills/<name>/SKILL.md`)
- **Command** — slash command workflow (`.claude/commands/` or `.claude/commands/kc/`)

If unclear, ask: "Are you creating an agent, a skill, or a slash command?"

## Step 2: Check for Overlap

```bash
ls .claude/agents/ .claude/agents/core/ .claude/agents/python/ .claude/agents/web/ .claude/agents/mobile/ 2>/dev/null
ls .claude/skills/ 2>/dev/null
ls .claude/commands/ .claude/commands/kc/ 2>/dev/null
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

### Skill format (`.claude/skills/<name>/SKILL.md`)

```markdown
---
name: <kebab-case-name>
description: "<What it does and when to use it>"
[disable-model-invocation: true]
[allowed-tools: [Read, Edit, ...]]
---

# <Skill Title>

<Detailed process, patterns, and expertise Claude should apply>
```

Rules:
- `description` ≤ 400 characters
- Add `disable-model-invocation: true` for skills with side effects or that should only run explicitly
- File ≤ 500 lines

### Command format (`.claude/commands/<name>.md` or `.claude/commands/kc/<name>.md`)

```markdown
---
name: <name>
description: <What it does and when to invoke it>
argument-hint: "[optional argument description]"
scope: project   # or: framework
[disable-model-invocation: true]
[allowed-tools: Bash(git *), Read, ...]
---

# <Command Title>

## $ARGUMENTS handling
...
```

Rules:
- `scope: project` → distributed to target projects
- `scope: framework` → KahnClaude management only, invoked as `/kc:<name>`

## Step 4: Update Docs

After creating the component:
1. Add it to the appropriate table in `README.md`
2. Update counts in the summary table if needed

Ask: "Update README.md? (y/n)"
