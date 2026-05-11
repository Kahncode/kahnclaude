---
name: create-agent-skill
description: Create a new agent, skill, or slash command in KahnClaude following framework conventions.
argument-hint: "[describe what you want to create: agent for X, skill for Y, command to Z]"
scope: project
allowed-tools: Read, Write, Glob, Grep, Bash(ls *)
---

# Create Agent / Skill / Command

@docs/standards/tools/agent-skill-standard.md

## Target

$ARGUMENTS

## Step 1: Determine Component Type

From the argument, identify what to create:

- **Agent** — specialist subagent invoked via the Agent tool (`.claude/agents/`)
- **Skill** — trigger-activated expertise template (`.claude/skills/<theme>/<name>/SKILL.md`)
- **Command** — slash command workflow (`.claude/commands/` or `.claude/commands/kc/`)

If unclear, ask: "Are you creating an agent, a skill, or a slash command?"

## Step 2: Check for Overlap

```bash
ls .claude/agents/ .claude/agents/core/ 2>/dev/null
ls .claude/skills/ 2>/dev/null
ls .claude/commands/ .claude/commands/kc/ 2>/dev/null
```

If a similar component already exists, ask whether to extend it or create a new one.

---

## Step 3: Create the File

### Agent

**Understand the agent:**
- **Specialist role** — what domain expertise does this agent have?
- **Proactive trigger** — should it auto-activate? Only if users would otherwise skip it.
- **Tool access** — minimum necessary (reviewers: Read/Grep/Glob; developers: + Write/Edit/Bash)
- **Subfolder** — `core/` for cross-cutting, or stack-specific (e.g. `web/`, `ue5/`)

If unclear, ask one question to clarify.

**Color and tool access:**

| Color | Role | Tool Access |
|-------|------|-------------|
| **Green** | Authoring code or assets | Read, Write, Edit, Grep, Glob, Bash |
| **Blue** | Review, research, audit | Read, Grep, Glob (never Write or Bash) |
| **Purple** | Testing | Read, Grep, Glob, Bash |

Add MCP tools only when the agent's workflow requires them.

**Create file** at `.claude/agents/<subfolder>/<name>.md`:

```markdown
---
name: <kebab-case>
description: "<What it does>. Use PROACTIVELY when <trigger>."    # <= 400 chars
model: inherit                                                     # Required
tools: <minimum necessary>
color: <green|blue|purple>
---

# <Role Title>

<Core identity — what the agent is, what it produces>

## Workflow

<Step-by-step process or behavioral constraints>
```

**Verify:**
- `model: inherit` present (required)
- No `scope` field (agents never have scope)
- Description <= 400 chars
- Tool list follows minimum-necessary principle
- File <= 300 lines

---

### Skill

**Understand the skill:**
- **Domain** — what area does this skill cover?
- **Trigger topics** — what user prompts should activate it?
- **Alternative action** — what would Claude do instead without this skill?
- **Theme folder** — which `.claude/skills/<theme>/` group?
- **Reference doc** — does this skill need a companion doc in `project/docs/standards/<theme>/`?

If unclear, ask one question to clarify.

**Determine description tier:**

| Tier | Pattern | When |
|------|---------|------|
| **User-facing** | `<Domain> expert. ALWAYS invoke when the user asks about <triggers>. Do not <alternative> directly — this skill <value>.` | Invoked by user prompts |
| **Orchestrator** | `<Domain> orchestrator. ALWAYS invoke when the user asks to <triggers>. Do not invoke <sub-skills> directly — this skill <routing>.` | Invokes sub-skills |
| **Sub-skill** | `Sub-skill of <orchestrator>. <What it does>. Invoked by the <orchestrator> orchestrator — do not invoke directly.` | Invoked only by orchestrators |

Trigger topics must not collide across skills.

**Create file** at `.claude/skills/<theme>/<name>/SKILL.md`:

```markdown
---
name: <kebab-case>                         # Must match directory name
description: "<directive description>"     # <= 400 chars, correct tier
[disable-model-invocation: true]           # Only if side effects or explicit-only
[allowed-tools: Read, Edit, Bash(...)]     # Only if specific tools needed
---

# <Skill Title>

@docs/standards/<theme>/<name>.md          # Reference doc (if applicable)

**Input:** $ARGUMENTS

## Instructions

<Step-by-step process>
```

If the skill needs a reference doc, also create `project/docs/standards/<theme>/<name>.md`.

**Verify:**
- Description <= 400 chars
- File <= 100 lines
- Name matches directory
- No trigger overlap with existing skills

---

### Command

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

- `scope: project` → distributed to target projects
- `scope: framework` → KahnClaude management only, invoked as `/kc:<name>`

---

## Step 4: Update Docs

After creating the component:

1. Add it to the appropriate table in `README.md`
2. Update counts in the summary table if needed

Ask: "Update README.md? (y/n)"
