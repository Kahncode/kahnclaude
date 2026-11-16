---
name: diagnose
description: "Root-cause confirmer. ALWAYS invoke when the user wants a cause PROVEN, not ranked: 'diagnose X', 'prove why X fails', 'find the real cause of this flake', 'add logs and a test until we know', 'get to 95%'. Starts from investigate's ranked causes, then loops logs + repro tests, build, run until one cause is at 95%+ or blocked. Prefer over investigate when proof must come from running code."
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Edit, Write, Agent, Skill, WebSearch, WebFetch
---

# Diagnose: Prove the Cause, Don't Guess It

`investigate` ranks causes from reading code, Perforce and the web. `diagnose` goes further: it makes the code **tell** you the cause. It adds targeted logs and a reproduction test, runs them, and keeps narrowing until one cause reaches **at least 95%** confidence, backed by an observation from a real run.

A cause is only "95%" when a run shows the mechanism happening, for example a log line where the server holds the tag and the client doesn't, at the frame the test fails. It must also hold up against the runner-up causes. Reading the code can get you to about 70%. Running it gets you the rest.

## Inputs

`$ARGUMENTS`: a symptom, failing test name, Horde job/artifact, Jira key, log excerpt or report path. If none is given, use the symptom from the conversation.

Variables `PROJECT_ROOT`, `UE_PROJECT`, `UE_ENGINE` are set in the process env (`.claude/settings.local.json` `env`).

Route the input first: a step-saved folder/zip or Horde URL → `horde-artifact`; a `.log`/`index.json` → `game-log`; a Slack link → the Slack MCP (`slack_read_thread`), never Chrome.

## Flow

### 0. Gather the failure evidence first
- Horde message or job: invoke `horde-artifact` to download the logs, then read the failing step.
- Local report: read `{{UE_PROJECT_DIR}}\Saved\Automation\Reports\<timestamp>\index.json` (errors, info lines, timestamps) and the matching `{{UE_PROJECT_DIR}}\Saved\Logs\*.log`.
- Crash or log question: invoke `game-log`.
- Pull out the exact error text, the test step, the frame and timestamp, and server vs client.

### 1. Investigate (breadth)
Invoke the `investigate` skill with the symptom and the evidence. Keep its ranked list of at least 10 causes, each with a probability. That list is the **hypothesis table** used for the rest of the run:

| # | Cause | P | Evidence for | Evidence against | Discriminating observation |
|---|-------|---|--------------|------------------|----------------------------|

The last column matters most: **what would we see in a run if this cause is true and the others are false?** If two causes predict the same observation, a log won't tell them apart; design a check that does.

If the top cause is already at 95% or more, backed by evidence from a real run (e.g. a log already prints the mechanism), skip to step 5.

### 2. Create the diagnostics changelist
- Follow the CLAUDE.md changelist discipline. Use a **separate** pending CL for diagnostics, not the user's feature CL, unless they say otherwise. Description: `[<JIRA or NOTICKET>][Diag] <symptom> #review`, with `Files:` stripped.
- `p4 edit -c <CL>` before touching any file. Never `attrib -r`. Never `p4 add` binaries. Never submit.
- Put temp files in `{{TEMP_BASE}}\diagnose-<CL>\`.

### 3. The confidence loop
Repeat until the top cause is at 95% or more, or the loop is **blocked** (see Stop rules).

**3a. Design the experiment.** Pick the top 2-3 causes that are still open. For each, choose the cheapest check that confirms or kills it:

- **Diagnostic logs** in game or test code, at the exact points the cause predicts state diverges:
  - `UE_LOG({{UE_DIAG_LOG_CATEGORY}}, Display, ...)` with a short-lived category, or the owning system's category at `Display` or above, so Horde logs keep it.
  - Log **both halves** (server and owning client) and include the frame (`GFrameCounter`), the world time, and the values the causes disagree on, e.g. the tag count, the instance name, velocity, or the attribute value.
  - Tag every diagnostic line with the comment `// DIAG(<CL>)` so it can be found and removed later.
  - Diagnostics never change behaviour: no new gates, no early returns, no logic.
- **Test-side diagnostics** in `{{UE_TEST_MODULE}}`: `AddInfo` lines in the failing step that describe both halves, or a `{{UE_TEST_LOG_WATCH_CLASS}}` on the suspect log line.
- **A reproduction test**, the strongest evidence. It is a CQTest that triggers the suspected mechanism directly and fails if the cause is real. Read `{{UE_TEST_README}}` first to pick the tier, the macros and the failure style. Follow the memory rules:
  - Wait for real readiness; never suppress errors.
  - Name tests with the `{{UE_TEST_PREFIX}}` prefix.
  - No anonymous namespaces; east const.
- Project specifics: read {{PROJECT_NOTES_DIR}}\diagnose.md if it exists.
  A repro that fails with the predicted message, and passes once the suspected condition is removed (e.g. by a test-only override), is near-proof.
- **A forcing experiment:** make the suspected condition certain (a cvar, a test override, an injected delay or ordering) and check that the symptom becomes deterministic. Then make it impossible and check that the symptom disappears.

Write the plan into the hypothesis table first: which cause each probe tests, and what result confirms or kills it.

**3b. Implement.** Game-code diagnostics go to the `code-dev` agent; repro tests and test-side diagnostics ({{UE_TEST_MODULE}}) go to `test-dev`. The brief needs the CL number, the exact files and lines, the `// DIAG(<CL>)` rule, "diagnostics only, no logic change", and the expected log lines.

**3c. Build.** Body-only change with the editor open: Live Coding (the code-dev agent's Step 2a route: check `LiveCodingConsole.log` ends "Live coding ready", then `LiveCoding.Compile` through editor-py; `unreal-project-compilation` is UBT only). Otherwise a full UBT build via `unreal-project-compilation`, in the background. If Live Coding stalls (memory: LiveCodingConsole stall), ask the user before closing the editor. Never open rebuilt binaries in a CL.

**3d. Run only the affected tests** with `{{TEST_RUNNER_SCRIPT}} -Tier <Tier> -Filter "<A>+<B>"` (from the PowerShell tool; subagents can't run it because of the execution policy).
- A flake needs several runs to show. Repeat until the symptom has appeared at least **2 times**, or for **N = 10** runs, whichever comes first. Run the loop yourself in the background (`run_in_background`) and wait with Monitor, never a foreground sleep loop. Read the results from `{{UE_PROJECT_DIR}}\Saved\Automation\Reports\<timestamp>\index.json`, not from the runner's console, because it uses Write-Host.
- **No repro in the first 10 runs:** start a **200-run** background loop with the same filter and net conditions, without asking; stop once the symptom is seen 2 times. Stop loops between passes, never by killing the editor.
- If it only fails on Horde, hand the diagnostics to the user to shelve and run a Horde preflight. Wait for the artifact and don't guess its result.

**3e. Update the table.** For every cause, record what the run showed and adjust P:
- The predicted observation was seen at the failing frame: raise P sharply.
- The observation contradicts the cause: drop it to 5% or below and mark it **ruled out**. That is a real result.
- No difference was seen: the probe didn't discriminate. Design a better one rather than nudging P.
- A new cause appeared in the logs: add it to the table.

Show the user a short update after each iteration: what ran, what was seen, the table's top 3 with P, and the next probe.

### 4. Stop rules
- **Done:** the top cause is at 95% or more, **and** it is backed by evidence from a real run, **and** every runner-up is at 10% or less or explicitly ruled out.
- **Blocked:** stop and ask the user instead of looping when:
  - the symptom hasn't reproduced in the 200-run loop, so the probes can't fire;
  - the next probe needs an Engine/ change (CLAUDE.md: needs approval), a submit, or closing an editor someone else is using;
  - after 5 iterations the top cause is still below 95%;
  - the remaining causes need data only Horde or a player report can give.
  Say what is known, what is missing, and the one experiment that would close the gap.

### 5. Report
Use the output format below, then offer next steps:
- **The fix:** hand off to `code-dev` with the proven cause and evidence, in its own CL if it's game code.
- **The repro test:** keep it as a regression test in its own CL (`test-dev`); it stays red until the fix lands, so quarantine it with a reason naming the owner if needed.
- **The diagnostics:** strip every `// DIAG(<CL>)` line, keep the ones worth keeping at Verbose, or shelve the diagnostics CL for Horde runs.
- **Jira:** file or update the {{JIRA_PROJECT_KEY}} bug with the evidence if the cause is a game bug.
- **Cleanup:** once the cause is proven or the ticket closes, list the DIAG/TRIAL CLs this run made and offer `p4 shelve -d -c N` then `p4 change -d N`; never delete without the user's OK.

Diagnosis ends at a proven cause; don't fix the bug unless the user asked for a fix. **If the user asked to FIX it** (e.g. "fix this flake", "run N times until clean"): loop fix (test-dev for test code, code-dev for game code; own CL) → `/code-review` → rerun N with no confirmation stops, and report at the end.

## Output format

```
## Diagnosed: [one-line symptom]  →  [cause] — [P]% (Confirmed)

### Proof
- [The run observation that proves it: report path or log file:line, frame, both halves' values]
- [The repro test result: name, N runs, failed M/N with the predicted message]

### Mechanism
[3-6 numbered steps from trigger to symptom, each with file:line]

### Hypothesis table (final)
| # | Cause | P start → end | Status | Deciding evidence |
|---|-------|---------------|--------|-------------------|

### Experiments run
1. [Probe] → [result] → [effect on the table]

### Changelists
- Diagnostics: CL [N] ([files], `// DIAG(N)` lines: [count])
- Repro test: CL [N] or "in diagnostics CL"

### Next step
[The single recommended action: the fix CL, quarantine, or the Horde preflight]
```

## Rules
- **95% needs a real run.** Code reading alone is capped at 80%. Say so if that's where you stopped.
- **Discriminate, don't decorate.** Each log or test exists to tell two causes apart. Remove probes that can't.
- **Diagnostics change no behaviour.** They are logs and `AddInfo` only, so they can't hide or create the bug.
- **Change one variable at a time** in forcing experiments.
- **Use separate CLs:** diagnostics, repro test and fix each get their own unless the user says otherwise. Never submit.
- **Don't guess about runs that are still in flight.** Report a pending Horde job or background loop as pending.
- **Respect the CLAUDE.md and memory rules:**
  - no content grep of `.uasset`/`Content`;
  - no Engine/ edits without approval;
  - run affected tests only;
  - temp files in `{{TEMP_BASE}}`;
  - no worktrees;
  - East const;
  - comments of at most 2 lines;
  - no anonymous namespaces.
