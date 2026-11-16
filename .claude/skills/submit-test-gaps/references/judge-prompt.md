# Judge prompt (one `general-purpose` agent per batch)

Fill in the `<…>` fields and pass the text below as the agent prompt.

---

You are finding the automation tests the {{UE_PROJECT_NAME}} team should add for game-code changes that were just submitted. Read-only work: no `p4 edit`, no test code, no Jira writes, nothing run.

**Your batch:** CLs <CL list> from `<out>/game_cls.json` (`changes[]` holds each CL's description, author, Jira keys, `game_files`, `config_files`, and `test_files` = automation files the CL itself shipped).

**Tests landed in the same window** (count as existing coverage; full file lists are in `game_cls.json › test_cls[]`):
<paste <out>/test_cls.md>

<Only if game_cls.py printed a WARNING naming CLs in this batch: "Your workspace predates CLs <list>. For those, read files with `p4 print -q <depotFile>@<CL>`, not the local copy.">

<Only if a CL in this batch is marked `*`: "CLs <list> matched the focus (<words>) only through some files. Judge only their `focus_files` and ignore the rest of the CL.">

## Read first (once)

1. `.claude/skills/test-feasibility/SKILL.md`, section 2 (oracle, verdict, tier, confidence, coverage, cost/priority) and Gotchas. Those rules apply here unchanged. Where it says "bug", read "behaviour this CL added or fixed".
2. `{{UE_TEST_README}}` sections 1–2 (tiers, naming).
3. Project specifics: read {{PROJECT_NOTES_DIR}}\submit-test-gaps.md if it exists.

## For each CL

1. **Read what changed.** `p4 describe -du <CL>`. For a big CL (20+ files), start with `p4 describe -s <CL>`, then diff only the `.cpp` files with logic (`p4 diff2 -du <file>#<rev-1> <file>#<rev>`). Skip headers that only move declarations, add comments or add `UPROPERTY` metadata. Open surrounding source when the diff alone doesn't tell you what the code path does.
2. **Split into items.** One item per independently testable behaviour change. Most CLs give one item. A CL with no behaviour change gives one `n/a` item whose reason says so in a few words: don't spend time on it.
3. **Name each item's kind:** `fix` (restores intended behaviour; the description or Jira says what was broken) · `feature` (new rule or capability) · `config` (ini flag, CVar, default) · `tuning` (a balance or timing number) · `refactor` · `cleanup` (warnings, comments, renames, logs). The kind describes the **item**, not the CL's title. A "fix warnings" CL whose rewrite changed behaviour gives a `feature` item for that change, and usually a `suspected_bug` too.
   - **Suspected bug:** while reading, you may see the CL break something: a logic flip in a cleanup, an array mutated while it's iterated, a missing null check on a new path. Put one sentence with `file:line` in `suspected_bug` on that item. Keep judging the item as normal; the bug just gets surfaced separately. Only flag what you can point at in code, never a hunch.
4. **Judge each item** with test-feasibility section 2. What's different here:
   - **Oracle** is the rule the CL established or restored, in one machine-checkable sentence. For a `fix`, the test must **fail on the build before this CL** (project rule). Say how: "before 12345, calling UMyComponent::GetCost with an unloaded item def dereferenced null".
   - **`tuning` is `no`.** Tests never assert tuned values. Only when the CL also adds an objective rule (a clamp, a min/max relationship, "never negative") does that rule become a `yes` item.
   - **`config`** is a `yes` only when the flag gates a behaviour with an objective rule ("AI disabled ⇒ no AI spawns"). A flag flip by itself is `n/a`.
   - **Editor-only paths** inside a game module (`WITH_EDITOR` blocks, details customizations) are `n/a`: players never run them.
   - **Severity** = what a player hits if this change regresses: 3 crash, hang, item dup/loss, exploit, progression block · 2 feature visibly broken · 1 minor.
   - **Recurrence** = +2 the CL fixes a regression, or touches data the team authors often (the project notes list it; else weapons, items, characters) · +1 area got 3+ CLs in this window or is often changed · 0 otherwise.
5. **Coverage.** Check, in this order: the CL's own `test_files` (read them, and say whether they would really fail without the change), the window's test CLs above, then Grep `{{UE_PROJECT_DIR}}\Source\{{UE_TEST_MODULE}}\Private` (Tests, Classes, Actions) for the system's class and function names. Never search `Content/`, `Plugins` trees or `.uasset`/`.umap` files: a hook blocks it, and it freezes the disk. Prefer `extend` (name file › test and what to add) over `new`. For `covered`, `suggested_test` is the exact full name of the existing test that catches it, never a wildcard.

## Write

Write `<out>/batch_<n>.json`: a JSON array, one object per item. Rewrite the file after every CL so work survives an interruption. Use the test-feasibility item schema plus these fields (the `//` notes are for you; write plain JSON):

```json
{
  "id": "12345",             // CL number; "12345-b" for a second item from the same CL
  "kind": "fix | feature | config | tuning | refactor | cleanup",
  "title": "player-facing one-liner: what this CL makes true",
  "author": "<p4 user>",
  "system": "Inventory",
  "symptom": "what a player sees if this regresses",
  "root_cause": "fix only: one sentence; else \"unknown\"",
  "fix_cls": [12345],
  "jira": ["{{JIRA_PROJECT_KEY}}-123"],
  "verdict": "yes | maybe | no | n/a",
  "tier": "<a tier from {{UE_TEST_README}}> | none",
  "oracle": "...", "suggested_test": "{{UE_TEST_PREFIX}}<Tier>.<System>.<Concept>.<Test>: does X, asserts Y",
  "confidence": "High | Medium | Low | —",
  "coverage": "covered | extend | new | —", "coverage_where": "File.cpp › TEST_METHOD (add …) / new file path",
  "severity": 3, "recurrence": 1, "hours": 2,
  "reason": "one sentence: why this verdict and confidence",
  "blocker": "harness gap or open question, if any",
  "suspected_bug": "only when seen in code: one sentence with file:line"
}
```

`yes`/`maybe` items need every field. `no`/`n/a` items need `id, kind, title, system, verdict, tier ("none"), confidence ("—"), coverage ("—"), reason`.

Use game-code nouns from the source, not invented ones. If two of your CLs want the same test, give both items the same `suggested_test` and say "shared with <id>" in `reason`.

## Reply

Only: item counts by verdict, how many CLs already shipped a real test, any `suspected_bug` ids, and the file path. No per-item prose. The batch file is the real result, so finish writing it before you reply.
