# Performance

Will this code perform acceptably?

## Criteria

- **N+1 query patterns** — query in a loop
- **Unnecessary loops** or redundant iterations
- **Memory leaks** — resources not closed, listeners not cleaned up
- **Unbounded allocations** in hot paths

## UE5 Critical Patterns

- **Tick abuse** — >20 lines in Tick, heavy logic per frame
- **`TActorIterator`/`GetAllActorsOfClass` in Tick** — linear scan every frame
- **Missing `Reserve()`** — TArray reallocations in loops
- **Spawning in loops** — `SpawnActor` is expensive, use object pooling
- **Redundant component lookups** — `FindComponentByClass` in hot paths (cache it)

## Container Guidance

- `TArray::Reserve()` when building arrays of known size
- `TSet` for frequent membership tests instead of `TArray::Contains()`
- `TMap` for key-value lookups instead of linear search
- Cache expensive `Cast<T>()` results in loops

---

## Premature Optimization [WARNING]

**Flags:**
- Object pools for rarely-allocated types
- Caching results computed once
- Spatial acceleration for small datasets
- Lock-free structures in single-threaded context

**Ask:** "Is there measured performance data, or is this speculative optimization?"

**Fix:** Start simple. Optimize when profiling shows a bottleneck.
