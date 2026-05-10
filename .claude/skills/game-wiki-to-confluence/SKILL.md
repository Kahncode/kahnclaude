---
name: game-wiki-to-confluence
description: "Game wiki publisher. ALWAYS invoke when the user asks to publish a game wiki to Confluence, push a wiki to Confluence, or sync a system wiki. Do not call Confluence tools directly — this skill ensures the local wiki is current, then delegates to the confluence-page skill."
allowed-tools: Read, Grep, Glob
---

# Wiki to Confluence

**Input:** $ARGUMENTS

## Flow

### 1. Resolve Subsystem

Parse $ARGUMENTS for the subsystem name (required).

### 2. Check Local Wiki

Check if `docs/wikis/<subsystem>.md` exists.

- **Does not exist:** Inform the user, then invoke `/game-wiki-writing <subsystem>` to create it. Continue after it completes.
- **Exists:** Ask the user: "The local wiki for <subsystem> already exists. Update it before publishing?"
  - **Yes:** Invoke `/game-wiki-writing <subsystem>`, then continue.
  - **No:** Continue with the existing file.

### 3. Publish

Read `docs/wikis/<subsystem>.md` and invoke `/confluence-page` with the wiki content to create or update the Confluence page.

### 4. Confirm

Report the Confluence page URL to the user.

## Rules

- Always confirm with the user before updating an existing wiki
- One subsystem per invocation
- The local wiki file is the source of truth — never bypass it to publish directly
