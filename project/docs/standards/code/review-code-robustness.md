# Review Code: Robustness — Reference

## Robustness Criteria

### Error Handling

- Try/catch or error returns around all I/O and external calls
- Never swallow errors silently — log with enough context to diagnose
- User-facing error messages must be helpful, not internal stack traces
- Distinguish expected errors (user-facing) from unexpected errors (logged internally)

### UE5 Init Ordering Race Pattern

**Problem**: During initialization, independent actors, components, and subsystems may initialize in any order. Code that assumes a specific order will intermittently fail.

**Two-Phase Collect-Process Pattern**:
```cpp
// Phase 1 — Collect (BeginPlay): gather refs, register, but don't use
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    // Register with subsystem — don't assume subsystem state is ready
    if (UMySubsystem* Sub = GetWorld()->GetSubsystem<UMySubsystem>())
    {
        Sub->RegisterActor(this);
    }
}

// Phase 2 — Process: use refs only after all actors have initialized
// Use a timer, delegate, or game state event to trigger phase 2
```

**Red flags**:
- Accessing another actor's state in `BeginPlay` without null-check
- Assuming a subsystem has completed its `Initialize()` during `BeginPlay`
- Calling functions on components of other actors during `PostInitializeComponents`
- Using `TActorIterator` in `BeginPlay` (not all actors have begun play yet)

### Null-Prone UE5 Patterns

Always null-check results from (see also: correctness dimension for Cast safety):
- `FindComponentByClass<T>()` — nullptr if component missing
- `GetWorld()` — can be null during shutdown
- `GetOwner()` — can be null if component is orphaned
- `TWeakObjectPtr::Get()` — can be null if object was collected
- `GetPlayerController(0)` — null on dedicated server

## Security Checklist

- No hardcoded secrets, API keys, or passwords — use environment variables
- Input validation on all user-provided data and external API responses
- SQL/command injection prevention — parameterized queries, never string concatenation
- XSS prevention — output properly escaped before rendering
- Authentication and authorization checks on all protected operations
- No unsafe deserialization of untrusted data

---

## Review Guidelines

### What to IGNORE
- Performance concerns (other dimension)
- Style and naming (other dimensions)
- Architecture opinions (other dimension)

### Severity Classification
- **CRITICAL**: Silently swallowed error on data-loss path, unguarded init ordering race
- **WARNING**: Missing error handling on I/O, unchecked nullable returns
- **INFO**: Defensive coding suggestions, additional edge case handling
