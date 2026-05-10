# Review Code: Debuggability — Reference

## Log Categories

Every module/system must define its own log category. Never use `LogTemp` in production.

```cpp
// Header
DECLARE_LOG_CATEGORY_EXTERN(LogMySystem, Log, All);
// Source
DEFINE_LOG_CATEGORY(LogMySystem);
```

## Verbosity Levels

| Level | Use for |
|-------|---------|
| `Fatal` | Unrecoverable errors — crash immediately |
| `Error` | Serious failures — state corruption or broken functionality |
| `Warning` | Unexpected but recoverable conditions |
| `Display` | Key game events visible in shipping (use sparingly) |
| `Log` | Normal operational info — stripped in shipping |
| `Verbose` | Detailed diagnostics for debugging |
| `VeryVerbose` | Extremely detailed trace-level output |

## Log Message Quality

Messages must include context: **what happened, which object, what values**.

```cpp
// Good
UE_LOG(LogCombat, Warning, TEXT("ApplyDamage: %s received %.1f from %s. Health: %.1f"),
    *GetName(), Damage, *Instigator->GetName(), Health);

// Bad
UE_LOG(LogTemp, Log, TEXT("damage applied"));
```

## On-Screen Debug Messages

Always guard with `#if !UE_BUILD_SHIPPING`:
```cpp
#if !UE_BUILD_SHIPPING
if (GEngine)
    GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Red, TEXT("Debug info"));
#endif
```

## UE Assertion Macros

| Macro | When | Behavior |
|-------|------|----------|
| `check(expr)` | Programming error — must never be false | Crashes Dev/Debug, stripped Shipping |
| `ensure(expr)` | Unexpected but recoverable | Logs callstack once, returns false |
| `ensureMsgf(expr, TEXT("..."))` | Same with message | Logs message + callstack |
| `verify(expr)` | Side effects must run in Shipping | Crashes Dev, evaluates in Shipping |
| `checkNoEntry()` | Unreachable code path | Marks unreachable branches |

Never use raw `assert()` — use UE macros above.

## Stat Tracking

For performance-sensitive systems, add tracking:
```cpp
DECLARE_CYCLE_STAT(TEXT("MySystem Tick"), STAT_MySystem_Tick, STATGROUP_Game);
void UMySystem::Tick(float DeltaTime)
{
    SCOPE_CYCLE_COUNTER(STAT_MySystem_Tick);
}
```

## UE_LOGFMT (Structured Logging, UE 5.2+)

```cpp
#include "Logging/StructuredLog.h"
UE_LOGFMT(LogCombat, Warning, "Actor {Name} took {Damage} damage",
    ("Name", GetName()), ("Damage", DamageAmount));
```

Prefer `UE_LOGFMT` over `UE_LOG` in new code — named fields are searchable in Unreal Insights.

---

## Review Guidelines

### What to IGNORE
- Correctness bugs (other dimension)
- Performance concerns (other dimension)
- Style and naming (other dimensions)

### Severity Classification
- **CRITICAL**: None typical for this dimension
- **WARNING**: `LogTemp` in production, unguarded `AddOnScreenDebugMessage`, raw `assert()`, missing log category
- **INFO**: Log verbosity suggestions, stat tracking additions, `UE_LOGFMT` opportunities
