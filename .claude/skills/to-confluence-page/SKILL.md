---
name: to-confluence-page
description: "Confluence page publisher. ALWAYS invoke when the user asks to create, update, publish or sync a Confluence page, or to put local Markdown docs (any .md file or folder, a game wiki) on Confluence. Do not call Confluence MCP tools directly: this skill confirms space and parent, removes local links, renders Mermaid as images and follows project conventions."
allowed-tools: Read, Grep, Glob, Write, Bash, mcp__atlassian__*, mcp__claude-in-chrome__*
---

# Create or Update Confluence Pages

Use PROACTIVELY when the user says: `create confluence page`, `update confluence page`, `publish to confluence`, `publish wiki to confluence`, `sync wiki`, or points at local `.md` docs and a Confluence page.

## Reference

See @docs/standards/confluence/confluence-page.md for spaces, page structure, formatting, and env vars.

## Required Variables

| Variable | Fallback |
|----------|----------|
| `CONFLUENCE_CLOUD_ID` | Ask user for any Atlassian URL, auto-extract from `_edge/tenant_info` |
| `CONFLUENCE_SPACE_KEY` | Ask user or detect via `getConfluenceSpaces` MCP |

## Optional Variables

| Variable | Default |
|----------|---------|
| `CONFLUENCE_ROOT_PAGE_ID` | _(none)_ -- new pages created as children of this |

`PROJECT_ROOT`/`UE_*` paths are set in the process env by `.claude/settings.local.json` `env`; Jira/Confluence IDs come from .claude/rules/project-vars.md.

Project specifics: read {{PROJECT_NOTES_DIR}}\to-confluence-page.md if it exists.

## Confluence-Ready Content (applies to every mode)

A Confluence reader has no checkout and no Markdown renderer, so two things that look fine locally are broken there:

1. **Local links.** `[example.md](example.md)`, `../Source/Foo.h`, `C:\...` or a visible `foo.md` name points at the author's disk. Every link must go to a real URL: another doc becomes a link to its Confluence page with the **page title** as the text (`Spawning Subsystem`, not `spawning.md`); a same-page anchor becomes `#Heading-Text`; a local file with no page becomes plain text with no link. Source paths can stay as inline code, because they name code and don't pretend to be links.
2. **Mermaid.** Confluence shows a `mermaid` code block as raw text, and a Mermaid app on the site may not render either (the project notes say if it is known broken). Render each diagram to a PNG, attach it to the page and embed the image. Keep the source in a collapsed "Diagram source (Mermaid)" expand so the next editor can change it.

`scripts/md_to_confluence.py` does both and refuses to output a page that still has a local link, a `.md` name or a bare Mermaid block. Use it for any Markdown source rather than converting by hand.

## Flow

### 1. Detect Mode

- User points at local Markdown files or a folder (e.g. `{{SUBSYSTEM_DOCS_DIR}}`): **Local Docs Mode** (below)
- User asks to publish a **game wiki** or **subsystem wiki**: **Wiki Mode** (below)
- User provides a page ID or title of an existing page: **update mode**
- Otherwise: **create mode**

### 2. Confirm Target

- Confirm space key (from `CONFLUENCE_SPACE_KEY`)
- Confirm parent page (from `CONFLUENCE_ROOT_PAGE_ID` or ask user)
- For update mode: fetch existing page with `getConfluencePage` to show current content

### 3. Draft Content

- Ask user for the page title and content topic
- Draft content following project conventions detected from existing pages
- Apply **Confluence-Ready Content** above. If the draft has a diagram, write it as Mermaid in a local `.md` and publish it through Local Docs Mode, so it is rendered to an image.
- Present draft to user for review before publishing

### 4. Create or Update

**Create:** Call `createConfluencePage` with:
- `spaceId`: resolved from `CONFLUENCE_SPACE_KEY`
- `title`: from user input
- `body`: drafted content
- `parentPageId`: from `CONFLUENCE_ROOT_PAGE_ID` (if set)
- Add relevant labels

**Update:** Call `updateConfluencePage` with:
- Page ID from lookup
- Updated `body` content
- Preserve existing labels, add new ones as needed

### 5. Confirm

Reply with the page URL so the user can verify the result.

### 6. Recommend Specialist Review

After publishing, recommend a review based on page content:

- **Technical/architecture content** (code references, system design, data flow): suggest running the `documenter` agent to verify technical accuracy and progressive discovery. Its diagrams go through Local Docs Mode.
- **Game design/balance content** (mechanics, tuning values, ability definitions): suggest running the `designer` agent to cross-reference code values and verify design accuracy.
- **General content**: no recommendation needed.

This is a recommendation, not mandatory — keep the skill fast for routine updates.

---

## Local Docs Mode

For one or more local `.md` files: a folder sync, a wiki, or a doc the user names. The MCP tools would make you retype every page and can't upload images, so this mode builds bodies on disk and publishes them from the user's logged-in Chrome tab.

### L1. Map docs to pages

- List the parent's children (`getConfluencePageDescendants`) and match each doc to an existing page by title or topic. Docs that cover a different area than the parent (e.g. a map-data doc under a combat page) need the user to choose where they go.
- Show the mapping table (doc → page ID/title, *update* or *create*) and ask about anything that would drop content already on the page, such as a section the local doc doesn't have.
- Create missing pages first with a one-line placeholder body via `createConfluencePage` (parent = the target parent), so every page has an ID before links are rewritten.
- Write the map to `{{TEMP_BASE}}\to-confluence-<scratch|CL>\pages.json`: `[{"source": "<absolute path with / separators, e.g. {{SUBSYSTEM_DOCS_DIR}}>/example.md", "pageId": "123456789", "title": "Example Subsystem"}]`. Put every doc that other docs link to in the map, even if it isn't being published now, so links to it resolve to its page.

### L2. Build

```bash
python -I "$KC_PROJECT_ROOT/.claude/skills/to-confluence-page/scripts/md_to_confluence.py" --map pages.json --out build [--only example.md]
```

Run it from `{{PROJECT_ROOT}}` (it reads the site and temp folder from `.claude/rules/project-vars.md`). The first run installs python-markdown and mermaid-cli into `{{TEMP_BASE}}\to-confluence-tools\`. Rendering uses the installed Chrome, so no diagram text leaves the machine. Never use mermaid.ink, Kroki or another online renderer: the docs describe internal code.

Each doc gets `build/<stem>/bundle.json`, `body.xhtml` and the PNGs. The doc's `# H1` is dropped because Confluence shows the page title.

If the build stops:
- **"Mermaid render failed"**: the diagram has a syntax error, and a Mermaid-aware viewer would fail on it too. Fix it in the source `.md` and tell the user what you changed. A common cause is `;` in a sequence-diagram `Note` or message, which Mermaid reads as the end of a statement; use a comma.
- **"not publishable"**: a local name or link survived. Add the missing doc to `pages.json`, or reword the source.

Diagrams render at natural size (`useMaxWidth: false`). mmdc's default 800 px window used to squeeze wide diagrams until the text was about 3 px. A `WARNING ... px wide` line means the diagram is wider than the page: it is sharp when clicked but small inline. Mention it to the user, and suggest `graph TD` or splitting the diagram rather than changing their doc yourself.

Open one or two PNGs with Read before publishing to check they are legible.

### L3. Publish from Chrome

Per page, in one tab of your own (`tabs_create_mcp`) on `{{CONFLUENCE_URL}}/...`:

1. Inject the file input: `javascript_tool` → `const i=document.createElement('input');i.type='file';i.setAttribute('aria-label','cc-bundle-upload');document.body.appendChild(i);'ok'`
2. `find` "file input labelled cc-bundle-upload", then `file_upload` one or more `bundle.json` files (set `i.multiple=true` in step 1 for several; 10 MB total per upload).
3. Read `scripts/publish_bundle.js` and run its text with `javascript_tool`. For each bundle it uploads the PNGs (same name = new attachment version), PUTs the storage body with version +1, and re-reads the page. It returns one report per page.
4. The page is done only when the report shows `imagesMissingAttachment: []`, `mdNamesLeft: 0`, `localHrefs: []`, `mermaidCodeBlocks: 0`.
5. Navigate to the page, wait about 6 s, and confirm the diagrams loaded: `[...document.querySelectorAll('img')].filter(i=>i.naturalWidth>300).length` should be at least the diagram count. Prefer this to a screenshot, because screenshots of this Confluence tab often time out.

Don't `fetch` a localhost server from the Confluence tab: Chrome's local-network check freezes it. That's why the bundle goes through a file input. Close your tab when finished.

### L4. Report

Give a table: doc → page link, version before → after, number of diagrams, any source fixes. Labels: add `ai`/`architecture` (or matching topic labels) to newly created pages.

---

## Wiki Mode

When the user asks to publish a **game wiki** or **subsystem wiki** to Confluence:

### W1. Resolve Subsystem

Parse the subsystem name from the user's request.

### W2. Check Local Wiki

Check if `{{PROJECT_ROOT}}\docs\wikis\<subsystem>.md` exists.

- **Does not exist:** Inform the user that no local wiki exists for this subsystem. Ask if they want to create content manually or provide the wiki content.
- **Exists:** Read the wiki file content. Ask the user: "Publish this wiki as-is, or would you like to make changes first?"

### W3. Publish

Publish the wiki file through **Local Docs Mode** (L1–L4), so its links and diagrams are converted.

### Wiki Rules

- The local wiki file (`{{PROJECT_ROOT}}\docs\wikis\<subsystem>.md`) is the source of truth
- One subsystem per invocation
- Always confirm with the user before publishing

---

## Rules

- Never delete existing pages
- Always add labels to new pages
- Always show draft content to user before creating/updating. In Local Docs Mode, the mapping table plus "converted from your local docs" counts, since the user wrote the content.
- Create new pages under the configured root page ID
- Detect conventions (ToC macro, status lozenges, heading hierarchy) from existing pages in the space
- No published page may contain a local link, a visible `.md` file name, or Mermaid source as its only diagram
