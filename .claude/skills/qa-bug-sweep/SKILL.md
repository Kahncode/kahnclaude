---
name: qa-bug-sweep
description: "Pre-QA bug sweep over every CL submitted to {{P4_STREAM}} in the last N days: parallel code reviewers, verified findings, Jira dupe check, ranked report with repro steps. ALWAYS invoke when recent submits (not one CL) should be checked for bugs: 'find bugs in the last 2d of changes', 'what did we break this week', '/qa-bug-sweep 5d'. For missing tests use submit-test-gaps."
---

# QA Bug Sweep

Review everything the team submitted in a time window and report the bugs QA
would find, before they find them. The result is a list a tester can pick up
and reproduce. It is not a code-quality review.

The bar for each finding is: **a person playing (or hosting) the build that
contains these CLs can make it happen and see it.** That means crashes, hangs,
wrong or missing UI, wrong numbers, broken interactions, desync between
players, lost or duplicated items, exploits, and missing feedback (VFX, SFX,
outline). Code smells, style issues, log noise nobody sees, editor-only tool
problems, automation-test changes, and races that need impossible timing are all
out. They are real issues, but QA can't find them, so they would drown out the
ones QA can.

## Inputs

- **Window**: `Nd`, `Nh`, or "since <day>". Turn it into days, e.g. "since
  Friday" on a Tuesday is 4 days. If the user gives no window, use 2 days and
  say so in the report.
- **Focus** (optional): a system ("Inventory", "Weapons") or a person. Apply it
  as a filter on `changes.json` after Step 1. Don't change the query.

## Step 1: List the CLs (one script, about 2 seconds)

```bash
python -I -X utf8 "$KC_PROJECT_ROOT/.claude/skills/qa-bug-sweep/scripts/list_changes.py" --days <N> --out "{{TEMP_BASE}}\qa-bug-sweep-scratch\<YYYY-MM-DD>-<N>d"
```

The script does all the listing in a few batched p4 calls. Don't loop
`p4 describe` per CL: that took minutes in earlier attempts and the user stopped
it. The script also:
- drops bot CLs (`build`, robomerge, Horde clients) and generated paths
  (Binaries, Intermediate, `{{UE_TEST_MODULE}}` source);
- marks each CL as code-review / tooling-only / asset-only / other;
- splits the code-review CLs into 3–10 balanced **batches**, keeping each
  system's CLs together where it can;
- records the workspace's `#have` changelist, so you know whether local files
  are older than the newest CL in the window.

Read the printed summary. Load `changes.json` only to get CL descriptions and
file lists for the prompts. If a focus was given, keep only the matching CLs
(by `area`, description, or `user`) and regroup them into batches of about 15
code files.

Tell the user the counts in one line (e.g. "31 code CLs in 8 batches; 42
asset-only CLs listed but not reviewed") and continue. Don't wait for an
answer.

## Step 2: Review (one agent per batch, all in ONE message)

Spawn one `code-reviewer` agent per batch, all in a single message so they run
in parallel. Fill in the prompt from `references/reviewer-prompt.md`. Each
agent gets:
- its batch: CL number, author, full description, code files;
- the **whole window's CL list** (number, author, first line of the
  description). Many real regressions come from two CLs in the window
  interacting, or from a later CL already fixing an earlier one, and a reviewer
  that sees only its own batch misses both;
- the workspace-sync warning from Step 1, if local files are behind.

Reviewers collect their own diffs (`p4 describe -du <CL>`). Don't fetch diffs
yourself: it fills your context and the agents need it more.

## Step 3: Verify (one skeptic per batch that has findings, all in ONE message)

Reviewers over-report. For every batch that returned findings, spawn one
`code-reviewer` with `references/verifier-prompt.md` and that batch's findings.
The verifier's job is to **disprove** each finding: guarded elsewhere, path
unreachable in a client build, fixed by a later CL, or invisible to a player.
Keep `confirmed` and `likely`. Drop `rejected`, but count those, and keep each
one's one-line reason for the appendix.

Then deduplicate across batches. Two batches can report the same symptom from
interacting CLs: merge them and list both CLs.

## Step 4: Jira check (one agent)

Spawn one `general-purpose` agent with `references/jira-prompt.md` and the
surviving bugs. It searches {{JIRA_PROJECT_KEY}} (read-only, never files or edits anything) and
tags each bug as:
- `ticketed`: an open ticket describes it (give the key);
- `regressed`: a Done ticket describes it, so the bug came back (give the key);
- `related`: the ticket for the CL that caused it, or a nearby report;
- `new`: nothing found.

## Step 5: Write the report

Write `{{TEMP_BASE}}\qa-bug-sweep-scratch\<YYYY-MM-DD>-<N>d\report.md` using the
template in `references/report-template.md`. Order: Crash, then Blocker, Major,
Minor, with `new` before `ticketed` inside each tier. Each bug title describes
what the tester sees, not what the code does: "Opening the inventory while reloading
crashes the client", not "null deref in UInventoryComponent::Open".

In chat, reply with the counts by severity and Jira status, the top 3 bugs (one
line each), and the report's full absolute path. Put everything else in the
report.

## Judgement notes

- **Severity:** Crash = process dies or hangs. Blocker = a player can't
  continue (stuck, can't finish the match, can't interact, progress lost). Major = a
  feature visibly works wrong. Minor = a visible but cosmetic or rare glitch.
- **Server vs client:** a server-only `check()` hit in a dedicated build still
  kicks every player off. That counts as Crash and is visible.
- **Config/ini CLs** (feature flags, CVars, `DefaultGame.ini` tuning) often
  change the most behaviour per line. Review them; don't skip them.
- **Asset-only CLs** aren't reviewed, because Blueprint diffs can't be read as
  text. The report lists them, each with a one-line risk note based on the
  description. Flag any that touch something a reviewed code CL changed.
- **Repro steps** must be things a tester can do in the build: menus, inputs,
  console commands that ship in dev builds. A step like "call X with null"
  is not a repro.
