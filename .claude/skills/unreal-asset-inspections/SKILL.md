---
name: unreal-asset-inspections
description: "UE5 asset expert. ALWAYS invoke when the user asks to inspect, read, set, or dump asset properties, find referencers, or find actors in a level. Do not run asset scripts directly — this skill handles all asset operations via editor Python."
allowed-tools: Bash(python3 *), Read
---

# Asset Inspector

Inspect and modify UE5 assets via the running editor's Python Remote Execution.

## Reference

See @docs/standards/unreal/unreal-asset-inspections.md for asset path conventions, property types, and script details.

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `KC_PROJECT_ROOT` | Workspace root (parent of `.claude/`) |
| `KC_UE_ENGINE` | UE root directory |

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

```bash
# All properties
python3 "$KC_PROJECT_ROOT/scripts/unreal/unreal-asset-inspections/read_uasset_property.py" "$ASSET_PATH"

# Specific property
python3 "$KC_PROJECT_ROOT/scripts/unreal/unreal-asset-inspections/read_uasset_property.py" "$ASSET_PATH" "$PROPERTY_NAME"
```

#### Set Property

> **Warning:** This modifies the asset directly without Perforce changelist tracking or verification. For tracked modifications with P4 discipline (changelist, baseline dump, verification, shelving), use the `blueprint-dev` agent instead. Proceed here only for quick one-off changes where tracking is not needed.

```bash
python3 "$KC_PROJECT_ROOT/scripts/unreal/unreal-asset-inspections/set_uasset_property.py" "$ASSET_PATH" "$PROPERTY_PATH" "$VALUE"
```

Report old and new values. Asset is auto-saved after modification.

#### Dump Properties

```bash
python3 "$KC_PROJECT_ROOT/scripts/unreal/unreal-asset-inspections/dump_asset_properties.py" "$ASSET_PATH"
```

Shows sorted key=value listing. Saves full JSON to `asset_dump.json`.

#### Find Referencers

```bash
python3 "$KC_PROJECT_ROOT/scripts/unreal/unreal-asset-inspections/find_asset_referencers.py" "$ASSET_PATH"
```

#### Find Actors in Level

1. Read the script template at `$KC_PROJECT_ROOT/scripts/unreal/unreal-asset-inspections/find_level_actors.py`
2. Replace `CLASS_FILTER` with the user's class name
3. Execute the modified script as inline code via Python Remote Execution

## Notes

- All actions require the editor running with Python Remote Execution enabled.
- Asset paths must be game-relative (e.g. `/Game/AI/Definitions/BD_Passenger_TC`).
- Actor search uses case-sensitive substring matching on class name.
