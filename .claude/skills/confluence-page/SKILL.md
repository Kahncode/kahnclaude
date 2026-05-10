---
name: confluence-page
description: "Confluence page expert. ALWAYS invoke when the user asks to create, update, or publish a Confluence page. Do not call Confluence MCP tools directly — this skill confirms space/parent, drafts content, and publishes with project conventions."
allowed-tools: Read, Grep, Glob, mcp__atlassian__*
---

# Create or Update Confluence Pages

Use PROACTIVELY when the user says: `create confluence page`, `update confluence page`, `publish to confluence`.

## Reference

See @docs/standards/confluence/confluence-page.md for spaces, page structure, formatting, and env vars.

## Required Environment Variables

| Variable | Fallback |
|----------|----------|
| `CONFLUENCE_CLOUD_ID` | Ask user for any Atlassian URL, auto-extract from `_edge/tenant_info` |
| `CONFLUENCE_SPACE_KEY` | Ask user or detect via `getConfluenceSpaces` MCP |

## Optional Environment Variables

| Variable | Default |
|----------|---------|
| `CONFLUENCE_ROOT_PAGE_ID` | _(none)_ -- new pages created as children of this |

## Flow

### 1. Detect Mode

- If user provides a page ID or title of an existing page: **update mode**
- Otherwise: **create mode**

### 2. Confirm Target

- Confirm space key (`$CONFLUENCE_SPACE_KEY`)
- Confirm parent page (`$CONFLUENCE_ROOT_PAGE_ID` or ask user)
- For update mode: fetch existing page with `getConfluencePage` to show current content

### 3. Draft Content

- Ask user for the page title and content topic
- Draft content following project conventions detected from existing pages
- Use Confluence-compatible markdown formatting
- Present draft to user for review before publishing

### 4. Create or Update

**Create:** Call `createConfluencePage` with:
- `spaceId`: resolved from `$CONFLUENCE_SPACE_KEY`
- `title`: from user input
- `body`: drafted content
- `parentPageId`: `$CONFLUENCE_ROOT_PAGE_ID` (if set)
- Add relevant labels

**Update:** Call `updateConfluencePage` with:
- Page ID from lookup
- Updated `body` content
- Preserve existing labels, add new ones as needed

### 5. Confirm

Reply with the page URL so the user can verify the result.

### 6. Recommend Specialist Review

After publishing, recommend a review based on page content:

- **Technical/architecture content** (code references, system design, data flow): suggest running the `documenter` agent to verify technical accuracy, add Mermaid diagrams, and ensure progressive discovery.
- **Game design/balance content** (mechanics, tuning values, ability definitions): suggest running the `designer` agent to cross-reference code values and verify design accuracy.
- **General content**: no recommendation needed.

This is a recommendation, not mandatory — keep the skill fast for routine updates.

## Rules

- Never delete existing pages
- Always add labels to new pages
- Always show draft content to user before creating/updating
- Create new pages under the configured root page ID
- Detect conventions (ToC macro, status lozenges, heading hierarchy) from existing pages in the space
