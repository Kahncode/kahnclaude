# Game Wiki Standards

Standards for game wiki documents in `docs/wikis/`.

## File Structure

- **Index:** `docs/GAMEWIKI.md` — linked table of all wiki files
- **Wikis:** `docs/wikis/<subsystem>.md` — one file per game system

## Frontmatter

Every wiki file must start with YAML frontmatter:

```yaml
---
system: <subsystem-name>
last-updated: YYYY-MM-DD
source-assets:
  - /Game/Path/To/Asset1
  - /Game/Path/To/Asset2
---
```

## Required Sections

Every wiki must have these four sections in order:

### 1. System Overview

Player-facing description of the game system.

- What does the system do for the player?
- When does the player interact with it?
- What is the core fantasy or feeling?

Write in second person ("You gain health when..."), not technical language.

### 2. Core Mechanics

Rules, formulas, and interactions that drive the system.

- Each mechanic gets its own H3 subsection
- Include formulas in fenced code blocks
- Describe input-output relationships
- Note interactions with other systems

### 3. Current Balancing Data

Tables of tuning values pulled from UE5 assets.

| Parameter | Value | Source Asset |
|-----------|-------|--------------|
| BaseHealth | 100.0 | `/Game/Data/DT_PlayerStats` |

Rules:
- Every value must include its source asset path
- Group rows by category (attributes, timers, multipliers, etc.)
- Use exact values from asset inspection — never approximate or guess
- Include the date values were last verified

### 4. Related Systems

Cross-references to other wiki files.

- Link format: `[System Name](wikis/<system>.md)`
- Include a one-line description of the relationship
- Only link systems with actual mechanical interactions

## Formatting Rules

- H1 (`#`) for the system name only
- H2 (`##`) for the four required sections
- H3 (`###`) for subsections within Core Mechanics
- Tables for all numerical data
- Fenced code blocks for formulas
- No emojis

## GAMEWIKI.md Index Format

The index file links all wiki files in a single table:

```markdown
# Game Wiki

| System | Description | Last Updated |
|--------|-------------|--------------|
| [System Name](wikis/<system>.md) | Brief description | YYYY-MM-DD |
```
