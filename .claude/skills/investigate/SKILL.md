---
name: investigate
description: "Root-cause investigator for bugs, crashes and unexpected behaviour. ALWAYS invoke when the user describes a symptom and asks what causes it: 'investigate X', 'why is X happening', 'debug this', 'X is broken/crashing/laggy', or a pasted error. Searches code, Perforce history and the web, returns 10+ ranked causes with probabilities, verifies the top few. To PROVE a cause, use diagnose."
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# Investigate — Rank the Likely Causes of a Symptom

Take a described symptom and produce a ranked list of **at least 10 potential causes**, each with a probability, grounded in evidence from three sources: the codebase, Perforce history, and the web. Then actively verify the top candidates so the user starts debugging from facts, not hunches.

The point of casting wide (10+ causes) is to fight tunnel vision. The first explanation that comes to mind is often wrong, and a good investigation surfaces the non-obvious candidates — a race condition, a recent unrelated CL, an engine quirk — alongside the obvious ones. Breadth first, then narrow by evidence.

## Required Variables

| Variable | Purpose |
|----------|---------|
| `PROJECT_ROOT` | Workspace root for code + p4 searches |
| `UE_PROJECT` | Path to `.uproject` (derive project/module names) |

Both are set in the process env (`.claude/settings.local.json` `env`).

## Flow

### 1. Frame the symptom

**Route the input first:**
- A `{{DOWNLOADS}}\step-saved_*` folder or zip, a Horde job URL, or a Slack `:x:` job paste → run `horde-artifact` first.
- A `.log`, a crash folder or `Saved/Automation/Reports/*/index.json` → run `game-log` first.
- A Slack link (`*.slack.com/archives/…`) → read it with the Slack MCP (`slack_read_thread`/`slack_read_channel`); never open Slack in Chrome.
Then investigate from their digest; never by reading a raw log.

Restate what's failing in one sentence so the search is aimed correctly. Pull out the searchable specifics: exact error strings, log categories (e.g. `LogNet`, `LogAbilitySystem`), class/function names, the subsystem (GAS, ReplicationGraph, AI, CommonUI), and whether it's client/server/both. If the symptom is too vague to search (e.g. "the game feels off"), ask one sharp clarifying question before burning a search — otherwise proceed.

Form an explicit hypothesis space across these failure categories so the final list isn't lopsided toward one kind of bug:

- **Logic / state** — wrong branch, off-by-one, stale cached value, bad default
- **Lifecycle / null** — use-after-free, GC'd UObject, uninitialized pointer, order-of-init
- **Replication / networking** — missing `DOREPLIFETIME`, RPC reliability, relevancy/`ReplicationGraph`, client-server desync, authority checks
- **GAS** — ability/effect interaction, attribute clamp, prediction mismatch, tag state
- **Timing / concurrency** — race, Tick ordering, async completion, frame-delay assumption
- **Data / config** — DataTable/DataAsset value, `.ini` setting, cooked vs editor difference
- **Regression** — a recent changelist changed adjacent code
- **Engine / third-party** — known UE5 bug, plugin behavior, version-specific quirk

### 2. Gather evidence (run the three searches in parallel)

These are independent — launch them together, don't serialize.

**Codebase.** `Grep` for the error string, log category, and the symptom's domain terms across `Source/`. Read the most relevant hits to understand the actual code path. Look for the usual suspects in whatever subsystem owns the symptom (e.g. for a replication bug, check `GetLifetimeReplicatedProps`, `bReplicates`, authority guards).

**Perforce history.** Regressions are common and cheap to check. Find what changed recently near the suspect code:
- `p4 changes -m 25 -s submitted //...` for the recent CL stream, or scope to a path: `p4 changes -m 15 //depot/path/to/subsystem/...`
- `p4 filelog -m 5 <suspect-file>` to see who last touched a specific file and why
- `p4 describe -s <CL#>` to inspect a suspicious changelist's contents
Run p4 via the Bash tool. If p4 isn't available or returns nothing, note it and move on — don't block the investigation on it.

**Web.** `WebSearch` the exact error string and the symptom phrased as a UE5 problem (include the engine area — "UE5 GAS GameplayEffect not applying on client"). Prefer Epic docs, the UE forums/Discourse, and known-issue trackers. `WebFetch` a page when a result looks authoritative and the snippet is too shallow. This is where you catch engine bugs and quirks that no amount of reading your own code would reveal.

### 3. Build the ranked list (10+ causes)

Synthesize everything into candidate causes. Each cause must be **specific and actionable** — "a replication issue" is useless; "`CurrentHealth` is missing from `GetLifetimeReplicatedProps`, so clients never see damage" is a lead. Draw from across the categories in Step 1; if every cause is the same flavor, you haven't searched widely enough.

Assign each a probability as **percentage + tier**, calibrated to the evidence:
- **High (60–90%)** — direct evidence points here (a matching code smell you found, a recent CL touching exactly this, a web result describing the same symptom)
- **Medium (25–55%)** — plausible and consistent with the symptom, but no smoking gun yet
- **Low (5–20%)** — possible, worth listing so it's not forgotten, but unsupported so far

Probabilities are independent estimates of "this is the cause" — they don't need to sum to 100% (causes can overlap, and there may be ones nobody listed). Don't anchor everything at 50%; spread them to reflect how the evidence actually fell. Order the list highest-probability first.

### 4. Verify the top candidates

Pick the top 2–3 and actively try to confirm or kill each — this is what separates an investigation from a brainstorm:
- Read the specific suspect code path end to end (not just the grep line)
- Inspect the suspicious CL with `p4 describe`
- Trace whether the conditions the cause requires are actually met in the code

Update the probability and tier based on what you find. **Ruling a cause out is a real result** — say so explicitly and demote it; a confirmed "it's not X" narrows the search as much as a confirmed "it's Y." If verification promotes a Low cause above a former High, re-sort.

### 5. Present the report

Use the output format below. Lead with the ranked list, then the verification findings, then concrete next steps.

## Output format

```
## Investigating: [one-line restatement of the symptom]

## Ranked causes

1. **[Cause — specific and concrete]** — High (75%)
   - Why: [the evidence — what you found in code/p4/web that points here]
   - Where: `path/to/File.cpp:123` or CL 12345 or [source link]
   - Check: [the single fastest way to confirm or rule this out]

2. **[Next cause]** — High (60%)
   - Why: …
   - Where: …
   - Check: …

[… continue to at least 10, descending by probability …]

## Verified top candidates
- **[Cause #N]** — Confirmed / Ruled out / Inconclusive. [What you did to check and what you found.]
- …

## Recommended next step
[The one thing to do first, given the above — usually chase the highest cause that's cheap to confirm.]

## Sources
- [Web result title](URL) — what it supports
- CL 12345 — what it touched
```

## Rules

- **Always produce at least 10 causes.** If you can't reach 10 from evidence, fill the tail with lower-probability candidates drawn from the category checklist and mark them Low — breadth is the whole point. Never pad with duplicates of the same root cause worded differently.
- **Every cause needs a "Why" tied to evidence.** A cause with no supporting reason from code, p4, or web is a guess; either find support for it or drop its probability to Low and say it's unsupported.
- **Run the three searches in parallel**, not one after another — they're independent and latency adds up.
- **Cite specifics.** Point to `file:line`, CL numbers, and real URLs — not "somewhere in the AI code" or "I recall that UE5…".
- **Date-stamp / version-check web claims.** Engine behavior changes between UE5 versions; confirm a forum answer applies to this project's engine before trusting it.
- **Don't fix anything.** This skill diagnoses and ranks. If the user wants the fix implemented, hand off to the `code-dev` agent (C++) or `blueprint-dev` (Blueprints) with the confirmed cause and evidence.
- **Input is a file or link: hand it to the right skill first** (see §1, "Route the input").
