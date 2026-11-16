---
name: test-feasibility
description: "Test-feasibility ranker for several bugs, Jira tickets, a JQL query or test ideas. ALWAYS invoke when the user asks which could be caught by automation tests: 'could a test have caught these', 'which of these bugs can we automate', or Jira keys plus a test question. Checks existing coverage, returns a ranked table and report. For a CL time window use submit-test-gaps."
allowed-tools: Read, Grep, Glob, Bash, Write, Agent, mcp__atlassian__searchJiraIssuesUsingJql, mcp__atlassian__getJiraIssue
---

# Test Feasibility: rank bugs and ideas by how well a test can stop them

Take a list of bugs or ideas. For each one, decide whether an automation test on the **current** {{UE_PROJECT_NAME}} harness could catch it or keep it from coming back, how sure we are, and whether the test is worth writing. Output is a ranked list a dev can pick work from.

This is read-only analysis. No `p4 edit`, no Jira writes, no test code. Nothing gets run, so every verdict is a judgement, and the report has to say so.

## 1. Collect the items

Accept any mix of:

- **Pasted text**: bullets, a table, a Slack dump. One item per distinct defect or idea. Split compound lines ("X crashes and Y is missing") into two items.
- **Jira keys or JQL**: `mcp__atlassian__searchJiraIssuesUsingJql` (cloudId `{{JIRA_CLOUD_ID}}`, `maxResults: 100`, `responseContentFormat: "markdown"`, fields `summary,description,status,resolution,priority,components,labels,created,comment`). Use `getJiraIssue` only when a description is too thin to judge.
- **A doc, artifact or file**: Claude Docs `read`, Artifact `read` for claude.ai links, `Read` for local `.md`/`.json`/`.csv`.

Give each item a short ID (`B1…` for bugs, `I1…` for ideas, or the Jira key) and keep the user's wording as the title.

**Find the fix when there is one.** A bug that has been fixed tells you the real root cause, which is the best evidence you can get. For Jira keys, run `p4 changes -l -s submitted {{P4_DEPOT_ROOT}}/...@<created date>,now | grep -n -B2 -A6 "{{JIRA_PROJECT_KEY}}-12345"`, then `p4 describe -s <CL>` (file list) and `p4 describe -du <CL>` for code CLs (skim it, don't dump it). A fix that only touches `.uasset`/`.umap` was a content or data fix, and those are often Content-sweep material. For pasted bugs with no key, search `Source/` for the named class or system to find the code path.

**Bug or idea?**
- A **bug** describes behaviour that is wrong now or was wrong before. The question is: would a test written against the expected behaviour have failed on the buggy build?
- An **idea** is either a feature not built yet ("armour should cap at 80% reduction") or a test idea ("check every weapon has a muzzle socket"). For a feature idea, judge whether its rules could be guarded once it is built. For a test idea, judge the test directly.

## 2. Judge each item

Read `{{UE_TEST_README}}` once for its tier table ("use the smallest world that can show the bug") and its naming rule (e.g. `{{UE_TEST_PREFIX}}<Tier>.<System>.<Concept>.<Test>`). Use those tiers, not your own.

Project specifics: read {{PROJECT_NOTES_DIR}}\test-feasibility.md if it exists.

For each item, answer these in order.

### a. What is the oracle?

State the rule the test asserts, as one sentence a machine can check: "after Repair, Health == MaxHealth", "no two LootTable rows share an ItemId", "opening inventory while dead logs no Error/Ensure". If you can't write the oracle without a word like "looks", "feels", "too", "should be around" or a tuned number, the item is not a `yes`.

The test suite must stay trustworthy and must never become a design gate, so oracles must be **objective, stable rules**: code contracts, crash/ensure/error-free paths, no dup or loss of items, conservation, server authority, unambiguous repros of the reported bug. Content rules may only compare an asset against its own other fields, a C++/engine default, or whether a component is present. They never compare against hardcoded classes, asset paths, magic counts or tuned values, because those break on every balance pass.

### b. Verdict

| Verdict | Meaning |
|---------|---------|
| `yes` | A test that one dev could write in about a day on the existing harness, with a deterministic pass/fail, would have failed on the bug (or will guard the idea). |
| `maybe` | Catchable only with a heavier or luckier test: long sessions, a specific race or timing, many players, live backend, exact repro state. Or the oracle is fuzzy. |
| `no` | Not practical to automate: visuals/art/anim/VFX/audio feel, UX wording, balance, hardware-specific perf, platform/driver crashes, live ops, exploit creativity. |
| `n/a` | Not a real defect: duplicate, can't reproduce, works as designed, a task mis-filed as a bug, or too little information to judge. |

Be sceptical. Crashes on a common path (open a menu, equip an item, load a map) are usually `yes` via a player-flow no-error check. Asset data mistakes with a clear rule (missing ref, wrong enum, duplicate ID) are usually `yes` via an asset-data rule. The README's tiers name which test types these are.

### c. Tier and test

Pick the smallest tier from the README table that can show the bug. Name the test by the README's naming rule (e.g. `{{UE_TEST_PREFIX}}<Tier>.<System>.<Concept>.<Test>`), then write one or two sentences: what it does, and what it asserts. Use game-code nouns from the project, not invented ones.

Respect the harness rules in `{{UE_TEST_README}}`; for example, waits are for real readiness (never fixed sleeps or suppressed errors).

### d. Confidence: High / Medium / Low

How sure are we that the suggested test would have failed on the bug **and** would stay green and stable afterwards? This maps straight onto how the test gets landed:

- **High**: objective rule, clear code path, and you can point to the line or asset field that broke. The test can **gate** (fail CI) from day one.
- **Medium**: rule is a design convention, or the test is costly or flaky-prone, or the root cause is inferred rather than seen. Lands as **report-only** until an owner confirms.
- **Low**: depends on a design or tuning decision, or the evidence is thin. **Parked**, phrased as a question for designers.

`no` and `n/a` items get `—`.

### e. Existing coverage: covered / extend / new

Search `{{UE_PROJECT_DIR}}\Source\{{UE_TEST_MODULE}}\` (its test, class and action folders) for the system and concept. Use Grep on Source only, never on `Content/` or `.uasset` (the hook blocks it, and it freezes the disk).

- **covered**: an existing test already asserts this rule. Name it (`File.cpp` › `TEST_METHOD`). Say whether it would really have caught *this* bug or only something nearby.
- **extend**: an existing test or per-level check is the natural home. Name the file and say what to add (a method, a check, a sweep rule). This is the preferred outcome, because a test that grows beats a new file.
- **new**: give the file it belongs in, following the README's file naming and folder rule.

If pending CLs might hold relevant tests, `p4 opened -a {{P4_DEPOT_ROOT}}/.../{{UE_TEST_MODULE}}/...` shows them. Mention the CL, but don't count it as covered.

### f. Cost and priority (value ÷ cost)

Estimate **hours** for one dev who knows the harness: unit/asset-data rule ≈ 1–3 h, extending a player-flow test ≈ 1–4 h, new player-flow test ≈ 4–8 h, needs new test-action/fixture support ≈ 8–16 h, needs harness work first ≈ 16 h+. Label these as estimates.

Score each `yes`/`maybe` item:

| Factor | Points |
|--------|--------|
| Severity | 3 = crash, hang, item dup/loss, exploit, progression block · 2 = feature broken · 1 = minor or cosmetic-adjacent |
| Recurrence risk | +2 already regressed once, or the data is authored often (new weapons, items, levels) · +1 area changes often · 0 one-off |
| Confidence | High +2 · Medium +1 · Low 0 |
| Cost | ≤2 h 0 · ≤8 h −1 · ≤16 h −2 · >16 h −3 |
| Coverage | covered −3 (nothing to do) · extend +1 |

**P0** ≥ 6 · **P1** 4–5 · **P2** 2–3 · **P3** ≤ 1. The script below does the arithmetic. You supply the factor values and a one-line reason for each, because the reasons are what the user will push back on.

## 3. Scale: fan out for long lists

For up to about 15 items, judge them inline. For more, split them into batches of about 15–30, grouped by system so each agent reads one area of the code. Spawn one `general-purpose` agent per batch, all in a single message. Give each agent:

- the path to this SKILL.md, with an instruction to apply sections 1–2 to its batch,
- its items (inline, or a JSON file path),
- where to write: `<out>/batch_<name>.json`, written progressively so work isn't lost,
- a reply limit: verdict counts and the file path only, no per-bug prose.

## 4. Record and rank

Write every item into `<out>/items.json`, where `<out>` = `{{TEMP_BASE}}\test-feasibility-scratch\<YYYY-MM-DD>-<slug>\`. Write one object per item:

```json
{
  "id": "{{JIRA_PROJECT_KEY}}-12345",
  "kind": "bug | idea",
  "title": "user's wording / Jira summary",
  "system": "Weapons",
  "symptom": "one plain sentence: what the player saw (or the idea's rule)",
  "root_cause": "one sentence from fix CL/code, or \"unknown\"",
  "fix_cls": [1234],
  "verdict": "yes | maybe | no | n/a",
  "tier": "<a tier from the README> | none",
  "oracle": "the objective rule the test asserts",
  "suggested_test": "{{UE_TEST_PREFIX}}Content.Weapons.Attachments.CompatibleWithHost: sweeps every attachment ... asserts ...",
  "confidence": "High | Medium | Low | —",
  "coverage": "covered | extend | new | —",
  "coverage_where": "WeaponContentTests.cpp › AttachmentsResolve (add rule) / new file path",
  "severity": 3, "recurrence": 2, "hours": 2,
  "reason": "one sentence: why this verdict and confidence",
  "blocker": "harness gap or open question, if any"
}
```

Then run the ranker, which computes the scores, sorts the items and writes `report.md`:

```bash
python -I -X utf8 "$KC_PROJECT_ROOT/.claude/skills/test-feasibility/scripts/rank.py" "<out>/items.json" --title "<short title>"
```

It merges every `batch_*.json` in the folder when `items.json` is missing, and it fails loudly on missing fields. Fix those fields and re-run it rather than editing the report by hand.

## 5. Reply

Shape the chat reply so the next action comes first:

1. **Start here**: the top 1–3 P0 items to write first, with hours. One line each.
2. **Counts**: yes / maybe / no / n-a, and how many are already covered.
3. **Ranked table** of every `yes` and `maybe`, highest priority first:

   | # | ID | Item | Verdict | Tier | Confidence | Priority | Coverage | Est. | Test |
   |---|----|------|---------|------|-----------|----------|----------|------|------|

   For long lists, show the top 20 and point to the report for the rest.
4. **Not automatable**: `no` and `n/a` as a one-line-each list (ID: reason). The user needs to see that these were considered, not skipped.
5. **Open questions**: the Low-confidence designer questions, plus any harness blockers that recur across items (for example, "the test map lacks a required actor: blocks 4 items").
6. The report path. For more than about 30 items, offer to publish the report as a Claude Doc for the team.

Close with the reminder that verdicts are judgements made from tickets and code, and nothing was run.

## Gotchas

- Don't stretch a `maybe` into a `yes` by imagining an elaborate test. The bar is "about a day on today's harness". Note the heavier test under `blocker` instead.
- A bug fixed by a content edit to one asset is a `yes` only when a **general** rule over all assets of that type would have flagged it. One-off art and placement tweaks are `no`.
- Bugs that are open now: the suggested test will land red. Say so in `blocker`, because the team decides whether known-failing tests gate or report.
- Several items often share one test (a snap matrix, a per-level check). Call out the shared test in the report so it's built once, and give each item the shared test's name.
