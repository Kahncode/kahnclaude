# Asset Inspector Reference

## Asset Path Conventions

Asset paths must be game-relative, starting with `/Game/`:

```
/Game/AI/Definitions/Passengers/BD_Passenger_TC
/Game/Blueprints/Items/BP_Sword
/Game/DataTables/DT_ItemStats
```

Do NOT use filesystem paths (e.g. `Content/AI/...`). The scripts expect Unreal's internal package path format.

## Property Types

The `set` action auto-detects value types:

| Input | Detected Type | Example |
|-------|--------------|---------|
| `3.14`, `0.5` | float | `set /Game/X prop 3.14` |
| `42`, `0` | int | `set /Game/X prop 42` |
| `true`, `false` | bool | `set /Game/X prop true` |
| Anything else | string | `set /Game/X prop MyValue` |

## Nested Struct Properties

Use dot-separated paths for nested properties:

```
config.patrol_distance
config.behavior.aggression_level
movement.max_speed
```

Example: `set /Game/AI/BD_Enemy config.patrol_distance 500.0`

## Scripts

| Script | Purpose |
|--------|---------|
| `read_uasset_property.py` | Read one or all properties as JSON |
| `set_uasset_property.py` | Set a property and auto-save the asset |
| `dump_asset_properties.py` | Full property dump with sorted listing + JSON export |
| `find_asset_referencers.py` | Query Asset Registry for referencing assets |
| `find_level_actors.py` | Template script — requires CLASS_FILTER replacement |

## Asset Registry Methods

`find_asset_referencers.py` tries two methods in order:

1. `AssetRegistry.get_referencers()` — primary, uses the in-memory asset registry
2. `EditorAssetLibrary.find_package_referencers_for_asset()` — fallback, scans packages

## Actor Search

`find_level_actors.py` runs inside the editor process (imports `unreal` directly). It:

1. Gets all actors in the current editor world
2. Filters by class name containing `CLASS_FILTER` (case-sensitive substring)
3. Reports per actor: display name, class, location, rotation, and custom properties

## Prerequisites

- Unreal Editor must be running
- Python Remote Execution enabled (`bRemoteExecution=True` in `DefaultEngine.ini`)
- For `dump`: saves `asset_dump.json` to the current working directory
