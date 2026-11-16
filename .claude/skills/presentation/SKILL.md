---
name: presentation
description: "Slide-deck maker in the user's design-system template. ALWAYS invoke when the user wants a talk, deck, slides or presentation: 'make a presentation about X', 'slides for the team on X', 'a 10-minute talk about X', 'turn this page into a deck'. Gathers real facts and screenshots, proposes outlines, builds a Slides artifact with speaker notes. Not for one-page explainers (illustrate)."
---

# Presentation — a deck about one topic, in Editor Grey

Build a 16:9 Slides deck that a {{UE_PROJECT_NAME}} audience (usually the game code team) understands live in ~10 minutes and that sends them to the full docs at the end. The look is fixed: the **Editor Grey** design system. The content is the work.

**The template (read first, every time):** Editor Grey Design System artifact
`{{PRESENTATION_DS_ARTIFACT_URL}}`. Read its `project/README.md`, `project/layouts.md`, `project/data-and-media.md`, `project/using-the-template.md` (Artifact `read` with `path`). Local snapshot: `{{TEMP_BASE}}\claude-scratch\editor-grey-ds\project\` (may be stale; the artifact wins).
**The reference deck** built in it: `{{PRESENTATION_REFERENCE_DECK_URL}}`. Its slide files are copied in `{{PROJECT_ROOT}}\.claude\skill-fixtures\presentation\example-deck\` (if present; else read them from the reference deck artifact) — one per layout; copy their markup, don't reinvent it (see `references/layouts.md`).

## What the user cares about (learned building the first deck)

- **One idea per slide, the point in the title.** Titles are `Topic: claim` or a question ("Unit: Can you test it without PIE?", "Data: Is every asset valid?"). Big type, few words; the talking points go in the speaker notes.
- **Real over mock-up.** Real function names (`IsValidItem(EmptyItem) → false`), real test names, real screenshots, real numbers with a source. Never invent a statistic, a quote or a screenshot. A rough drawing is only a placeholder, labelled as one, until the real capture exists.
- **Light, airy slides.** When a slide feels heavy, cut words and move them to the notes, swap a table for a picture or a yes/no flowchart, add space under the title (`padding:0 0 40px 0` on the header block).
- **Small green accents.** Blue is the main accent; green is small and repeated: tier chips, page-number digits, step labels, one highlighted card or word. Red means failure only; orange for numbered markers and one warning step.
- **Screenshots cropped tight and balanced.** Crop empty areas off; give side-by-side images the same height. Numbered markers sit *beside* the control with a leader line, never on top of the button.
- **Page numbers** on every slide but the cover: `NN / total` bottom right, number in bold green.
- **Agenda as slide 2**, ideally with a looping GIF of the thing in action on the right.
- **Close with the docs**: "Questions?", one link, its path with the key word in green, a picture of the docs (page tree screenshot).
- **No game key art / logo on the cover** unless the user provides one. The cover is the name strip: `{{UE_PROJECT_NAME}} . Talk . <Area> . <TitleAsTestName>`.
- The user iterates a lot. Make every change they name exactly, and nothing else; offer options in batches (5–50) when they ask for options, with a recommendation.
- English in slides and notes, plain words, no marketing, no em-dash asides.

## Step 0 — Pin the brief (one AskUserQuestion, max 3 questions)

Only ask what isn't already said: audience, length (5 / 10 / 20 min → ~6 / ~11 / ~18 slides), live talk vs read alone (live: short slides + full notes). Default when unsaid: game code team, ~10 min, presented live. Also ask for the **title** only if none is obvious; otherwise propose one.

Mode:
- **Draft mode (default for a real talk)** — outlines → draft board → deck. Use it when the user says "talk", "presentation for the team", or gives a date.
- **Quick mode** — straight to the deck. Use it when the user says "quick", "just make it", "rough deck", or it is under ~6 slides.

## Step 1 — Gather facts (before any slide)

Match the topic:
- **{{UE_PROJECT_NAME}} system / test / tool**: the Confluence pages first (space {{CONFLUENCE_SPACE_KEY}}; the registry `{{CONFLUENCE_PAGE_REGISTRY}}`), then the code (`Grep` scoped to `{{UE_PROJECT_DIR}}\Source\<Module>`, real function names and `file:line`), `p4 changes -m 10 -l` on the main files, memory notes, Jira (`project = {{JIRA_PROJECT_KEY}} AND text ~ "<topic>"`). More than 2 source files to read → one Explore agent brings back conclusions.
- **A CL or bug**: `p4 describe -s`, the Jira ticket, the test that caught it, the Horde run.
- **General topic**: web search; cite sources in the notes.

Collect, per likely slide: the one claim, 1–3 real examples (names, numbers, file names), and the **visual** that proves it.
**Screenshots that already exist**: Confluence pages built with illustrate / confluence-user-guide keep their source captures under `{{TEMP_BASE}}\illustrate-scratch\<topic>\screens\` (editor windows, Horde pages, Slack posts). Look there before asking the user to capture anything. Everything else goes on the capture list (Step 3).

Never invent numbers, names or links; mark anything unverified in the notes ("not verified: …").

## Step 2 — Outline options (draft mode)

Publish ONE private HTML page (Artifact quickstart `intent: "other"`, then a plain page) with 3–6 outline options. Each option: a name, the slide list, which slides carry the must-cover parts, and a one-line pitch; mark one **Recommended** and say why in one line. Talks that worked: cover → agenda (+GIF) → why → 2–4 "how" slides (one per kind/step) → run it → what happens on CI → when it goes red → docs/Q&A.
The user picks one (or merges). Don't build yet.

## Step 3 — Draft board (draft mode)

One private HTML page the user can click through. Per slide:
1. **Preview**: the real slide markup at 1920×1080, scaled into a 16:9 box (`transform: scale(width/1920)`), in Editor Grey colours.
2. **Approved** ideas (the user's picks, pre-ticked) and **5–10 more ideas** (headline + what's on the slide), clickable.
3. **Screenshots and GIFs to add**: what to capture, where it goes; thumbnails for ones already found ("Have it").
4. **Speaker notes** draft.
A fixed bottom bar with **Copy my picks** (clipboard, with a select-text fallback) produces `slide 3 3.1 Title + 3.4 …` the user pastes back. Store picks in `localStorage` with try/catch; bump the key when ids change.
Iterate on the user's pasted picks and comments until they say to build. Keep slide numbers and page numbers in sync when slides are inserted.

## Step 4 — Build the deck

1. `Artifact` quickstart `intent: "slides"` with `design_systems: false`, then create from the **Slides** type (`type_url` from the quickstart), `title` = the talk title, `auto_open: "after_first_write"`. Follow the instructions that result returns, with these choices:
   - **Install Editor Grey** (Creating step 3): `designSystems` record `{"title":"Editor Grey","namespace":"editorgrey","artifact":"{{PRESENTATION_DS_ARTIFACT_URL}}","version":null,"copiedAt":"<now>"}` and the `files` entry `"project/ds/editorgrey/tokens.json": {"artifact":"{{PRESENTATION_DS_ARTIFACT_URL}}","path":"project/tokens.json"}` in the same call as `project/deck.json` + the cover.
   - `faces`: `roboto` (`https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap`) and `jetbrains-mono` (`https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap`). No other faces.
2. **Upload media first** (`asset: true`, `file_paths` for up to 25 at once) and use the returned `/_blob/<id>` verbatim. The example deck's `/_blob/` ids belong to the old deck; never reuse them. Media rules: `references/media.md` (15 MB per file, cropping, GIF compression with ffmpeg).
3. Write `project/deck.json` (full `order`, `sections`, faces, the `designSystems` record), then the cover; send them together. Then three slides per call, in order.
4. Each slide = one `<section>` copied from the matching example-deck layout (`references/layouts.md`), with:
   - the eyebrow + title header, same place on every content slide;
   - the page number `<p>` before the `<aside>`;
   - an `<aside>` of speaker notes, 60–150 words, full sentences, carrying the details the slide leaves out (numbers, file names, CLs, the story behind a screenshot). Notes are visible to anyone with the link: nothing private.
5. Fit check by arithmetic before writing (the type's slide format): safe area 1664 × 792 with `padding:128px 128px 160px`; heading ≈ size × lines × 1.15; text wraps at ~0.6 × size per character; code lines at 24px mono are 14.4px per character. Too tall → cut text or split; nothing under 24px.
6. Don't render or re-read the deck to verify (the Slides type forbids it unless the user asks).

## Step 5 — Hand over

Link + the slide list in one line each, then what's left for the user: placeholders (`[Talk date]`, captures still drawn), sharing (private until Share menu), export (Share › Export › PowerPoint; Google Slides = upload the .pptx to Drive › Open with Google Slides; Roboto and JetBrains Mono are built into Google Slides). End with the usual after-task block: What I did / What to check / Next step / Context warning.

## Revising a deck the user has already seen

Edit only the slide files the user named (Edit, then publish those files to the deck `url` with `root`), never rebuild. Slide inserted → update `deck.json` `order`, every later page number (`NN / total`), and the agenda numbers. New image → upload, then reference the new `/_blob/<id>`.

## Files

- `references/layouts.md` — which example slide to copy for each layout, and the fixed snippets (header, page number, name strip, card, code panel, marker + leader line, flowchart boxes).
- `references/media.md` — finding, cropping and compressing screenshots and GIFs on this machine.
- `{{PROJECT_ROOT}}\.claude\skill-fixtures\presentation\example-deck\` (optional, if present) — the 11 finished slides and `deck.json` of the reference deck.
