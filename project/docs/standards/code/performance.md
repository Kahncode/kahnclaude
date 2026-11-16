# Performance

Will this code perform acceptably?

## Criteria

- **N+1 query patterns** — database/API query in a loop
- **Unnecessary loops** or redundant iterations
- **Memory leaks** — resources not closed, listeners not cleaned up
- **Unbounded allocations** in hot paths

## Critical Patterns

- **Heavy logic in hot paths** — complex computation per-frame or per-request
- **Linear scans in loops** — O(n²) when O(n) is possible
- **Missing pre-allocation** — array/buffer reallocations in loops
- **Expensive operations in loops** — object creation, I/O, network calls
- **Redundant lookups** — same expensive operation repeated when result could be cached

## Container Guidance

- Pre-allocate when building collections of known size
- Use sets for frequent membership tests instead of list contains
- Use maps/dicts for key-value lookups instead of linear search
- Cache expensive operation results when used multiple times

## Database/Query Performance

- Batch queries instead of one-per-item
- Use appropriate indexes for common query patterns
- Limit result sets — avoid `SELECT *` without `LIMIT`
- Consider pagination for large datasets

---

## Premature Optimization [WARNING]

**Flags:**
- Object pools for rarely-allocated types
- Caching results computed once
- Spatial acceleration for small datasets
- Lock-free structures in single-threaded context

**Ask:** "Is there measured performance data, or is this speculative optimization?"

**Fix:** Start simple. Optimize when profiling shows a bottleneck.

---

## Severity Classification

- **CRITICAL**: O(n²) in production hot path, unbounded memory growth, N+1 in request handler
- **WARNING**: Missing pre-allocation, redundant lookups in loops, heavy computation in hot path
- **INFO**: Optimization opportunities, caching suggestions
