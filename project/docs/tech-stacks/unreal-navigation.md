# Unreal Navigation — Nav Octree Memory, Instant vs Lazy Gathering

> Generic UE5 facts, verified in engine source (5.8.x). Project values and measurements: `{{PROJECT_ROOT}}\docs\tech-stacks\navigation.md`.
> Paths are relative to `Engine/Source/Runtime/NavigationSystem/Private/` unless noted. Line numbers drift between engine versions; grep the function name.

## What "Nav tree memory" measures

- `stat navigation` → **Nav tree memory** = `STAT_Navigation_CollisionTreeMemory` (`Engine/Public/EngineStats.h`).
- It is the **navigation octree**, not the navmesh: a copy of the collision geometry (triangles) of every nav-relevant component the nav system has registered, plus nav modifiers.
- Navmesh tiles are counted separately (Recast memory, Detour tile stats).
- The stat is one global counter, so the editor world and the PIE server world add together.
- Known stat drift: `~FNavigationOctree` subtracts `NodesMemory` but not `OctreeSizeBytes` (`NavigationOctree.cpp`), see [UE-166263](https://issues.unrealengine.com/issue/UE-166263).

## When the octree stores geometry

`UNavigationSystemV1::DoesAnyNavDataRequireGeometryStorage` (`NavigationSystem.cpp`):
- **Editor worlds: always** (`!World->IsGameWorld()` → true).
- **Game worlds:** when any nav data is `RuntimeGeneration=Dynamic` or `RequiresInitialRebuild()`.
- `Static` and `DynamicModifiersOnly` game worlds skip geometry (`SkipNavGeometry`). The octree then holds bounds and modifiers only.

So **Dynamic is the reason the geometry is kept**: tiles can be rebuilt at runtime only if the source triangles are still in memory.
**Navigation invokers** (`bGenerateNavigationOnlyAroundNavigationInvokers`) only limit which **tiles are built**. They do not limit what the octree stores.

## DataGatheringMode: Instant vs Lazy

Set on `[/Script/NavigationSystem.NavigationSystemV1] DataGatheringMode`. The engine default is **Instant** (`UNavigationSystemV1` constructor).
Per-element override: `INavRelevantInterface::GetGeometryGatheringMode`. Landscape reads `ALandscapeProxy::NavigationGeometryGatheringMode` (Details → Navigation), `Default` = use the project setting.

| | Instant | Lazy |
|---|---|---|
| When an element registers (`FNavigationOctree::AddNode`) | Full collision exported and stored right away | Bounds only, plus the `bPendingLazyGeometryGathering` flag. No triangles |
| When a tile overlapping the element builds | Uses the stored copy | `DemandLazyDataGathering` exports it then (`RecastNavMeshGenerator.cpp` `GatherNavigationDataGeometry`) |
| Normal meshes after export | Kept until the component unregisters | **Also kept** until it unregisters. Never released when the invoker leaves |
| Landscape (supports geometry slices) | **Whole heightfield** stored as triangles until the proxy unloads | Only the slice under the tile is exported, used, then emptied (`CollisionData.Empty()` when `bDumpGeometryData`). **Never stored** |
| Nav modifiers | Gathered at registration | Deferred until a tile needs them |
| CPU | Paid once at load or stream-in | Paid per tile build. Landscape slices are re-exported on **every** rebuild |

Details:
- "Overlapping" means the element's bounds intersect the tile box grown by the agent radius. A long mesh (road, cliff) is exported **whole** when any tile touches it.
- With invokers and Lazy, octree geometry grows to cover "everywhere an invoker has ever been", and never shrinks while those actors stay loaded.
- Elements are removed from the octree only on unregister (`FNavigationOctree::RemoveNode`): World Partition cell streams out, level unloads, component destroyed.
- Why Instant is the default: tile builds only rasterize (cheaper), the cost lands during loading instead of gameplay, and geometry is snapshotted at registration.
- Why Lazy suits large invoker maps: memory scales with where invokers go, not with the whole loaded map, and the landscape costs about zero.

## Fully async gathering caps tile throughput

`bDoFullyAsyncNavDataGathering=True` (on `RecastNavMesh`) moves geometry gathering off the game thread, but the generator then allows **one tile task at a time** ("temp solution to enforce only one worker thread", `FRecastNavMeshGenerator`, `bDoAsyncDataGathering ? 1 : MaxTileGeneratorTasks`). `MaxSimultaneousTileGenerationJobsCount` is effectively 1.
With Lazy, the export work runs inside that one queue, so navmesh around a newly active invoker can appear more slowly.
Forum report of limited generation with fully async + invokers: <https://forums.unrealengine.com/t/fully-async-nav-data-gathering-with-nav-invokers-results-in-extremely-limited-navmesh-generation/2615304>

## The "too many triangles" warning

`LogNavigation: Warning: Exporting collision geometry with too many triangles (N)` comes from the Recast geometry export when a single element exceeds `GeometryExportTriangleCountWarningThreshold` (NavigationSystemV1, default 200000).
- Usually a static mesh using its render mesh as collision ("complex as simple"). Each placed actor stores its own transformed copy.
- The warning names only the first element of each name in a row (`LastNameHash`). Grep the log for every one.

## Levers to shrink the octree (biggest first)

1. `DataGatheringMode=Lazy` (project-wide), or Lazy on the landscape proxy only.
2. *Can Ever Affect Navigation* = false on anything agents never walk on or around: background, out-of-bounds terrain meshes, decoration, HLODs. Removes the element entirely, better than Lazy for those.
3. Simple (convex/box) collision instead of complex-as-simple on high-poly meshes.
4. Game worlds: `RuntimeGeneration=DynamicModifiersOnly` with a baked, World-Partition-streamed navmesh (`bIsWorldPartitioned=True`) stores **no** geometry. Cost: no runtime rebuild from geometry changes (movable geometry, destruction). This is a design decision.
5. Editor only: load fewer World Partition regions. The editor always stores geometry.

## Measuring

- `stat navigation` → Nav tree memory (read it in the editor **before** starting PIE).
- LLM tag `NavigationOctree` (`-llm`, `stat LLMFULL`).
- A/B test: flip `DataGatheringMode`, restart the editor, reopen the map, compare.
