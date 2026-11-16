---
name: code-review
description: "Code review expert. ALWAYS use when the user says: review, check, look at, critique, audit, or feedback on code/CL/PR/changes. Also triggers on 'what do you think of this code', 'is this okay', 'anything wrong here', Swarm review URLs, or CL numbers. Finds bugs, security issues, performance problems, and style violations."
allowed-tools: Read, Grep, Glob, Bash(p4 describe:*), Bash(p4 opened:*), Bash(p4 changes:*), Bash(p4 client:*), Agent
---

# Code Review — Orchestrator

**Input:** $ARGUMENTS

## Overview

This skill finds real bugs, not style nitpicks. The goal is to catch issues that would cause production problems: crashes, security holes, data corruption, and performance regressions.

## Step 1 — Identify Target (NO DIFFS)

Resolve the review target from `$ARGUMENTS`:

| Input | Resolution |
|-------|------------|
| CL number | Use directly |
| Swarm URL | Extract CL from review URL |
| No args | `p4 opened` → latest pending CL |

Run exactly ONE command: `p4 describe -s <CL>` (summary only) to get the file paths.

**Stop here.** Do NOT:
- Run `p4 describe -du` (no unified diff)
- Run `p4 diff` on any file
- Use the Read tool on source files
- Fetch diff content in any other way

The code-reviewer agents gather their own diffs. They have P4 access and know what context they need. Gathering diffs here wastes tokens and context.

## Step 2 — Spawn Review Agents

Spawn `code-reviewer` agents for **all** concerns. Include ALL spawns in a SINGLE message (parallel execution).

**Exception, tiny diff:** 1 file and at most 80 changed lines (check with `p4 describe -s` / `p4 opened` file count and `p4 diff -ds` line counts, not the diff body) → spawn ONE `code-reviewer` covering every concern in the table below.

### Concerns

| Concern | Focus |
|---------|-------|
| **correctness** | Logic errors, edge cases, null derefs, off-by-one |
| **regression** | Breaks existing callers, saved assets, replication, Blueprints |
| **security** | Input validation, injection, auth, secrets |
| **performance** | N+1, tick abuse, allocations, caching |
| **architecture** | SOLID, coupling, size limits, over-engineering |
| **style** | Epic conventions, naming, include order |

### Agent Prompt Format

```
Review for **{concern}**. Load criteria from docs/standards/code/{concern}.md (and {{PROJECT_NOTES_DIR}}\standards-code-{concern}.md if it exists)

Target: CL {number}
Files: {file paths in the change}

Gather the diff yourself using `p4 describe -du {CL}` or `p4 diff -du {path}`.
Focus ONLY on {concern}. Verify findings against actual source.
```

## Step 3 — Aggregate Results

Combine all agent results:

1. **Group by severity** — C first, then W, M, S, I
2. **Dedupe** — same file:line + same issue = keep one
3. **Flag conflicts** — if agents disagree on same line, mark for Step 4

## Step 4 — Resolve Conflicts (Only If Needed)

Skip this step unless two agents report contradictory findings about the same code (e.g., one says "null deref" and another says "already guarded").

If conflicts exist: read the source at the cited line, determine which agent is correct, drop the false positive.

## Step 5 — Output

Use a compact, scannable format. No narrative — just findings.

```
## CL 12345 — X critical, Y warnings

C file.cpp:42 — issue in ≤10 words
  Fix: one-line fix hint or short code snippet

W file.cpp:99 — issue in ≤10 words
  Fix: one-line fix hint

W file.h:15 — issue
  Fix: hint

BLOCK | APPROVE WITH FIXES | APPROVE
```

### Format Rules

- **Header:** `## CL {number} — {counts}` — one line, no summary paragraph
- **Severity prefix:** `C` critical, `W` warning, `M` minor, `S` suggestion, `I` info
- **Finding:** `{prefix} {file}:{line} — {issue}` — issue ≤10 words
- **Fix:** indented, one line when possible; multi-line only for non-obvious fixes
- **No sections:** flat list sorted by severity, no `### CRITICAL` headers
- **No narrative:** no "let me verify", no "I found", no status updates
- **Recommendation:** single word/phrase at the end

## What NOT to Flag

- Pre-existing bugs in untouched code — *unless* this change breaks that code
  (a regression finding is anchored to the change, even when the symptom
  surfaces in an untouched caller, asset, or Blueprint)
- Style preferences not in project standards
- Speculative "might be slow" without evidence
- TODOs or future improvements unrelated to the change
