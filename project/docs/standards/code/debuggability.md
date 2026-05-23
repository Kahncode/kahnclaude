# Debuggability

Is this code diagnosable in production?

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

## Critical Path Logging

Important code paths must have enough logging to diagnose issues without a debugger. Add logs at:

| Path Type | What to Log |
|-----------|-------------|
| **Operation entry** | Key inputs, caller context if non-obvious |
| **Decision branches** | Which branch taken and why (the deciding value) |
| **State transitions** | Old state → new state, what triggered it |
| **External calls** | Request sent, response received (or failure) |
| **Error recovery** | What failed, what fallback was used |
| **Operation exit** | Outcome, duration for slow operations |

### Minimum Coverage

Every public function in a gameplay-critical system should log at `Verbose` on entry and exit. Decision points that affect game state should log at `Log` or `Display` depending on importance.

```cpp
// Good: logs the decision path
void UInventoryComponent::TryAddItem(UItemData* Item)
{
    UE_LOG(LogInventory, Verbose, TEXT("TryAddItem: %s to %s"), *Item->GetName(), *GetOwner()->GetName());
    
    if (!CanAddItem(Item))
    {
        UE_LOG(LogInventory, Log, TEXT("TryAddItem: Rejected %s — inventory full or invalid"), *Item->GetName());
        return;
    }
    
    Items.Add(Item);
    UE_LOG(LogInventory, Log, TEXT("TryAddItem: Added %s. Count: %d/%d"), *Item->GetName(), Items.Num(), MaxSlots);
}

// Bad: no visibility into what happened
void UInventoryComponent::TryAddItem(UItemData* Item)
{
    if (CanAddItem(Item))
        Items.Add(Item);
}
```

### Don't Over-Log

Avoid logging inside tight loops or per-frame ticks at `Log` level — use `VeryVerbose` or add a throttle. Excessive logging impacts performance and buries important messages.

## Error Handling

- Try/catch or error returns around all I/O and external calls
- Never swallow errors silently — log with enough context to diagnose
- User-facing error messages must be helpful, not internal stack traces
- Distinguish expected errors (user-facing) from unexpected errors (logged internally)

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

## Severity Classification

- **CRITICAL**: None typical for this dimension
- **WARNING**: `LogTemp` in production, unguarded `AddOnScreenDebugMessage`, raw `assert()`, missing log category
- **INFO**: Log verbosity suggestions, stat tracking additions, `UE_LOGFMT` opportunities
