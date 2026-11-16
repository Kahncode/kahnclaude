---
name: illustrate
description: "Illustrated explainer page builder. ALWAYS invoke when the user wants a bug, system or concept explained WITH DRAWINGS: 'explain X with a drawing', 'illustrate how X works', 'draw the issue', 'make a page I can show the team about X'. Gathers real facts (file:line, Perforce, Jira, docs), then publishes a private Artifact with SVG and interactive figures. Not for Confluence (confluence-user-guide)."
---

# Illustrate — teach one subject with many good drawings

Produce one HTML page that makes a reader *see* how something works or why it breaks, and gives them the vocabulary to work on it. The usual reader is a **game coder** being onboarded to a system, or reviewing a change in it. Three tests for the finished page:
- Could they redraw the key figures from memory and explain the mechanism?
- Do they now recognise every recurring concept and function they'll meet in this code, and know what each is for?
- Could they change, test or review this code tomorrow using only this page and its links?

The user's taste, learned from review (keep to it):
- **Simple explanations, calm look.** Short plain sentences, grey/neutral background, muted colours (`assets/base.html` has the right palette). Never a saturated "explosive" palette.
- **Complete vocabulary.** Every recurring concept, idiom and function of the system gets explained (section 2). Missing core ideas, like the automation fixture's "queue now, run later", was the biggest complaint.
- **Detailed and visual.** Every concept with a mechanism, space, sequence or set of states gets its own drawing; systems typically end up with 8–15 figures.
- **Interactive wherever there is a knob.** Sliders, step-through "play" buttons, toggles, small animations, 2D or 3D views.
- **Figures early.** The first screen already shows a picture.
- **Real screenshots where there is real UI.** Take them where possible and ask for the rest (section 3), cropped with red boxes, numbered circles and arrows.
- **Grounded and linked.** `file:line` references, real diffs, Perforce history, Jira bugs, Confluence pages, Epic documentation, and a "try it yourself in PIE" section.
- **Teaching first** (section 4): learning goals, concrete before abstract, predict-then-reveal, worked example, check-yourself, recap.

Three kinds of subject, each with its own page shape (section 5):
- **Issue** — a bug, flake, regression, "why does X happen". Project CLs and Jira keys usually mean this.
- **System** — how a subsystem is put together and how data/control flows through it.
- **Concept** — a general idea (a theorem, a protocol, an algorithm) with no codebase behind it.

## 1. Gather facts before drawing anything

A wrong drawing is worse than no drawing, because people trust pictures. So first collect what's true:

- **Code:** read the actual functions. Record `path:line` for every claim, using the **full file name** (`LyraGameplayAbility_RangedWeapon.cpp:540`, never a shortened `RangedWeapon.cpp`) and the revision you read (`p4 have <file>`, or "workspace, opened in CL N" if it's modified locally).
- **Perforce history (code subjects):** `p4 changes -m 15 -l <files>` on the main files, `p4 describe -s` on the interesting ones. Recent CLs (number, date, author, summary), especially bug fixes, and pending CLs on the same files (`p4 opened -a <files>`).
- **Recent bugs:** memory notes and Jira (`project = {{JIRA_PROJECT_KEY}} AND text ~ "<system>" ORDER BY updated DESC`). Keys, summaries, status.
- **Existing team docs:** search Confluence (space {{CONFLUENCE_SPACE_KEY}}, CQL `space = {{CONFLUENCE_SPACE_KEY}} AND text ~ "<system>"`) and the repo's `docs/` and module READMEs. Keep titles and URLs, and note where they disagree with the code.
- **Engine documentation:** for engine features the system builds on (AI/Behavior Trees, GAS, Replication Graph, CQTest/Automation, Enhanced Input, World Partition…), find the matching pages on `dev.epicgames.com/documentation/unreal-engine/...` with a web search. Link only pages you actually found; never guess a URL.
- **Issues:** pull the evidence that exists — CL descriptions, Jira ticket, logs under `{{TEMP_BASE}}`, memory notes, measured numbers. Label each claim *confirmed* (measured, logged, reproduced) or *hypothesis*.
- **How to see it live:** console commands, cvars, debug draws (`ShowDebug …`, the system's own cvars, `p.NetShowCorrections`), log categories, and the automation tests that exercise this code.
- **Concepts:** get the maths or protocol exactly right. When a figure depends on geometry, compute coordinates (a few lines of Python) instead of eyeballing them.
- For large project subsystems, use one or two Explore subagents to map code, history and docs and bring back conclusions; then read the key functions yourself.

Never invent numbers, file paths, line numbers or links. If you couldn't verify something, say so on the page ("not verified: …").

## 2. Build the concept map before writing

Before outlining the page, list the **concepts and sub-concepts** a coder needs to work in this subject. This is what keeps the page from "missing a lot". Write the list down (in your notes, then as the page's concept index).

How to find them, for code subjects:
1. **Entry points:** the classes and functions people call from outside (the public API, the test macros, the console commands).
2. **What callers actually use:** count how often the system's functions/types appear in the code that uses it (for the automation framework: which fixture/action functions the tests call most; for an inventory system: which component functions gameplay code calls). `rg -o "Fixture\.\w+" {{UE_PROJECT_DIR}}/Source/{{UE_TEST_MODULE}} | sort | uniq -c | sort -rn | head -30` style counts. High counts = recurring concepts that must be on the page.
3. **Core idioms:** the patterns the code is built on that aren't a single function (queue-now-run-later, server/client halves, ready gates, one-per-tick queues, rewinding history). These are often the most important concepts and the easiest to miss.
4. **Data and config:** the structs, data assets, ini sections and cvars that control behaviour.
5. **Words the team uses:** memory notes, `UBIQUITOUS_LANGUAGE.md`-style glossaries, Confluence titles.

Group them into 4–8 **concepts**, each with its sub-concepts, and order them so each builds only on earlier ones. Example (Gameplay Ability System): *Abilities & tags* → *Activation* (CanActivateAbility, cost, cooldown, commit) → *Prediction* (prediction keys, rollback) → *Effects & attributes* (instant / duration / infinite, modifiers, executions) → *Replication* (full / mixed / minimal, gameplay cues) → *Debugging* (`showdebug abilitysystem`, log categories).

Then every concept gets a **concept card** on the page (section 5): what it is, why it exists, how it works (figure), real code, how to use it, gotchas, links.

For issue pages, the concept map is smaller: the 3–6 concepts needed to understand the bug (e.g. net role, actor ownership, relevancy, tick order), each explained briefly before the bug itself. For concept pages, it's the sub-ideas of the proof or protocol.

## 3. Plan the figures

Answer in one sentence: *what is the single thing the reader most needs to see?* That becomes the lede and the central figure. Then give each concept card a figure where one helps. Pick each form from the content:

| Content | Figure |
|---|---|
| The concept map itself | component/concept map with each node linking (`<a href="#card-id">`) to its card |
| Two places / frames / copies of one thing (local vs world, server vs client) | side-by-side panels, same element highlighted in both |
| Something ends up in the wrong place | right place and wrong place on one drawing, gap labelled with its formula |
| Space: cells, ranges, radii, zones, who-sees-what | top-down grid/map drawn to scale, actor and radius/cells highlighted |
| Decisions the code takes | vertical flow of steps, each with `file:line`, bad path and fix marked |
| Timing, races, ordering, deferred execution | swim lanes (server / client / time axis, or "queued" vs "runs" lanes) |
| Components and data flow | boxes + labelled arrows; several small figures rather than one crowded one |
| States and transitions | state diagram with the triggering events on the arrows |
| Categories / tiers / types | a row of small pictograms or cards, one per kind |
| History | timeline of CLs and bugs on one axis |
| Geometry / maths | construction to scale with computed coordinates + worked numbers |

**Make figures interactive whenever something can vary:** sliders for parameters, play/step buttons for sequences, before/after toggles, hover/click to highlight. Plain SVG + a few lines of JS; `<canvas>` or a small three.js scene (cdnjs, pinned) when motion or 3D really matters. Every interactive figure must read correctly at rest.

`references/figures.md` has ready patterns for each of these, including interactive and 3D ones. Read it before drawing.

Exaggerate small effects so they're visible (a 3° angle drawn as 12°) and say so. Keep colour meaning fixed across the page: one colour per entity, green for correct, red for wrong. Small pictograms or emoji are welcome when they encode meaning.

**Plan the screenshots too.** For code subjects with anything visible (editor windows, menus, overlays, the game view, Horde, Swarm, reports, logs), write a shot list and read `references/screenshots.md`. Take every shot you can without disturbing anyone: web pages through Claude in Chrome, already-open windows through `scripts/capture_window.py`. Never launch the editor or interrupt a session for a picture. View each shot before using it and correct the page from what it shows. Pure concept pages usually need none.

## 4. Teach, don't catalogue

The page is a lesson, not a reference sheet. (Same principle as the project's `create-tutorial` skill.) Use these moves; each does a job for the reader:

- **Say what they'll learn.** Under the lede, 2–4 "After this page you can…" goals phrased as abilities.
- **Start from what they already know.** One line on prerequisites; an **analogy** for abstract mechanisms (dormancy as motion-sensor lights; a pose ring buffer as a video you can scrub back), and where it stops working.
- **Concrete before abstract.** One real case first, then the rule. Numbers before symbols.
- **Build up in layers.** Simplest true version first, then the complications one figure at a time. Each card relies only on earlier cards.
- **Predict, then reveal.** Ask before a key result; answer in `<details class="reveal">` or let an interactive figure answer it.
- **Show real code at the moment it explains something.** 5–15 lines with `file:line` beat a table describing them.
- **Name the misconceptions.** "Looks like X, actually Y" boxes, including docs that disagree with code.
- **Worked example, then "your turn"** with the answer hidden.
- **Check yourself.** 3–5 questions near the end testing the goals; prefer "what happens if…" and "where would you change…".
- **Recap** in 3–5 bullets, plus where to go next.
- **Introduce each term once**, in bold, with a one-line meaning; reuse the project's names.

## 5. Page shape

Start from `assets/base.html` — theme tokens (light + dark), type, layout and components (`.facts`, `.flow/.step`, `figure`, `.diff`, `.timeline`, `.card`, `.concepts`, teaching blocks, tables). Copy and fill it; don't rebuild the CSS.

**Concept card** (the unit of a system page; smaller versions on issue and concept pages):
- `<section class="card" id="card-…">` with the concept's name and a one-line definition.
- **Why it exists** — the problem it solves, in one or two sentences.
- **How it works** — a figure (interactive if something varies) and a short explanation; sub-concepts as small headed parts inside the card.
- **In the code** — a 5–15 line excerpt and the main `file:line` refs.
- **How to use it** — the common recipe a coder needs ("to wait for X, call…", "to add a wave, add a row to…"), as a short snippet or steps.
- **Gotchas** — what goes wrong, from code, bugs and history.
- **Learn more** — related Confluence page, Epic doc, test, or the card it builds on.

**System page:**
1. Title, lede (what the system is for, in one sentence a designer would understand), learning goals, and the **concept map figure** on the first screen, its nodes linking to the cards.
2. A compact **concept index** (`.concepts` list: concept → sub-concepts, each linked).
3. One **concept card per concept**, in build-up order. Go deep: real defaults, real constants, real order of checks.
4. An end-to-end walk-through of one real scenario that uses the concepts together (step-through figure if possible).
5. Key classes table: class · file · responsibility.
6. History: recent CLs and bugs (timeline + table), and docs that disagree with the code.
7. Invariants and gotchas across the system.
8. Try it yourself in PIE: map, how to make it happen, console commands/cvars/debug views, log categories, the automation tests to run.
9. Where to change X — common edits and the file they live in.
10. **Learn more:** team docs (Confluence, repo docs), Epic documentation pages for the engine features involved, related systems' pages.
11. Check yourself, recap.

**Issue page:**
1. Eyebrow (ticket · system · CL), short title, lede (symptom and cause in plain words), learning goals, and a figure on the first screen.
2. Fact tiles: the numbers that matter.
3. **Background concepts:** short cards for the 3–6 concepts needed to understand the bug.
4. The code path as a flow with `file:line` on every step; bad branch and fix marked.
5. Why it goes wrong — the central figure (interactive if a parameter drives the error), with its formula or rule.
6. Evidence: observed vs predicted / before vs after.
7. Why it's intermittent / why nobody saw it; wrong leads ruled out.
8. The fix: a real diff, current state, what is still unverified.
9. History: recent CLs and bugs on the touched files.
10. Try it yourself in PIE; knock-on effects and open questions; learn more; check yourself, recap.

**Concept page:**
1. Title, lede, learning goals, the intuition figure first; formal statement second.
2. Cards for the sub-ideas, building up to the proof or protocol, drawn as figures (interactive when it helps); the algebra too.
3. A worked example with real numbers, then "your turn".
4. Variations, where it's used, common mistakes, learn more (classic references found by search), check yourself, recap.

Drop a section only when there is nothing true to say in it.

## 6. Craft rules

- **Theme-aware drawings.** Every SVG fill/stroke/text colour uses the CSS variables from `base.html` (`var(--a)`, `var(--bad)`, …), never a literal colour. Same for canvas/three.js: read colours from `getComputedStyle(document.documentElement)`. Every SVG shape gets an explicit `fill` (`none` where intended).
- **Phone width.** Each SVG sits in `.svgbox` with a `viewBox` and `width:100%`; nothing pushes the page wider.
- **Labels don't collide.** Leave room in the viewBox for outer labels; check positions, especially after rotations.
- **Each figure has** an `aria-label` and a caption saying what to notice.
- **Line references** in the small mono `.ref` style, full file name, old location too if the code moved.
- **Plain words.** Short sentences, active voice, the project's own nouns.
- **Long pages stay navigable:** the concept index links to every card; each card ends with a small "↑ concepts" link back.
- **External assets:** Google Fonts (linked in base.html) and, only when needed, one pinned cdnjs library (e.g. three.js). Links to Confluence/Epic docs are fine (they open in a new tab).
- **Check the page once** before handing it over: parse the SVGs or render it headless, and fix overlaps or broken scripts. For screenshots, view each `shotfrags/<id>-preview.png` and fix any highlight that misses its target.

## 7. Output

1. Write the page to a file:
   - If the task gives an output path, use exactly that.
   - Otherwise `{{TEMP_BASE}}\illustrate-scratch\<slug>.html` (project temp-file rule).
2. Publish it as a private Artifact with the Artifact tool, following that tool's own rules (quickstart with intent `other` before a first publish; `icon` on first publish; a one-sentence `description`). Republish the same file path to update it.
   - **Skip publishing** when the task says "local only", "don't publish", or gives an explicit output directory for evaluation.
3. Reply briefly:
   - the link (or the local path when not published),
   - what the page explains, in one sentence, and how many concepts it covers,
   - anything on the page marked unverified,
   - the most important thing for the user to check,
   - **the screenshots you'd like from the user**, as a numbered list saying what to show and where it goes (format in `references/screenshots.md`). Don't hold the page back waiting for them. Skip this list when publishing is skipped or nothing is missing.
4. When the user sends a screenshot folder, follow `references/screenshots.md` section 3: view all of them, place, crop, highlight, correct the page, republish, and say what's still missing.
