---
name: fix-agent-skill
description: Debug a misbehaving agent or skill by analyzing the current session, then audit and fix the component file.
argument-hint: "[agent name, skill name, or path — leave blank to diagnose from session]"
scope: framework
allowed-tools: Read, Edit, Glob, Grep
---

# Fix Agent / Skill

@docs/standards/tools/agent-skill-standard.md

## Target

$ARGUMENTS

**Resolve the target:**

- Agent name → find `.claude/agents/**/<name>.md`
- Skill name → find `.claude/skills/**/<name>/SKILL.md`
- Path → use directly
- Empty → diagnose from session (see Phase 0)

## Phase 0: Session Diagnosis (no target given)

Examine the current conversation:

1. What was the agent or skill supposed to do?
2. What happened instead? (not triggered? wrong output? wrong tools used? error?)
3. Which instruction was missing, wrong, or ambiguous?
4. Which component file is responsible?

If ambiguous, ask: "Which agent or skill misbehaved?"

---

## Phase 1: Audit

Read the file and audit against the appropriate checklist:

### Agent Audit Checklist

- [ ] `name` — kebab-case
- [ ] `description` <= 400 chars
- [ ] `description` includes `Use PROACTIVELY when <condition>` if agent should auto-activate
- [ ] `model: inherit` present (required)
- [ ] No `scope` field (agents never have scope)
- [ ] `tools` list follows minimum-necessary principle:
  - Green (authoring): Read, Write, Edit, Grep, Glob, Bash
  - Blue (review/audit): Read, Grep, Glob only — never Write or Bash
  - Purple (testing): Read, Grep, Glob, Bash
- [ ] `color` follows convention (green = authoring, blue = review, purple = testing)
- [ ] Instructions don't conflict with tool access (e.g. told to edit but only has Read)
- [ ] File <= 300 lines

### Skill Audit Checklist

- [ ] `name` matches directory name, kebab-case
- [ ] `description` <= 400 chars, uses correct directive tier (user-facing / orchestrator / sub-skill)
- [ ] Description has "ALWAYS invoke" + trigger list + negative constraint
- [ ] `disable-model-invocation: true` only if skill has side effects or is explicit-only
- [ ] `allowed-tools` set if specific tools needed (no `Bash(ls *)` — use Glob)
- [ ] No trigger overlap with other skills (Glob `.claude/skills/*/` and check descriptions)
- [ ] `@project/docs/standards/<theme>/<name>.md` reference present if a companion doc exists
- [ ] File <= 100 lines
- [ ] Instructions are clear and actionable

---

## Common Failure Modes

**Agent failures:**
- Missing `Use PROACTIVELY when...` for agents that should auto-trigger
- Overly broad tool access (reviewer with Write/Bash)
- Missing `model: inherit`
- Description too vague to guide agent selection
- Instructions conflict with tool access (e.g. told to edit but only has Read)

**Skill failures:**
- Passive description ("Use when...") instead of directive ("ALWAYS invoke...")
- Missing negative constraint ("Do not X directly")
- Trigger topics too vague or overlapping with another skill
- `disable-model-invocation: true` set when it shouldn't be

---

## Phase 2: Report

```
Component: [name]  ([agent|skill])
Path: [path]

Session Issue:
- [What went wrong and why]
  Fix: [instruction change needed]

Convention Issues:
- [issue] → Fix: [change]
```

## Phase 3: Apply Fixes

Ask:

```
Found [N] issues. How to proceed?
1. Fix all automatically
2. Review each fix
3. Show diff only
4. Cancel
```

Apply with Edit. Read back changed sections to verify.

## Phase 4: Confirm

Summarize changes. DO NOT COMMIT without explicit user confirmation.

> Fixed [N] issues:
>
> - [issue 1]
> - [issue 2]
>
> Commit these changes? (Provide the command, do NOT commit automatically)
>
> ```
> git add [file] && git commit -m "fix: [name] — [summary]"
> ```
