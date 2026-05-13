---
name: code-review
description: "Code review orchestrator. ALWAYS invoke when the user asks to review code, a diff, a CL, or a Swarm review. Do not invoke review-code-* sub-skills directly — this skill resolves the diff, selects dimensions, and aggregates findings."
---

# Code Review — Orchestrator

@docs/standards/code/review-philosophy.md

**Input:** $ARGUMENTS

## Instructions

### Step 1 — Resolve the Diff
Invoke the `perforce-resolve-diff` skill with `$ARGUMENTS` to obtain the diff content.

### Step 2 — Select Applicable Dimensions
Inspect the diff and apply each dimension's relevance criteria:

| Dimension | Invoke when |
|-----------|------------|
| correctness | ALWAYS |
| style | ALWAYS |
| readability | ALWAYS |
| pragmatism | ALWAYS |
| solid | ALWAYS |
| ue-best-practice | ALWAYS |
| robustness | ALWAYS |
| pragmatism | ALWAYS |
| debuggability | ALWAYS |
| architecture | New files, import/include changes, class changes, >50 lines, new public API |
| performance | Tick/loops, container ops, allocations, DB/network calls, hot paths |
| interface | Public/protected signatures changed/added, headers modified, >3 params |
| networking | Replicated props, RPCs, GetLifetimeReplicatedProps, HasAuthority, net dormancy |

**MANDATORY:** Dimensions marked "ALWAYS" must be invoked on every review — no exceptions. Skip conditional dimensions only if their criteria clearly do not match.

### Step 3 — Resolve Standard File Paths
For each selected dimension, run the resolver script to get the absolute path:

```bash
python .claude/scripts/code-review/resolve_code_review_dimension.py --batch <dim1>,<dim2>,...
```

Each output line is the absolute path to that dimension's standard file.

### Step 4 — Invoke Review Agents

**CRITICAL RULE: One agent per dimension. NEVER combine dimensions into a single agent.**

For each selected dimension, spawn a **separate** `code-reviewer` agent. This is mandatory.

1. Read the standard file from the path resolved in Step 3
2. For EACH dimension, spawn a distinct `code-reviewer` agent with:
   - `subagent_type: code-reviewer`
   - `description: "Code review: <dimension-name>"`
   - Prompt containing: the dimension name, the standard file content, and the diff

**Parallelization requirement:** Include ALL dimension agent spawns in a SINGLE message so they run concurrently. If you have 5 dimensions, you must have 5 separate Agent tool invocations in one response — not one agent reviewing 5 dimensions.

**Anti-pattern (WRONG):**
> "Review CL 150283 for correctness, style, readability, UE5 best practices, and performance."

**Correct pattern:**
- Agent 1: "Review CL 150283 for **correctness**. [correctness standard] [diff]"
- Agent 2: "Review CL 150283 for **style**. [style standard] [diff]"
- Agent 3: "Review CL 150283 for **readability**. [readability standard] [diff]"
- Agent 4: "Review CL 150283 for **ue-best-practice**. [ue-best-practice standard] [diff]"
- Agent 5: "Review CL 150283 for **performance**. [performance standard] [diff]"

Each agent receives exactly ONE dimension and its corresponding standard document.

### Step 5 — Aggregate Results
Combine all dimension results into a single report. Deduplicate overlapping findings. Sort by severity: CRITICAL first, then WARNING, then INFO.

### Step 6 — Re-Verification Pass
For every CRITICAL finding, re-read the actual source file at the cited line to confirm the issue exists. Remove false positives. This step is mandatory.

### Step 7 — Final Output
Present the consolidated report using the standard output format (see reference).
