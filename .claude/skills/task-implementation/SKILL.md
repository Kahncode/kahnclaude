---
name: task-implementation
description: "Unified implementation orchestrator. ALWAYS invoke when the user asks to implement, build, or modify C++ code, Blueprint assets, or both, and right after the user approves a plan-mode plan that changes C++ or Blueprints (pass the plan file path). Do not invoke sub-agents directly — this skill routes to the correct agents and drives the full implement-test-review-shelve cycle."
allowed-tools: Agent, Read, Grep, Glob, Skill, ToolSearch, AskUserQuestion, mcp__atlassian__*
---

# Unified Implementation Workflow

Use PROACTIVELY when the user says: `implement this`, `implement feature`, `build this`, `code this up`, `modify blueprint`, `implement task`, or approves a plan in plan mode. With an approved plan, pass its file path as the plan and skip 2b.

**Input:** $ARGUMENTS

**Plan mode still on** (a plan was rejected, then this skill was typed): call ExitPlanMode with the plan file first; agents spawned in plan mode can only read. Never resume an agent started in plan mode; spawn a fresh one.

## 0. Ticket Setup

If the input contains a Jira ticket reference (e.g., `{{JIRA_PROJECT_KEY}}-123`):

### 0a. Get Ticket Content
1. Use `mcp__atlassian__getJiraIssue` with:
   - `fields: ["summary", "status", "description", "assignee"]`
2. Extract the implementation plan from description

### 0b. Mark In Progress
1. Call `mcp__atlassian__getTransitionsForJiraIssue` and pick the transition named `In Progress`; IDs differ per workflow. Then `mcp__atlassian__transitionJiraIssue` with that ID
2. If transition fails, warn the user but continue

Skip if: no ticket reference, or user says "don't update Jira".

Project specifics: read {{PROJECT_NOTES_DIR}}\task-implementation.md if it exists.

## 1. Classify Work Type

From the input, determine:
- **cpp** — C++ files only -> code-dev + code-reviewer
- **tests** — only files under `{{UE_PROJECT_DIR}}\Source\{{UE_TEST_MODULE}}\` -> test-dev + code-reviewer (the cpp flow with test-dev in place of code-dev; no planner fan-out)
- **blueprint** — Blueprint assets only -> blueprint-dev + blueprint-reviewer
- **both** — C++ and Blueprint -> all four agents, C++ first

If unclear, ask: "Does this involve C++ code, Blueprint assets, or both?"

## 2. C++ Track (if cpp, tests or both)

**tests:** skip 2a-2d; delegate to one `test-dev` (as 2e, with test-dev for code-dev). Test files in a `cpp`/`both` task also go to test-dev, never code-dev (Stage 3c).

Two facts shape this stage. All agents share one Perforce workspace (no worktrees), so two agents in the same file overwrite or invalidate each other's edits. UBT is single-instance and compiles whatever is on disk, so a build during a fan-out queues on the mutex and then fails on other agents' half-written files. Parallel code-devs therefore write code in disjoint files and don't build; one integration build follows.

When this stage finishes, proceed to Stage 3 if both, else to Stage 3b.

### 2a. Triage

Use the single path (2e) without planning when the task is plainly one logical change: a bug fix, or a change in one class or one or two files. A planner run isn't worth its cost there. Everything else goes to 2b.

### 2b. Plan

Delegate to `code-planner`, passing the ticket content and user prompt, plus this request verbatim:

> Besides your normal plan, append a `### Parallelization` section for implementation by several agents working at once in one workspace, where none of them can compile until all are done.
>
> - **Foundation** — what several packages depend on: new or changed declarations, enums, structs, gameplay tags, `.Build.cs` dependencies. Give exact signatures, and name stub bodies wherever a declaration would not link without one (e.g. `UFUNCTION`s). Write `none` if nothing is shared.
> - **Packages** — table of name, exclusive files, work. A `.h`/`.cpp` pair stays together. No file appears in two packages, including registries, shared config and test group lists. After the foundation, a package must be implementable from the foundation alone; if it needs another package's new code, move that code to the foundation or merge the two packages.
> - **Verdict** — `parallel` or `single`, with one line of reasoning. Say `single` if the work is really one chain of dependent edits. Don't split just to split.

If Open Questions would change the design, ask the user with AskUserQuestion. Otherwise don't ask for plan approval.

### 2c. Decide

Check the planner's split rather than trusting it. Fan out only if all of these hold:

- Two or more packages, with no file listed twice.
- Each package is worth a fresh agent: about 50+ changed lines, or a mechanical sweep across several files. Fold smaller ones into a neighbour.
- At most 4 packages. Merge the closest ones beyond that, because each extra agent re-reads context and adds integration risk.

If any check fails, or the verdict is `single`, use the single path (2e) with this plan.

### 2d. Parallel path

1. **Show the split** — one line per package with its file count. This is for visibility; don't wait for an answer.
2. **Changelist** — reuse a CL# from the input if there is one. Otherwise, using the Bash tool:
   ```bash
   p4 change -o | sed -e 's/<enter description here>/[TICKET] Summary #review/' -e '/^Files:/,$d' | p4 change -i
   ```
   Use `[NOTICKET]` when there's no ticket. Stage 6 writes the full description.
3. **Foundation** (skip if `none`) — one `code-dev`, alone in the workspace, so it builds as usual. Tell it the CL# (don't create one), to apply only the foundation, including stubs, and to report the headers workers should read. A broken contract is far cheaper to catch here than after every worker has coded against it.
4. **Workers** — one `code-dev` per package, all as Agent calls in a single message so they run concurrently. Use the worker prompt below.
5. **Wait for every worker** before going on. Then check each one's reported files against its package. An overlap, or a file nobody was assigned, goes into the integration prompt as something to reconcile.
6. **Integration** — one `code-dev`, using the integration prompt below. Its build is the compile gate for this track. Never run a second round of parallel workers: if a worker failed or stopped early, hand its unfinished package to the integration agent.

**Worker prompt:**

```
You are one of <N> code-dev agents working at the same time in one Perforce workspace.

CL: <CL#> (already exists; do not create one)
Your package: <name>
Files you may edit or create: <exact list>
Read first (foundation already in place): <headers>
Task: <this package's part of the plan, with the foundation signatures>
Other packages, for context only: <one line each>

These rules replace Step 1a and Step 2 of your usual workflow:
- Touch only your listed files. If you need a change anywhere else, don't make it; report it under "Needed outside package".
- Existing file: `p4 edit -c <CL#> <file>` before modifying.
- New file: after Write, run `p4 add -c <CL#> <file>`.
- Do not build: no UBT, Build.bat, UHT or Live Coding. Other agents' files are half-written, so the errors would be meaningless, and a later step does the build.
- Run p4 commands only on your own files. No CL-wide or default-changelist operations, and no p4 revert. The default changelist holds the user's unrelated work.
- Ignore files changing around you; that's the other agents.

Report exactly:
Package: <name>
Files changed: <list>
Files created: <list>
Needed outside package: <list, or none>
Unfinished: <list, or none>
Uncompiled assumptions: <anything the build should confirm, or none>
```

**Integration prompt:**

```
<N> code-dev agents just finished coding in CL <CL#> without compiling. You are now alone in the workspace.

Plan: <full plan>
Worker reports: <each report verbatim>
To reconcile: <overlaps or unassigned files, or none>

1. Finish everything under "Needed outside package" and "Unfinished". p4 edit -c <CL#> first.
2. Run `p4 opened -c <CL#>`. Reopen any reported file that is missing from it, naming that file individually. Never move anything else out of the default changelist; it holds the user's unrelated work.
3. Do your normal Step 2: full UBT build, fixing errors in any file in this CL, until it passes.
4. Report your usual summary, plus which errors came from mismatches between packages.
```

### 2e. Single path

Delegate to one `code-dev`: pass the plan if there is one, otherwise the ticket content and user prompt, and tell it to work out a concise plan itself. It implements directly, without asking for user validation, and handles its own changelist and build.

## 3. Blueprint Track (if blueprint or both)

1. Delegate to `blueprint-dev` agent — pass the full input (include CL# from C++ track if both)
2. After blueprint-dev completes, invoke `/unreal-asset-inspections` to verify properties
3. If verification fails: pass discrepancies back to blueprint-dev, re-verify (max 3 iterations)
4. Proceed to Stage 3b

## 3b. Scope check

Run `p4 opened -c <CL#>` and compare it with the plan's file list (or, without a plan, the files the agents reported). Any file outside it: **stop** and ask the user, offering to move it to a separate CL. Approval covers exactly what was named.

## 3c. Write the test (before review, so Stage 4 reviews it)

The project's CLAUDE.md test rule: a change to game-system behaviour adds or extends an automation test (objective, stable rules only; a bug fix's test must fail without the fix). If the plan has none and one is practical, delegate it to `test-dev` in the same CL; otherwise note why in the Stage 8 report. Skip for **tests** work (the test is the work).

## 4. Review

For **cpp**, **tests** or **both**: invoke `/code-review` skill — pass CL#
For **blueprint** or **both**: delegate to `blueprint-reviewer` agent — pass asset paths

**Severity meanings:**
- CRITICAL/WARNING: Blockers — must fix before merge
- MINOR: Style/naming issues — fix automatically, inside files already in the CL
- SUGGESTION: Improvement ideas — fix automatically only when inside files already in the CL and it adds no new helper, component or dependency
- INFO: Pre-existing issues outside this task's scope — context only, no action

The policy is to fix everything actionable inside the CL's files, not just the blockers. So: if **any** CRITICAL, WARNING, MINOR, or SUGGESTION findings exist, proceed to Stage 5. Only skip to Stage 5b when the review is clean (nothing, or INFO-only).

Don't stop to ask the user whether to fix in-CL MINOR or SUGGESTION findings — applying them is the default. Exceptions: a finding marked "no action / works by design" (note it and move on), and any finding whose fix lands in a file **not** already in the CL, or adds a new helper/component/dependency: list those and ask, offering a separate CL.

## 5. Fix Review Findings

1. Report the findings to the user with severity counts (CRITICAL, WARNING, MINOR, SUGGESTION, INFO) — for transparency, not to gate on their answer
2. Delegate **all actionable in-CL findings** (CRITICAL, WARNING, MINOR, and SUGGESTION, per the Stage 4 limits) for fixing to `code-dev` (game code), `test-dev` ({{UE_TEST_MODULE}} files) or `blueprint-dev`. Skip INFO, "no action / works by design", and the out-of-CL findings you asked about
3. Re-review once with **one** `code-reviewer` on the fix delta (`p4 diff` of the files the fix touched), given the prior findings list, asking which are resolved and whether the fix introduced new issues. Re-run the full `/code-review` fan-out only if the fix touched files the first review didn't see. Blueprints: blueprint-reviewer on the fixed assets only

**After re-review, check remaining findings:**
- **No CRITICAL or WARNING remaining:** Proceed to Stage 5b. (MINOR/SUGGESTION that legitimately remain — e.g. by-design notes — are acceptable; the gate is on blockers, because some suggestions are intentional no-ops and shouldn't drive an endless fix loop.)
- **CRITICAL or WARNING still present:** Ask the user:
  > "Review found [N CRITICAL, M WARNING] remaining after fixes. Options:
  > 1. Apply another round of fixes (specify which)
  > 2. Proceed to shelve with these findings
  > 3. Abandon the changelist"
  
  Then:
  - Option 1: Return to step 2 of this stage
  - Option 2: Proceed to Stage 5b
  - Option 3: Report abandonment and exit workflow

## 5b. Run tests

Run the affected tests once, after the last fix: run the project's test runner (`{{TEST_RUNNER_SCRIPT}}`) for the groups this CL affects (never whole tiers). Check editor state first (`{{EDITOR_STATUS_SCRIPT}}`); if the user said they're running tests or not to touch the editor, skip the run and report it as owed. Failing tests caused by this CL go back to Stage 5 step 2; unrelated reds are reported, not fixed.

## 6. Update review description

1. Invoke `/perforce-changelist-description`

Proceed to Stage 7.

## 7. Shelve the review

1. Invoke `/swarm-review-shelve`

Proceed to Stage 8.

## 8. Done

Report:
```
Implementation: Complete
Work type: <cpp|tests|blueprint|both>
C++ path: <single | parallel: N workers, foundation yes/no, reason if planned but not split>
Files changed: N (list)
Assets modified: N (list /Game/... paths)
Changelist: CL# <number>
Build: Passed (if C++)
New dependencies: <merged from every code-dev report with its WARNING details, or none> (if C++)
Verification: Passed (if Blueprint)
Review: <X critical, Y warnings, Z minor, A suggestions, W info>
Tests: <added/extended file, or why none> · run: <groups, pass/fail, or owed + why>
Out-of-CL findings: <list asked about, or none>
Shelved: Yes
```

## Rules

- For mixed tasks: C++ track completes before Blueprint track begins
- Only C++ implementation fans out. Blueprint work and Stage 5 fixes stay with one agent, since fixes can cross package lines and each round rebuilds anyway
- All parallel work lands in one CL, so review and shelve work as they do for a single dev
- Multi-batch refactor: one CL; each batch builds only; one review, one affected-tests run and one shelve after the last batch
- Never `p4 revert` or reopen files outside this CL; parallel sessions share the workspace
- Never skip compile (C++) or asset verification (Blueprint)
- Single fix-review pass per track; user decides only if blockers (CRITICAL/WARNING) remain afterward
- Present review findings before applying fixes — for visibility, then fix all actionable findings without waiting for the user to choose
