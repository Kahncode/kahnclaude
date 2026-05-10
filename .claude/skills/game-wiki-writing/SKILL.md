---
name: game-wiki-writing
description: "Game wiki author. ALWAYS invoke when the user asks to write, create, or update a game wiki, system wiki, or GAMEWIKI index. Do not write wiki docs manually — this skill gathers balancing data from UE5 assets and delegates to the designer agent."
---

# Write Game Wiki

@docs/standards/design/game-wiki-writing.md

**Input:** $ARGUMENTS

## Flow

### Mode Detection

- No args, "index", or "all": **Index mode**
- Subsystem name provided: **Subsystem mode**

### Index Mode

1. Glob for `docs/wikis/*.md`
2. Read each file's frontmatter for system name, description, and last-updated
3. Write or update `docs/GAMEWIKI.md` following the index format in the standards doc
4. Done

### Subsystem Mode

1. Spawn a `designer` agent (`subagent_type: designer`) with:
   - The subsystem name
   - Instruction to grep the codebase for relevant code (DataTables, DataAssets, GameplayEffects, AttributeSets, config values)
   - Instruction to run asset inspection scripts via Bash for discovered UE5 assets:
     ```
     MSYS_NO_PATHCONV=1 python3 "$KC_PROJECT_ROOT/scripts/unreal/unreal-asset-inspections/dump_asset_properties.py" "<asset_path>"
     ```
   - Reference to @docs/standards/design/game-wiki-writing.md for the required format
   - Instruction to write the result to `docs/wikis/<subsystem>.md`
2. After the designer finishes, run **Index Mode** to update GAMEWIKI.md

## Rules

- Always follow the format in @docs/standards/design/game-wiki-writing.md
- Include source asset paths in the Balancing Data section so data can be refreshed
- Never fabricate values — only use data from code or asset inspection
- Create `docs/wikis/` directory if it doesn't exist
