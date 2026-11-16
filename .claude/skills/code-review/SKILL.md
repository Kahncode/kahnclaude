---
name: code-review
description: "Code review expert. ALWAYS use when the user says: review, check, look at, critique, audit, or feedback on code/CL/PR/changes. Also triggers on 'what do you think of this code', 'is this okay', 'anything wrong here', Swarm review URLs, or CL numbers. Finds bugs, security issues, performance problems, and style violations."
allowed-tools: Read, Grep, Glob, Bash(p4 describe:*), Bash(p4 opened:*), Bash(p4 changes:*), Bash(p4 client:*), Agent
---

# Code Review — Orchestrator

**Input:** $ARGUMENTS

## Overview

This skill finds real bugs, not style nitpicks. The goal is to catch issues that would cause production problems: crashes, security holes, data corruption, and performance regressions.

## Step 1 — Gather Context

Resolve the review target from `$ARGUMENTS`:

| Input | Action |
|-------|--------|
| CL number | `p4 describe -du <CL>` |
| Swarm URL | Extract CL from review |
| No args | `p4 opened` → latest pending CL |

Then gather:
1. **File list** — all files in the change
2. **Callers** — grep for functions that call modified code

## Step 2 — Spawn Review Agents

Spawn `code-reviewer` agents for **all** concerns. Include ALL spawns in a SINGLE message (parallel execution).

### Concerns

| Concern | Focus |
|---------|-------|
| **correctness** | Logic errors, edge cases, null derefs, off-by-one |
| **security** | Input validation, injection, auth, secrets |
| **performance** | N+1, tick abuse, allocations, caching |
| **architecture** | SOLID, coupling, size limits, over-engineering |
| **style** | Epic conventions, naming, include order |

### Agent Prompt Format

```
Review for **{concern}**. Load criteria from docs/standards/code/{concern}.md

Target: {CL number | Swarm URL | file/folder path}
Files: {file paths to review}
Callers: {grep results}

Focus ONLY on {concern}. Verify findings against actual source.
```

## Step 3 — Aggregate and Deduplicate

Combine all agent results:

1. **Deduplicate** — same file:line + same issue = keep one
2. **Merge overlapping** — if two agents found the same root cause, combine into one finding
3. **Sort** — CRITICAL first, then WARNING, then INFO

## Step 4 — Re-Verify All Findings

For every CRITICAL and WARNING finding:

1. Read the actual source file at the cited line 
2. Verify the surrounding code doesn't already handle the issue
3. Check if tests exist that would catch this
4. Remove false positives

This step is mandatory and catches most hallucinated findings.

## Step 5 — Output

```markdown
## Code Review: [CL description or file summary]

### Summary
[1-2 sentences: overall risk level, most important finding, recommendation]

### CRITICAL (X)
[Each finding with file:line, issue, why it matters, and specific fix code]

### WARNING (Y)
[Each finding with file:line, issue, why it matters, and specific fix code]

### MINOR (Z)
[Style/naming issues introduced by this change — should fix, not blockers]

### SUGGESTION (A)
[Improvement ideas — optional, take it or leave it]

### INFO (W)
[Pre-existing issues only — context, not actionable]

---
**Stats:** X critical, Y warnings, Z minor, A suggestions, W info across N files.
**Recommendation:** [BLOCK / APPROVE WITH FIXES / APPROVE]
```

### Finding Format

Each finding must include:

```
**[SEVERITY]** file/path.cpp:42

Issue: [What's wrong in one sentence]

Why: [Concrete consequence — what breaks if not fixed]

Fix:
```cpp
// Replace this:
OldCode();
// With this:
NewCode();
```
```

No vague descriptions. Every fix must be actual code the developer can copy-paste.

## What NOT to Flag

- Pre-existing code that wasn't touched by this change
- Style preferences not in project standards
- Speculative "might be slow" without evidence
- TODOs or future improvements unrelated to the change
