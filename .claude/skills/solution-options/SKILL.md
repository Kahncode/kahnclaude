---
name: solution-options
description: "Quick implementation-options scout. ALWAYS invoke when the user wants the ways to build something laid out first: 'what are the options to do X', 'how would we implement X', 'is there a way to X', 'can the engine already do X'. Reads real code and engine source, returns a short table (effort, upsides, downsides) and one pick. Read-only. Not for bugs (investigate) or scoping (task-planning)."
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Agent
---

# Solution Options: quick ways to build X, with an opinion

The user has something they want and wants to see the realistic ways to get it **before** anyone writes a plan or code. They want speed and a clear opinion: a short, evidence-backed table they can decide from in under a minute. They don't want a survey essay.

A good answer does three things a quick guess can't:
1. **It checks whether the request works as phrased.** Users describe the outcome in terms of the mechanism they imagine. Often that mechanism doesn't exist ("sort by column" when the window can't sort), and saying so early changes which options make sense.
2. **It finds what already exists.** Engine features, project config and macros that every case already passes through usually beat new code. Most of the value is in spotting that the engine already has tags, a config group list, or a delegate.
3. **It makes a call.** Give one recommendation, say why, and say what it costs.

## Speed budget

Aim for roughly 10–20 tool calls and no subagents. Launch your searches in parallel. Spawn one `Explore` agent only if you can't locate the subsystem within a few greps. The skill is useful because it is fast. If the area is so unknown that a fair answer needs deep research, give the partial table and say which option needs more digging rather than stalling.

Make no edits, create no CL and run no builds. This skill is read-only.

## Flow

### 1. Restate the goal (in your head, one line)

Separate **the outcome** ("see all Inventory tests together") from **the mechanism they named** ("a label so they can be sorted"). Search for ways to get the outcome. Mention the named mechanism only if it's possible or worth ruling out.

### 2. Find the facts (parallel)

Look where the answer usually lives:

| Where | What to look for |
|---|---|
| **Project code** (`{{UE_PROJECT_DIR}}\Source\**`) | The single point every case already flows through: a macro, base class, subsystem, or registration helper. One change there covers every case. |
| **Project config** (`{{UE_PROJECT_DIR}}\Config\*.ini`) | Is there an existing settings block that already does something similar (e.g. `+Groups=` lists)? Config-only options are the cheapest. |
| **Engine source** (`{{UE_ENGINE}}\Source\**`, usually `Runtime/` + `Developer/` + `Editor/`) | Does UE already support this? Grep the `Public/` header of the relevant module for the feature noun (`Tags`, `Category`, `Filter`, `Delegate`). Check the UI code too, because "the engine supports X" and "the editor window shows X" are different claims. |
| **Plugins in `.uproject`** | Is a plugin already enabled that does this? |
| **Memory** | Has this area come up before (an earlier plan, a decision, a known pitfall)? |

Never content-search `Content/`, whole `Plugins/` trees or `*.uasset`/`*.umap`. Use file-name search or the asset registry (the `unreal-asset-inspections` skill) instead.

Put a `file:line` on every claim that rules an option in or out. The user decides from these facts, so they have to be real.

### 3. Build the option set

Aim for **3–5 real options**. Usually these come from different layers:
- **Config only** (no code)
- **Small project-code change** at the shared choke point
- **Combination** of the two, if they reinforce each other
- **Big-but-obvious** (rename, restructure). Include it if the user is likely thinking of it, mostly to say why not.
- **Engine modification.** Include it if it's the only "true" fix. If the project's CLAUDE.md restricts engine edits, say they need explicit approval.

Leave out options that don't hold up. Two strong options beat five padded ones.

Put side-mechanisms that cover an edge case (e.g. an ini file for the handful of tests the macro doesn't reach) on a final `—` row instead of numbering them as main options.

### 4. Judge each option

For effort, use concrete units the user can picture: "config only", "~6 lines in one header", "touches 40 files", "Engine/ change". Avoid S/M/L by itself.

Downsides to always weigh in this project:
- **Engine/ edits** add merge cost on every engine update (and need approval if the project's CLAUDE.md restricts them).
- **Renames** cascade into Horde filters, quarantine lists, config, docs and memory (see the global "never rename without a plan" rule).
- **Header/macro changes** mean a full module rebuild, which Live Coding can't do.
- **Hand-maintained lists** (ini, data tables) drift.
- **Duplicated meaning**, where the same fact lives in two places that can disagree.
- **Replication/GAS/multiplayer**: does it work on client *and* server?

### 5. Recommend

Pick one option, or one plus an optional add-on, and give the reason in one sentence. Then list the **decisions to settle** before building: edge cases the investigation surfaced that the user has to answer (odd naming, cases the choke point misses, ambiguous data). Keep it to 0–3 bullets.

## Output

Use this shape. Users scan it, and the "short answer first" line is what they read when busy.

```markdown
**Short answer:** <1–2 sentences: the key fact that frames the choice (often "X can't do Y as asked; the real levers are A/B/C") + what's already in place>

## Options

| # | Approach | Effort | What you get | Downsides |
|---|---|---|---|---|
| **1** | **<name>.** <how, with file:line> | <concrete> | <outcome> | <costs> |
| 2 | ... | ... | ... | ... |
| — | <side mechanism for edge cases> | ... | ... | ... |

## Recommendation

**<Option N>** (+ optional add-on): <one-sentence why>.

Decisions to settle first:
- <edge case>: <the choice>

<If nothing was changed: "No code changed — investigation only.">

- **What I did:** <one plain sentence>
- **What to check:** <the single decision the user needs to make>
- **Next step:** <the obvious hand-off, e.g. "pick N and I'll hand it to code-planner → code-dev">
```

Bold the recommended option's row number and name. Keep cells short, and put long reasoning in the recommendation, not the table. Write for a busy reader: lead with the status, keep each point short, and don't repeat yourself.

## Example (abridged)

Prompt: *"I want to group tests by system in the automation window. What are the options?"*

> **Short answer:** the Session Frontend can't sort by a column (no sort on its headers, `SAutomationWindow.cpp:273-335`). The tree is built from the dot-separated test path and sorted alphabetically (`AutomationReport.cpp:635-643`). So "sort by System" means a tag filter, a Group dropdown entry, or moving System within the path.
>
> | # | Approach | Effort | What you get | Downsides |
> |---|---|---|---|---|
> | **1** | **Work out a `[System]` tag from the path.** All tests go through the project test-class macro `MY_TEST_CLASS_DETAIL`, which already passes `DefaultTags` (`MyTestClass.h`) | ~6 lines, one header | Tags column, toolbar tag filter, `-testtags` from the command line | Repeats the path (but can't drift); full rebuild |
> | 2 | One `+Groups=` entry per System in `DefaultEngine.ini` | Config only | Group dropdown entry per System | Hand-kept list; `Contains` substring can catch the wrong tests |
> | 3 | Rename paths to System-first | Large | Tree groups by System | Breaks tier groups, Horde, quarantine lists. Not recommended |
> | 4 | Sortable Tags column | Engine change | Real sorting | Needs Engine/ changes and approval |
>
> **Recommendation: 1.** One change point, covers every CQTest test, and the tag can't disagree with the path.
