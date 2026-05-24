---
name: code-review
description: "Code review expert. ALWAYS use when the user says: review, check, look at, critique, audit, or feedback on code/diff/CL/PR/changes. Also triggers on 'what do you think of this code', 'is this okay', 'anything wrong here', Swarm review URLs, or CL numbers. Finds bugs, security issues, performance problems, and style violations."
allowed-tools: Read, Grep, Glob, Bash(p4 diff:*), Bash(p4 describe:*), Bash(p4 opened:*), Bash(p4 changes:*), Bash(p4 client:*), Agent
---

# Code Review — Orchestrator

**Input:** $ARGUMENTS

## Overview

This skill finds real bugs, not style nitpicks. The goal is to catch issues that would cause production problems: crashes, security holes, data corruption, and performance regressions.

## Step 1 — Resolve the Diff

Resolve the diff from `$ARGUMENTS` using:

@docs/standards/perforce/resolve-diff.md

| Input type | Resolution |
|------------|------------|
| CL number (digits) | `p4 describe -du <CL>` |
| Swarm URL | Extract review ID, get associated CL |
| File path | `p4 diff -du <path>` |
| "pending" or no args | `p4 opened` then latest pending CL |
| System name | Grep/Glob to find files, diff those |

**Output:** The unified diff content and list of files changed.

## Step 2 — Gather Context

Before spawning reviewers, gather context they'll need:

1. **Read full files** — not just the diff lines, but the entire functions/classes being modified
2. **Find callers** — grep for functions that call the modified code
3. **Check related tests** — are there tests for this code? Do they cover the changes?

This context goes to every reviewer. Better context = fewer false positives.

## Step 3 — Spawn Review Agents

Spawn `code-reviewer` agents for each applicable concern. Include ALL spawns in a SINGLE message (parallel execution).

### Concerns and Skip Rules

| Concern | Skip when | Focus |
|---------|-----------|-------|
| **correctness** | Never | Logic errors, edge cases, null derefs, off-by-one |
| **security** | Docs-only | Input validation, injection, auth, secrets |
| **performance** | Docs-only | N+1, tick abuse, allocations, caching |
| **architecture** | Never | SOLID, coupling, size limits, over-engineering |
| **style** | Never | Epic conventions, naming, include order |

Note: `debuggability` and `interface` from the old concern list are now folded into `architecture`.

### Agent Prompt Format

```
Review this diff for **{concern}**.

Load criteria from: project/docs/standards/code/{concern}.md

## Context (read these files to understand the change)
{list of full file paths to read}

## Callers (code that calls into the modified functions)
{grep results showing callers}

## Diff
{full unified diff}

Focus ONLY on {concern}. Other agents handle other aspects.
Verify every finding by reading the actual source file.
```

## Step 4 — Aggregate and Deduplicate

Combine all agent results:

1. **Deduplicate** — same file:line + same issue = keep one
2. **Merge overlapping** — if two agents found the same root cause, combine into one finding
3. **Sort** — CRITICAL first, then WARNING, then INFO

## Step 5 — Re-Verify All Findings

For every CRITICAL and WARNING finding:

1. Read the actual source file at the cited line (not just the diff)
2. Verify the surrounding code doesn't already handle the issue
3. Check if tests exist that would catch this
4. Remove false positives

This step is mandatory and catches most hallucinated findings.

## Step 6 — Output

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
