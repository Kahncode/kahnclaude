# Agent & Skill Standards

Shared conventions for creating and auditing KahnClaude agents and skills.

---

## Skill Conventions

### File Structure

```
.claude/skills/<theme>/<skill-name>/SKILL.md    # Skill definition (< 100 lines)
project/docs/standards/<theme>/<name>.md         # Reference doc (criteria, patterns)
```

### Frontmatter

```yaml
---
name: kebab-case-name                  # Must match directory name
description: "..."                     # <= 400 chars, directive tone (see below)
disable-model-invocation: true         # Only if skill has side effects or explicit-only
allowed-tools: Read, Edit, Bash(...)   # Only if skill needs specific tools
---
```

### Description Tiers (Directive Format)

Research shows directive descriptions achieve 100% auto-activation vs ~50% for passive.

| Tier | Pattern | When |
|------|---------|------|
| **User-facing** | `<Domain> expert. ALWAYS invoke when the user asks about <triggers>. Do not <alternative> directly -- this skill <value>.` | Invoked by user prompts |
| **Orchestrator** | `<Domain> orchestrator. ALWAYS invoke when the user asks to <triggers>. Do not invoke <sub-skills> directly -- this skill <routing>.` | Invokes sub-skills |
| **Sub-skill** | `Sub-skill of <orchestrator>. <What it does>. Invoked by the <orchestrator> orchestrator -- do not invoke directly.` | Invoked only by orchestrators |

**Components of a directive description:**

1. **Domain identifier** -- e.g. "Code review expert", "Perforce sync expert"
2. **ALWAYS invoke** -- directive keyword, not "Use when" (that's a suggestion)
3. **Trigger topic list** -- comprehensive but not exhaustive
4. **Negative constraint** -- "Do not [what Claude would do instead] directly"

**Why it works:** "ALWAYS invoke" alone: Claude might still bypass for "simple" tasks. "Do not X" alone: Claude doesn't know what to do instead. Together: unambiguous instruction with blocked escape path.

**Anti-pattern -- passive descriptions that fail:**

```yaml
# BAD (37-50% activation):
description: "Docker expert for containerization. Use when creating Dockerfiles."

# GOOD (100% activation):
description: "Docker expert. ALWAYS invoke when the user asks about Docker, Dockerfiles, or containers. Do not write Dockerfiles directly -- use this skill first."
```

**Avoid trigger overlap:** If two skills claim the same keywords, Claude may become confused. Ensure trigger topics don't collide across skills. Use distinct verbs (e.g. "compile" vs "implement").

### Body Structure

```markdown
@docs/standards/<theme>/<name>.md    # Reference doc (if applicable)

## Instructions

Step-by-step process Claude follows when the skill activates.
```

### Checklist

- [ ] `name` matches directory name, kebab-case
- [ ] `description` <= 400 chars, uses correct directive tier
- [ ] `disable-model-invocation: true` if side effects or explicit-only
- [ ] `allowed-tools` set if specific tools needed
- [ ] File <= 100 lines
- [ ] Instructions are clear and actionable
- [ ] No trigger overlap with existing skills

---

## Agent Conventions

### File Structure

```
.claude/agents/<subfolder>/<name>.md    # Agent definition
```

Subfolders: `core/` (cross-cutting), or stack-specific (e.g. `web/`, `mobile/`)

### Frontmatter

```yaml
---
name: kebab-case-name
description: "<What it does>. Use PROACTIVELY when <specific trigger>."
model: inherit
tools: Read, Grep, Glob, ...
color: green|blue|purple    # green=authoring, blue=review/audit, purple=testing
---
```

### Description Rules

- <= 400 characters
- No `scope` field on agents
- Only add `Use PROACTIVELY when [condition]` for agents that would otherwise be skipped
- Agents users always invoke explicitly do NOT need proactive triggers

### Body Structure

```markdown
# <Role Title>

<Core identity -- what the agent is, what it produces>

## Workflow / Guidelines

Step-by-step process or behavioral constraints.
```

### Tool Access Principle

Default to minimum necessary:
- **Reviewers/auditors:** `Read, Grep, Glob` only -- never `Write` or `Bash`
- **Developers:** `Read, Write, Edit, Grep, Glob, Bash`

### Checklist

- [ ] `name` -- kebab-case
- [ ] `description` <= 400 chars, includes proactive trigger if needed
- [ ] `model: inherit` present
- [ ] No `scope` field
- [ ] `tools` list follows minimum-necessary principle
- [ ] `color` follows convention (green/blue/purple)
- [ ] Instructions are clear and actionable
- [ ] File <= 300 lines
