---
name: kc:fix-agent-skill
description: Debug a misbehaving agent or skill by analyzing the current session, then audit and fix the component file.
argument-hint: "[agent name, skill name, or path — leave blank to diagnose from session]"
scope: framework
allowed-tools: Read, Edit, Glob, Grep
---

# Fix Agent / Skill

## Target

$ARGUMENTS

**Resolve the target:**
- Agent name → find `.claude/agents/**/<name>.md`
- Skill name → find `.claude/skills/<name>/SKILL.md`
- Path → use directly
- Empty → diagnose from session (see Phase 0)

## Phase 0: Session Diagnosis (no target given)

Look at the current conversation to understand what went wrong:

1. What was the agent or skill supposed to do?
2. What did it actually do instead?
3. Which instruction was missing, wrong, or ambiguous?
4. Which component file is responsible?

Identify the file. If ambiguous, ask: "Which agent or skill misbehaved?"

## Phase 1: Audit

Read the file and check against KahnClaude conventions.

**Agent checklist:**
- [ ] `name` field — lowercase-with-hyphens
- [ ] `description` ≤ 400 chars, includes "Use when..." trigger
- [ ] `model: inherit` present
- [ ] No `scope` field
- [ ] Instructions are clear and actionable

**Skill checklist:**
- [ ] `name` matches directory name, lowercase-with-hyphens
- [ ] `description` ≤ 400 chars, describes what + when
- [ ] `disable-model-invocation: true` if it has side effects
- [ ] `allowed-tools` set if specific tools are needed
- [ ] File ≤ 500 lines
- [ ] Instructions are clear and actionable

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

After fixes, offer to commit:
`git add [file] && git commit -m "fix: [name] — [summary]"`
