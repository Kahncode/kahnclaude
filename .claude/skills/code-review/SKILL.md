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
python project/scripts/code-review/resolve_code_review_dimension.py --batch <dim1>,<dim2>,...
```

Each output line is the absolute path to that dimension's standard file.

### Step 4 — Invoke Review Agents
For each selected dimension:

1. Read the standard file from the path resolved in Step 3
2. Spawn a `code-reviewer` agent via the Agent tool with:
   - The dimension name
   - The absolute path to that dimension's standard file
   - The diff content

The agent's own instructions contain the review philosophy and output format.

### Step 5 — Aggregate Results
Combine all dimension results into a single report. Deduplicate overlapping findings. Sort by severity: CRITICAL first, then WARNING, then INFO.

### Step 6 — Re-Verification Pass
For every CRITICAL finding, re-read the actual source file at the cited line to confirm the issue exists. Remove false positives. This step is mandatory.

### Step 7 — Final Output
Present the consolidated report using the standard output format (see reference).
