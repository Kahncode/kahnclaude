# Tech Stack Guide: Atlassian Confluence

<!-- detection: opt-in | signal: confluence in README or docs references | prerequisite: none -->
<!-- prompt: "Do you want to set up Confluence integration for documentation and knowledge base?" -->

---

## Setup — Environment Variables

Store in `CLAUDE.local.md` (never committed).

### Required

> **Tip:** Just paste any Confluence URL (e.g., `https://mycompany.atlassian.net/wiki/spaces/TEAM/pages/123456`) and Claude will auto-extract the Cloud ID and space key.

| Variable | How to Obtain |
|----------|---------------|
| `CONFLUENCE_CLOUD_ID` | Paste any `https://<company>.atlassian.net/...` URL — Cloud ID is fetched automatically from `_edge/tenant_info` |
| `CONFLUENCE_SPACE_KEY` | Paste any space or page URL — space key is extracted from `/wiki/spaces/<KEY>/...` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFLUENCE_ROOT_PAGE_ID` | _(none)_ | Page ID of the team's root page — new pages are created as children of this |

---

## Setup — Auto-Detection

No manual questions required. All configuration is auto-detected via MCP, then confirmed with the user.

| Step | Method | CLAUDE.md Section |
|------|--------|-------------------|
| 1. Detect space | `getConfluenceSpaces` MCP — list spaces, let user pick | Service Ports |
| 2. Detect root page | `getPagesInConfluenceSpace` MCP — list top-level pages, let user pick | Project Rules |
| 3. Detect conventions | Fetch 2-3 recent pages via `getConfluencePage`, analyze for common patterns (ToC macro, status lozenges, heading hierarchy) | _(applied silently)_ |

### Defaults (no question needed)

- Never delete existing pages
- Always add labels
- Create new pages under the selected root page ID

---

## Operational Reference — Confluence

### Content Format

**Always use ADF (Atlassian Document Format) when updating pages.** Markdown format strips images, layouts, and rich formatting. ADF preserves all content including embedded media.

```
contentFormat: "adf"   ✓ preserves images, tables, panels, layouts
contentFormat: "markdown"   ✗ strips images and rich content
```

### Space

Configure your space key in CLAUDE.md or CLAUDE.local.md:

```
CONFLUENCE_SPACE_KEY: <YOUR_SPACE>
```

### Formatting & Editing References
- [Formatting & Editing Guide](https://www.atlassian.com/software/confluence/resources/guides/confluence-essentials/formatting-editing) — panels, status lozenges, expand, table of contents, slash commands
- [Available Markdown Commands](https://support.atlassian.com/confluence-cloud/docs/available-markdown-commands/) — headings, bold, italic, code, links, lists, dividers, action items
- [Format Text](https://support.atlassian.com/confluence-cloud/docs/format-text/) — bold, italic, underline, strikethrough, colors, alignment, subscript/superscript

### Key Pages

Configure your team's key page index here:

| Page ID | Title |
|---------|-------|
| `<ID>` | Team Root Page |
| `<ID>` | How-To Guide |
| `<ID>` | Debug Commands |

### Key Folders

| Folder ID | Purpose |
|-----------|---------|
| `<ID>` | Release Notes |
| `<ID>` | Playtest Feedback |
