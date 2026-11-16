# Brief for the illustrate agent

Fill the `{…}` fields and pass everything below the line as the Agent prompt (subagent_type `general-purpose`).
Leave out the "Existing page" block when the page is new. `{PARENT_ID}` is the page's parent: `parentId` in `<WS>\existing\page.json`, or the parent chosen for a new page.

---

Build an illustrated user guide for **{SYSTEM}** by invoking the `illustrate` skill (Skill tool, skill `illustrate`), then make the page ready to convert for Confluence. Work local only: **do not publish an Artifact**. Someone else converts and uploads your file.

**Output files** (all in `{WS}`):
- `page.html`: the finished page. This exact path overrides the illustrate skill's default path.
- `screenshots-wanted.md`: the illustrate skill's numbered "screenshots I'd like from you" list, in its usual format. Always write it, even though you're not publishing. Leave out shots the kept images already cover. If nothing is missing, write `None.`
- `notes.md`: anything you marked unverified, docs that disagree with the code, and the one thing the user should check first.

**Who reads it:** game coders on the team, on Confluence. It is a user guide: how the system works, how to use it, how to change it, and how to test it. Follow the illustrate skill's system-page shape, with the changes below.

## First: what the pages around it already cover

The page sits in a tree, and the team doesn't want the same explanation in two places. Before you plan the page, look at its neighbours: the parent page **{PARENT_ID}**, the parent's other children, and this page's own children (page **{PAGE_ID}**; skip this part for a new page). List them with `mcp__atlassian__getConfluencePageDescendants` (cloud ID `{{CONFLUENCE_CLOUD_ID}}`, depth 1). Read a neighbour with `mcp__atlassian__getConfluencePage` (`contentFormat: "markdown"`) only when its title suggests it shares concepts with this topic. Skip unrelated pages, and skip copies or older versions of this same page (same title with a suffix such as "(native)" or "[scratch]").

Write `neighbours.md` in the output folder: one row per neighbour you opened, with title, URL, the concepts it explains well, and your decision for each shared concept.

On the page, a concept that a neighbour already explains well gets:
- a short card: 2-4 sentences of what the reader needs here, and at most one small figure, plus
- a link to that page in bold: **Full explanation: [Page title](URL)**.

The full mechanism, its figures and its gotchas stay on the other page. Concepts no neighbour covers get the full concept card as usual. End the page with a **Related pages** section that links each relevant neighbour with one line on what it covers.

## Page shape changes

- **Title emoji.** Start the `<h1>` with one emoji that fits the system, like 🧪 for automation tests, 🎒 for inventory or 🗺️ for navigation. It becomes the page's emoji in the Confluence title and sidebar. Pick one that isn't already used by the neighbour pages, so the sidebar stays readable. A page that already has an emoji keeps it.
- **No concept index.** Leave out the `ul.concepts` list, its "Concepts on this page" heading, and the "↑ concepts" links. The converter puts Confluence's own table of contents at the top of the page. Keep the concept map figure, and give every concept card an `<h2>`, because the table of contents lists the `<h2>` headings.
- **Colour: Blue scale** (the default scheme; the tokens are in `{SKILL_DIR}\assets\schemes.json`). The converter replaces the base.html colour tokens with the scheme's when it renders the page, so keep using the variables, and add `--d: #7fa8e6` to your page's `:root` for your own preview.
  - `--a` navy is the main thing on a figure.
  - `--b` blue is the second thing (the other half, the other copy).
  - `--d` sky blue is a third thing.
  - `--c` violet is used **only** for what is selected or needs attention: the active button, the current step, a highlighted box.

  Things differ by how deep the blue is, not by hue. **Red means only wrong and green means only right**, so never use red, green, orange, yellow, cyan or teal for a thing, a tag or a highlight. Give every box in every figure its entity colour, with the stroke in the colour and the fill as `color-mix(in srgb, var(--a) 14%, var(--panel))`. Use neutral `--fg` or `--muted` strokes only for frames and axes. Keep one colour per entity across the whole page.
- **Figures fill the page width.** Drawings are shown up to 1100 px wide, as on the old HTML pages, so draw for that: a wide `viewBox` (760-1100 wide, wider than tall) and text sized for it. A figure taller than wide stays small.

## Existing page (start from it)

The current Confluence page "{TITLE}" was exported to `{WS}\existing\`:
- `content.md` is the native text of the page. `macro-N.html` files are earlier illustrated pages or widgets that were embedded as HTML.
- `images.md` lists **every image the page shows now**, with the section it was in and its caption. `images.json` is the same list for the converter.

Treat the existing content as the starting point. Keep what is still true, correct what the code now contradicts (say so in `notes.md`), and add what is missing. Don't drop sections someone wrote on purpose (owner notes, decisions, links) just because they don't fit the illustrate shape. Fold them in.

**Keep every listed image.** Put each one where it helps the reader, normally the section it came from:
- A screenshot that came out of a `macro-N.html` (key `macN-…`): copy its whole `<div class="shotwrap">…</div>` block from that file, including the highlight layer. Its `<img>` already points at `existing/images/…`. Add `data-keep="KEY"` to that `<img>`.
- Any other image: `<figure><img data-keep="KEY" src="existing/images/FILE" alt="…"><figcaption>…</figcaption></figure>`.
- If an image is truly obsolete (the UI it shows no longer exists), still keep it, under a short "Older screenshots" heading near the end, and say why in `notes.md`.

The converter reports any kept image the page doesn't show, so a missing one will be noticed.

## Make it convertible

Everything static becomes native Confluence content: headings, paragraphs, lists, tables, code blocks, panels, expands, and PNG images of your SVG figures. Only interactive parts stay HTML, each as its own small embedded page. Follow these rules so that split works:

1. **Mark each interactive figure.** Wrap everything one interactive figure needs (controls, SVG or canvas, output box) in one element with `data-widget="Short name"`. Usually that element is the `<figure>`. Keep the `<figcaption>` inside it, and the converter moves it out as native text. Never put a heading inside a widget.
2. **One script per widget.** Write that widget's code in its own `<script data-widget="Short name">` (the same name). Put helpers several widgets use in one `<script>` with no attribute. A widget's script may only look up elements inside its own widget.
3. **Static figures stay static.** An SVG with no script becomes an image. Use the base.html CSS variables as usual; the converter renders it in the light theme.
4. **Interactive means a knob.** Sliders, step/play buttons, toggles, pickers, per-reader checklists. A `<details class="reveal">` is not a widget, because Confluence has native expands.
5. **Links:** full URLs for other pages; `href="#id"` only to a heading or a `section.card` with a heading inside, because those become Confluence anchors.
6. **No `<h1>` beyond the title.** The Confluence page keeps its existing title.

Check before you finish: run `python "{SKILL_DIR}\scripts\to_adf.py" "{WS}\page.html" --out "{WS}\bundle-check.json" --page-id 0 --existing "{WS}\existing"` (drop `--existing` when there is no export). It prints a summary. Fix every warning, and make sure `kept_images_not_placed` is empty and `widgets` lists exactly your interactive figures. Delete nothing.

**Reply** in at most 12 lines: the concept count, figure count, widget names, kept images placed (N of N), the neighbour pages you linked instead of repeating (title → which concept), unverified items, and the paths of the output files (`page.html`, `screenshots-wanted.md`, `notes.md`, `neighbours.md`). Don't paste the page.
