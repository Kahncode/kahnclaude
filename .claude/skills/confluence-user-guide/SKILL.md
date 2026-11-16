---
name: confluence-user-guide
description: "Illustrated Confluence user guide for a system. ALWAYS invoke for /confluence-user-guide [system] or when a system's Confluence page should be created or refreshed with drawings: 'illustrated Confluence page for X', 'redo this page with /illustrate'. Keeps the current content; interactive figures go in HTML macros. Prefer over illustrate and to-confluence-page for Confluence."
---

# Confluence user guide

Turn one system's Confluence page into an illustrated user guide. The steps:
1. Find or confirm the page.
2. Export what's there now.
3. An agent runs `/illustrate`, starting from the existing content.
4. Another agent converts the result and publishes it: native Confluence for everything static, HTML macros only for interactive figures, full width.

The heavy steps run in agents, so this conversation keeps only their short reports. `/illustrate` alone reads code, history and docs for 30+ minutes.

`{SKILL_DIR}` below means the absolute Windows path of `.claude/skills/confluence-user-guide` (`<home>\.claude\skills\confluence-user-guide`, `~` expanded: `file_upload` needs a literal path).

## 1. Find the page and get one confirmation

The argument is a system name ("Inventory", "Networking"), a Confluence URL, or a page ID.

- **URL or ID:** that's the page. Read its title with `mcp__atlassian__searchConfluenceUsingCql` (`id = <ID>`).
- **System name:** search space {{CONFLUENCE_SPACE_KEY}} (cloud ID `{{CONFLUENCE_CLOUD_ID}}`) with CQL, for example `space = {{CONFLUENCE_SPACE_KEY}} AND type = page AND (title ~ "<system>" OR text ~ "<system>") ORDER BY lastmodified DESC`. Keep the 3 most likely pages: the title names the system, a guide or overview page, or under a matching parent.

Then ask **one** AskUserQuestion. This is the only stop before publishing, so make the question carry the whole decision:
- When a page was found or given: "Update <title> (<URL>) with an illustrated guide? Its current text and images are exported first (downloaded to `{{DOWNLOADS}}` as cug-export-<id>.json) and kept on the new page. The old version stays in page history." Options: each candidate page, plus "Create a new page".
- When nothing fits: offer the likely parents from the search, the system's area, and the root page `{{CONFLUENCE_ROOT_PAGE_ID}}`, for a new page titled "<System> user guide".

A "Create a new page" answer needs its parent, so ask that follow-up too. Otherwise don't ask anything else until the end.

Workspace: `{{TEMP_BASE}}\confluence-user-guide-<slug>\`, where slug is the system in kebab-case. If that folder already has files from an earlier run, use `…-<slug>-2` and so on. Never delete an old run.

## 2. Export the existing page (agent)

Skip this step for a new page. Otherwise spawn an agent with the brief in `references/agent-export.md`, filled with PAGE_ID, TITLE, WS and SKILL_DIR, and wait for it. It downloads the page body and every image it shows, then unpacks them into `<WS>\existing\` (`content.md`, `macro-N.html`, `images/`, `images.json`, `images.md`).

Images are the hard part to recreate: real screenshots someone took by hand. That's why they are exported as files and the next agents must place every one.

## 3. Illustrate (agent)

Spawn an agent with the brief in `references/agent-illustrate.md`, filled with SYSTEM, TITLE, PAGE_ID, PARENT_ID (from `<WS>\existing\page.json`, or the parent chosen for a new page), WS and SKILL_DIR. Run it in the background and wait for its notification; don't do the work yourself meanwhile. The agent:
- checks the neighbouring pages first (the parent, the parent's other children, the page's own children). A concept a neighbour already explains gets a short card and a link there instead of a second full explanation.
- invokes the `illustrate` skill and writes `<WS>\page.html`, in the Blue scale colours, drawn wide, and without the illustrate concept index.
- marks each interactive figure with `data-widget` so the converter can split it, and places every kept image.
- writes `screenshots-wanted.md`, `notes.md` and `neighbours.md`.

If it reports kept images it couldn't place, or converter warnings it couldn't fix, send it back with SendMessage once. If that doesn't fix them, tell the user and stop before publishing.

## 4. Convert and publish (agent)

Spawn an agent with the brief in `references/agent-publish.md`. Fill:
- `TARGET_ARGS`: `--page-id <id>` for an update; `--parent-id <id> --space-id {{CONFLUENCE_SPACE_ID}} --label user-guide` for a new page.
- `EXISTING_ARG`: `--existing "<WS>\existing"`, or nothing for a new page.
- `TARGET_TEXT` and `PAGE_OR_PARENT_ID`.

It runs `scripts/to_adf.py`, which produces:
- native ADF with Confluence's table of contents at the top (`--toc-level 2`) and the Blue scale scheme (`--scheme bluescale`, the default, from `assets/schemes.json`): coloured h2 headings, tinted table headers, custom-colour panels.
- drawings rendered at their display width: up to 1100 px, at most 650 px high, enlarged at most 1.6×. Screenshots keep their real size.
- PNG figures rendered with headless Chrome in the scheme's colours.
- a script check of every widget.
- kept attachments, reused by fileId.

It then publishes from a logged-in Chrome tab with `scripts/publish.js`: images uploaded, page body updated, `content-appearance-*` set to `max` (full width), the title emoji set if the page has none, and labels on a new page. Finally it checks the live page.

The publish agent stops instead of publishing when a widget script fails or a kept image would disappear. Pass that report on to the user as it is.

## 5. Report

Read `<WS>\screenshots-wanted.md` and `<WS>\notes.md` (both are short), then reply:
- **Page:** the link, and whether it was updated (version N) or created.
- **What's on it:** concepts, figures, widgets as HTML, images kept N of N.
- **Linked instead of repeated:** each neighbour page from `neighbours.md` that the page now links to, and for which concept.
- **Check first:** the single most important thing from `notes.md`.
- **Screenshots worth taking:** the numbered list from `screenshots-wanted.md`, as written. When the user later sends a screenshot folder, rerun steps 3 and 4 with those files. The illustrate skill's `references/screenshots.md` covers how to place and annotate them.

## Why it works this way

- **Native first.** Confluence search, comments, page history, editing and dark mode work on native content, and not inside an HTML macro. Interactive figures are the only things Confluence can't do itself.
- **Link, don't repeat.** A concept explained on two pages drifts apart. The neighbour pages own their concepts, and this page summarises them in a few lines and links there.
- **Confluence's own table of contents.** It replaces the illustrate concept grid, which took a whole screen of height. It lists the h2 headings, one per concept card.
- **A title emoji on every page.** The illustrate agent starts the `<h1>` with an emoji that fits the system. `publish.js` sets it as the page emoji (`emoji-title-*` properties), which shows in the title and the sidebar. It never replaces an emoji the page already has.
- **Blue scale colours.** Red and green mean only wrong and right, and things differ by depth of blue, with violet only for the selection. The native parts use Confluence's own palette, so they still adapt to dark mode. The figures and widgets take the scheme's CSS tokens. Add or change a scheme in `assets/schemes.json`.
- **Wide figures.** On the old HTML pages, figures filled the content width up to 1100 px. A native image shows at the pixel size it is given, so `to_adf.py` renders each drawing at its display size and sets that size on the image.
- **Diagrams as PNG.** A static SVG has no native equivalent; a PNG attachment shows everywhere, including mobile and exports. It is rendered in the light theme, so it won't switch to dark mode.
- **Widget macros.** Each one is a separate small page: the page CSS, the shared helpers, and only the script statements that drive it. The converter checks each one in headless Chrome before upload. In a macro, links open a new tab, because navigating the top page is blocked in its frame.
- **Publishing through the browser tab.** The Confluence MCP tools would need the whole body retyped. Loading the bundle file into the logged-in tab sends it as it is.

## Files

- `scripts/to_adf.py`: converter (with `dom.py`, `adf.py`, `widgets.py`, `jsunits.py`, `render.py`). `--no-render` is a quick dry run.
- `scripts/publish.js`: browser publisher; it travels inside `bundle.json`.
- `scripts/export.js`, `scripts/unpack_export.py`: export of the current page.
- `references/agent-*.md`: the three agent briefs.
