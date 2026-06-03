# Confluence Page Reference

Extracted from @project/docs/tech-stacks/atlassian_confluence.md -- do not edit directly.

---

## Environment Variables

### Required

| Variable | How to Obtain |
|----------|---------------|
| `CONFLUENCE_CLOUD_ID` | Paste any `https://<company>.atlassian.net/...` URL -- Cloud ID fetched from `_edge/tenant_info` |
| `CONFLUENCE_SPACE_KEY` | Paste any space or page URL -- extracted from `/wiki/spaces/<KEY>/...` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFLUENCE_ROOT_PAGE_ID` | _(none)_ | Page ID of team's root page -- new pages created as children |

## Auto-Detection Steps

| Step | MCP Method |
|------|-----------|
| Detect space | `getConfluenceSpaces` -- list spaces, let user pick |
| Detect root page | `getPagesInConfluenceSpace` -- list top-level pages, let user pick |
| Detect conventions | Fetch 2-3 recent pages via `getConfluencePage`, analyze for patterns |

## Convention Patterns to Detect

When analyzing existing pages, look for:
- Table of Contents macro usage
- Status lozenge patterns (e.g., `<ac:structured-macro ac:name="status">`)
- Heading hierarchy conventions (H1 for title, H2 for sections, H3 for subsections)
- Panel/info/warning macro usage
- Common label taxonomy

## Formatting Resources

- [Formatting & Editing Guide](https://www.atlassian.com/software/confluence/resources/guides/confluence-essentials/formatting-editing) -- panels, status lozenges, expand, ToC, slash commands
- [Available Markdown Commands](https://support.atlassian.com/confluence-cloud/docs/available-markdown-commands/) -- headings, bold, italic, code, links, lists, dividers, action items
- [Format Text](https://support.atlassian.com/confluence-cloud/docs/format-text/) -- bold, italic, underline, strikethrough, colors, alignment

## Page Structure Template

A well-structured Confluence page typically follows:

```
# Page Title

## Overview
Brief summary of the page content.

## Details
Main content organized with clear headings.

### Subsection
Detailed information.

## Related Pages
Links to related content.
```

## Key Rules

- Never delete existing pages
- Always add labels to created pages
- Create new pages under the selected root page ID
- Use space conventions detected from existing pages
