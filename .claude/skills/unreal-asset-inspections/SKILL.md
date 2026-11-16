---
name: unreal-asset-inspections
description: "UE5 asset expert. ALWAYS invoke when the user asks to inspect, read, set, or dump asset properties, find referencers, or find actors in a level. Do not run asset scripts directly — this skill handles all asset operations via editor Python."
allowed-tools: Bash(py *), Read
---

# Asset Inspector

Inspect and modify UE5 assets via the running editor's Python Remote Execution.

## Reference

See @docs/standards/unreal/unreal-asset-inspections.md for asset path conventions, property types, and script details.

## Required Variables

| Variable | Purpose |
|----------|---------|
| `UE_ENGINE` | UE engine root directory (read by the scripts) |

Set in the process env by `.claude/settings.local.json` `env` (the scripts read `UE_ENGINE` from it; never set it inline). The scripts live in `.claude/scripts/unreal/unreal-asset-inspections/`.

## Flow

### 1. Detect Action

Parse `$ARGUMENTS` to determine the action:

| Pattern | Action |
|---------|--------|
| `read <path> [property]` | Read one or all properties |
| `set <path> <property> <value>` | Set a property value |
| `dump <path>` | Dump all properties with sorted key=value listing |
| `referencers <path>` | Find all assets referencing this asset |
| `actors <class>` | Find all actors of a class in the current level |
| Empty or ambiguous | Ask the user what they want to do |

### 2. Execute

#### Read Properties

```
# All properties
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/unreal-asset-inspections/read_uasset_property.py" "<ASSET_PATH>"

# Specific property
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/unreal-asset-inspections/read_uasset_property.py" "<ASSET_PATH>" "<PROPERTY_NAME>"
```

#### Set Property

> **Warning:** This modifies the asset directly without Perforce changelist tracking or verification. For tracked modifications with P4 discipline (changelist, baseline dump, verification, shelving), use the `blueprint-dev` agent instead. Proceed here only for quick one-off changes where tracking is not needed.

```
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/unreal-asset-inspections/set_uasset_property.py" "<ASSET_PATH>" "<PROPERTY_PATH>" "<VALUE>"
```

Report old and new values. Asset is auto-saved after modification.

#### Dump Properties

```
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/unreal-asset-inspections/dump_asset_properties.py" "<ASSET_PATH>"
```

Shows sorted key=value listing. Saves full JSON to `asset_dump.json`.

#### Find Referencers

```
py "$KC_PROJECT_ROOT/.claude/scripts/unreal/unreal-asset-inspections/find_asset_referencers.py" "<ASSET_PATH>"
```

#### Find Actors in Level

1. Read the script template at `.claude/scripts/unreal/unreal-asset-inspections/find_level_actors.py`
2. Replace `CLASS_FILTER` with the user's class name
3. Execute the modified script as inline code via Python Remote Execution

## Notes

- All actions require the editor running with Python Remote Execution enabled.
- Asset paths must be game-relative (e.g. `/Game/Characters/BP_Hero`).
- Actor search uses case-sensitive substring matching on class name.
