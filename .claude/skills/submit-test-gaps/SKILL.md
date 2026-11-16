---
name: submit-test-gaps
description: "Finds the automation tests worth adding for game code submitted to {{P4_STREAM}} in the last N days: reads each diff, checks {{UE_TEST_MODULE}} coverage, returns a ranked list and a report. ALWAYS invoke for 'what tests should we add for the last 3d', 'which recent CLs have no tests', '/submit-test-gaps 7d'. For bug lists use test-feasibility; to write a test, test-dev."
---

# Submit Test Gaps

Go through what the team just submitted and say which automation tests would keep each game-code change working. The result is a ranked list a dev can pick from, with the top items ready to hand to the `test-dev` agent.

This is a planning pass: read-only, nothing gets built or run, no Jira writes. Every verdict is a judgement from diffs and code, and the reply says so.

The skill is a pipe between two existing ones: `qa-bug-sweep`'s listing script finds the CLs, and `test-feasibility`'s rules and ranker judge and sort the tests. Only the middle step, reading a CL's diff as "what rule did this make true?", is new. Keep the judging rules in test-feasibility, so the two skills never drift apart.

## Inputs

- **Window**: `Nd`, `Nh`, or "since <day>". Turn it into days. With no window, use 7 days and say so.
- **Focus** (optional): a system, a person, or a word from CL descriptions ("Inventory", a P4 user name, "Weapons").

## Step 1: List and filter (two scripts, a few seconds)

```bash
OUT="{{TEMP_BASE}}/submit-test-gaps-scratch/<YYYY-MM-DD>-<N>d"
python -I -X utf8 "$KC_PROJECT_ROOT/.claude/skills/qa-bug-sweep/scripts/list_changes.py" --days <N> --out "$OUT"
python -I -X utf8 "$KC_PROJECT_ROOT/.claude/skills/submit-test-gaps/scripts/game_cls.py" "$OUT/changes.json" [--focus "<words>"]
```

`list_changes.py` batches the p4 calls and drops bot CLs. Ignore the `Batch N` lines it prints: those are qa-bug-sweep's review batches. `game_cls.py` keeps a CL only if it changed **game code**: C++ in runtime modules under `{{UE_PROJECT_DIR}}\Source` or `{{UE_PROJECT_DIR}}\Plugins\**\Source` (not Editor, Automation, Tests or visualizer modules), or gameplay `.ini` under `Config` (not `*Editor*.ini`). Engine, editor/tooling-only, `[Automation]`-tagged config and asset-only CLs are counted but not judged. It also lists every CL in the window that touched `{{UE_TEST_MODULE}}`, because a test that just landed is coverage. `$OUT/test_cls.md` holds that list in a short form ready to paste into a prompt. Then it splits the game CLs into at most 8 batches, keeping each system together.

With a focus, a CL whose description doesn't name the focus but whose files do is marked `*` and gets a `focus_files` list. Its judge looks only at those files. That still pays off: a "compile fix" CL that quietly changed Inventory behaviour is exactly what this catches.

Tell the user the counts in one line ("N game CLs in M batches; whole window: X asset-only and Y tooling/engine CLs skipped, Z test CLs") and continue without waiting. The skipped counts always cover the whole window, not just the focus.

If there are no game CLs, say so and stop. With 5 or fewer, skip Step 2 and judge them yourself, following `references/judge-prompt.md`.

## Step 2: Judge (one agent per batch, all in ONE message)

Spawn one `general-purpose` agent per batch, all in a single message so they run in parallel. Fill in the prompt from `references/judge-prompt.md`:
- the CL list;
- the contents of `test_cls.md`;
- the workspace warning, only for the CLs it names in that batch;
- the `*` focus note, only for that batch's marked CLs;
- the output path `$OUT/batch_<n>.json`.

Agents fetch their own diffs. Don't fetch diffs yourself: it fills your context, and the agents need it more.

The batch files are the result. Judges sometimes end without sending a reply, so don't wait on one. When every judge has finished, run:

```bash
python -I -X utf8 "$KC_PROJECT_ROOT/.claude/skills/submit-test-gaps/scripts/game_cls.py" --check "$OUT"
```

If it names missing CLs, spawn one more judge for just those CLs, writing `batch_<n>_retry.json`.

## Step 3: Rank

```bash
python -I -X utf8 "$KC_PROJECT_ROOT/.claude/skills/test-feasibility/scripts/rank.py" "$OUT/items.json" --title "Test gaps: last <N>d of {{P4_STREAM}}"
```

With no `items.json` yet, `rank.py` merges every `batch_*.json`, then scores, sorts and writes `$OUT/report.md`. When it names items with missing fields, fix those fields in `items.json` and run it again. Don't edit the report by hand.

Then look across batches for **shared work**:
- **Same test:** two CLs want the same check, for example one per-level sweep or one inventory dup/loss rule. Give both items the same `suggested_test`, add "shared with <ids>" to their `reason`, and re-run `rank.py`. One test that guards three CLs is worth more than three tests.
- **Same file or fixture:** different tests that extend the same test class or need the same setup. Leave the items as they are and list the grouping in the reply, because they're cheaper written together.

`rank.py` still lists each item of a shared test as its own row, and the "Start here" in `report.md` may repeat one test. In the chat reply, merge them into one line ("12345 + 12350: …").

## Step 4: Reply

Put the next action first:

1. **Start here**: the top 1–3 P0 tests to write, one line each with the CL(s), the test name and the hours. A shared test is one line.
2. **Suspected bugs** (only when a judge filled `suspected_bug`): one line each with the CL, author and `file:line`. These come from reading code, not running it. Suggest `investigate` to confirm one, or a Jira ticket. They come before the counts, because a live bug matters more than a missing test.
3. **Counts**: CLs judged → items yes / maybe / no / n/a (covered items counted apart). How many CLs already shipped a test that would really catch a regression. Asset-only and tooling/engine CLs skipped in the whole window.
4. **Ranked table** of every `yes` and `maybe` that isn't covered (top 20, then point to the report). Write test names without the `{{UE_TEST_PREFIX}}` prefix to keep the table narrow:

   | # | CL | Change | Verdict | Tier | Conf. | Priority | Coverage | Est. | Test |
   |---|----|--------|---------|------|-------|----------|----------|------|------|

5. **Shared work**: tests that cover 2 or more CLs, then groups of tests that share a file or fixture.
6. **Not testable**: the `no` items in one line each (CL: reason). Give `n/a` only as a count by kind ("9 n/a: 5 cleanup, 3 refactor, 1 flag flip"), because nobody needs to read those.
7. The report's full absolute path.

Close by offering to hand the items the user picks to the `test-dev` agent, with each item's oracle, tier and file as the plan. Don't start that yourself. Remind the user that verdicts come from reading diffs and code, and nothing was run.

## Judgement notes

- **Change ≠ test.** Most CLs in a week are cleanup, tuning, editor work or one-off content. A report where most items are `n/a`/`no` and a handful are P0 is a good report. Don't stretch a `maybe` into a `yes` to fill the list.
- **Fix CLs are the best candidates.** The bug happened once, and the fix shows the exact rule. The project's CLAUDE.md test rule applies: the suggested test must fail on the build before the fix.
- **Tests shipped with the CL** still get read. A test that only checks that the code runs, without asserting the new rule, is `extend`, not `covered`.
- **Asset-only CLs are counted, not judged.** Blueprint and data diffs can't be read as text. A judge will sometimes notice a pairing from descriptions, for example a config CL and the level that uses it. Mention those, but don't go looking for them.
- **Suspected bugs are a by-product, not the goal.** Report what judges flag. For a bug hunt over the window, point the user to `qa-bug-sweep`.
