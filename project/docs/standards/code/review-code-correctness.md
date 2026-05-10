# Review Code: Correctness — Reference

## Correctness Criteria

### Priority 2 — Correctness (from review methodology)

- Logic errors, off-by-one errors, wrong comparisons
- Race conditions and thread safety
- Null/nullptr dereferences
- Unhandled error paths and edge cases

### CRITICAL Severity Patterns

- Raw UObject pointer without `UPROPERTY()` — GC will collect it (crash)
- Unchecked `Cast<T>()` dereference — nullptr crash
- Missing `GENERATED_BODY()` — silent reflection/GC failure
- Replicated property without `DOREPLIFETIME` — desync (data corruption)
- Resource leaks without RAII — data loss path

### From general-code-quality.md

- Logic errors and incorrect branching
- Race conditions and concurrency issues
- Null/nil dereferences — check before use
- Off-by-one errors — especially in loops and array access
- Unhandled errors or panics caught only at the top level

### UE5 Cast Safety

Every `Cast<T>()` result must be null-checked before use:
```cpp
// CRITICAL — crash if cast fails
AMyActor* Actor = Cast<AMyActor>(OtherActor);
Actor->DoSomething();  // nullptr dereference

// Correct
if (AMyActor* Actor = Cast<AMyActor>(OtherActor))
{
    Actor->DoSomething();
}
```

---

## Review Guidelines

### What to IGNORE
- Style, naming, formatting (other dimensions handle these)
- Performance concerns (unless they cause incorrect behavior)
- Architecture opinions

### Severity Classification
- **CRITICAL**: Null dereference, data corruption, race condition, unchecked `Cast<T>()` dereference
- **WARNING**: Suspicious logic that may be intentional but looks wrong, unhandled edge cases
- **INFO**: Defensive coding suggestions that would prevent future bugs
