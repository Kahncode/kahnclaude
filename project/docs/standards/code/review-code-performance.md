# Review Code: Performance — Reference

## Performance Criteria

### Priority 4 — Performance

- No N+1 query patterns
- Proper pagination on list operations
- No memory or resource leaks (resources closed, listeners cleaned up)
- Independent async operations parallelized

### Game Thread Bottleneck Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Expensive Tick | Heavy logic every frame | `FTimerManager`, event-driven, `SetActorTickInterval` |
| `TActorIterator` / `GetAllActorsOfClass` per frame | Linear scan of all actors | Cache at BeginPlay, use Subsystems, maintain registry |
| Redundant component lookups | `FindComponentByClass` in loops | Cache in member variable |
| String ops in hot paths | `FString` concat, `FName` creation | `static const FName`, direct comparisons |
| Spawning in loops | `SpawnActor` is expensive | Object pooling |
| Collision queries every frame | Complex sweeps/overlaps | Reduce frequency, simpler shapes, async traces |

**Tick abuse rule**: Flag Tick functions >20 lines. Flag `TActorIterator`/`GetAllActorsOfClass` inside Tick, timers under 1s, or per-frame code.

### Memory Patterns

| Pattern | Fix |
|---------|-----|
| Asset duplication | `TSoftObjectPtr` and `FStreamableManager` |
| GC pressure | Object pooling, `FStructOnScope` for temp data, avoid `NewObject` in hot paths |
| Oversized textures | BC7/ASTC compression, texture streaming |

### Network Performance

| Pattern | Fix |
|---------|-----|
| Over-replication | `DOREPLIFETIME_CONDITION`, Push Model |
| Large RPCs | Compress, delta-encode, split updates |
| Poor relevancy | `IsNetRelevantFor`, Net Cull Distance, Replication Graph |

### Container Guidance

- `TArray::Reserve()` when building arrays of known size
- `TSet` for frequent membership tests instead of `TArray::Contains()`
- `TMap` for key-value lookups instead of linear search in `TArray`
- Cache expensive `Cast<T>()` results in loops

## Render / GPU Patterns

| Pattern | Fix |
|---------|-----|
| Too many draw calls | Merge static meshes, ISM/HISM, Nanite |
| Expensive dynamic shadows | Cascaded shadow maps, reduce shadow-casting lights |
| Shader complexity | Material LOD, reduce instruction count |
| Overdraw | Sort translucents, reduce particle size, use opaque where possible |
| Resolution scaling | `r.ScreenPercentage` or `r.DynamicRes.OperationMode=2` |

## Profiling Methodology

**Workflow:** Measure → Profile → Fix top 1-3 → Verify. Never optimize without measuring first.

### Baseline Metrics

| Command | What It Measures |
|---------|-----------------|
| `stat fps`, `stat unit` | Frame time: Game thread, Render thread, GPU |
| `stat game` | Gameplay systems (Tick, components, timers) |
| `stat scenerendering` | Draw calls, occlusion, visibility |
| `stat memory` | Memory usage breakdown |
| `stat net` | Network replication cost |

Record P50/P95 frame times, Game/Render/GPU ms, total memory before any changes.

### Profiling Tools

| Tool | When to Use |
|------|-------------|
| Unreal Insights (`-trace=cpu,frame,bookmark`) | Identify which system dominates frame time |
| `stat startfile` / `stat stopfile` | Capture `.ue4stats` for offline analysis |
| `stat slow [-ms=1.0]` | Log any function exceeding a threshold |
| `SCOPE_CYCLE_COUNTER` / `TRACE_CPUPROFILER_EVENT_SCOPE` | Custom per-function tracking |

If the hot system has no custom stats, **add them first** before optimizing.

### Fix Guidelines

- Fix top 1-3 bottlenecks, one at a time, so each improvement is measurable
- Keep code readable — avoid micro-optimizations that obscure intent
- Use `FORCEINLINE` only when the profiler proves the function is hot AND call overhead matters
- Add stat tracking to any system you optimize so it remains measurable

### Verification

- Re-run the **exact same scenario** (same map, player count, action sequence)
- Compare before/after metrics — target ≥ 2x improvement on the bottleneck path
- Ensure no regressions in other areas

### Report Format

```
# Performance Report — <system/map> (<date>)

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Frame Time (P95) | … ms | … ms | -…% |
| Game Thread | … ms | … ms | -…% |

## Bottlenecks Addressed
1. **<Name>** — impact, root cause, fix applied, result

## Recommendations
- Immediate: [quick wins]
- Next milestone: [larger refactors]
```

---

## Review Guidelines

### What to IGNORE
- Correctness bugs (other dimension)
- Style and naming (other dimensions)
- Micro-optimizations that do not show up in profiling

### Severity Classification
- **CRITICAL**: Resource leak, unbounded allocation in hot path
- **WARNING**: Tick abuse, `TActorIterator` in Tick, missing `Reserve()`, wrong container, Blueprint VM overhead in per-frame code
- **INFO**: `Reserve()` opportunities, caching suggestions, algorithm improvements
