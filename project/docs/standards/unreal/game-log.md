# Game Log Reference

Maintained as part of the game-log skill.

---

## UE Log Format

Standard UE log line format:
```
[YYYY.MM.DD-HH.MM.SS:mmm][  0]LogCategory: VerbosityLevel: Message text
```

Example:
```
[2025.03.15-14.32.01:456][  0]LogCombat: Warning: ApplyDamage: Player1 received 50.0 damage from Enemy3. Health now 25.0
```

## Verbosity Levels

| Level | Use For | Survives Shipping? |
|-------|---------|-------------------|
| `Fatal` | Unrecoverable errors -- crashes immediately | Yes |
| `Error` | Serious failures that corrupt state or break functionality | Yes |
| `Warning` | Unexpected but recoverable conditions | Yes |
| `Display` | Key game events (use sparingly) | Yes |
| `Log` | Normal operational info | No (stripped) |
| `Verbose` | Detailed diagnostic info | No |
| `VeryVerbose` | Extremely detailed trace-level | No |

## Log Categories

Each module or system defines its own category:

```cpp
// Header
DECLARE_LOG_CATEGORY_EXTERN(LogMySystem, Log, All);

// Source
DEFINE_LOG_CATEGORY(LogMySystem);

// File-local only
DEFINE_LOG_CATEGORY_STATIC(LogMySystem, Log, All);
```

**Rule**: Never use `LogTemp` in production code. One category per major system.

### Finding Categories in Source

```bash
# Find category declarations
grep -r "DECLARE_LOG_CATEGORY_EXTERN" Source/ --include="*.h"
grep -r "DEFINE_LOG_CATEGORY" Source/ --include="*.cpp"
```

### Finding Log Callsites

```bash
# Find where a specific message is logged
grep -r "ApplyDamage" Source/ --include="*.cpp" --include="*.h"

# Find all logs for a category
grep -r "UE_LOG(LogCombat" Source/ --include="*.cpp"
```

## Common Error Patterns in Logs

| Pattern | Meaning | Investigation |
|---------|---------|---------------|
| `Ensure condition failed` | `ensure()` fired -- unexpected but recovered | Check callstack, find the ensure in source |
| `check failed` | `check()` fired -- programming error, will crash | Find the check macro in source |
| `Access violation` | Null pointer dereference | Check callstack for the offending line |
| `Package not found` | Missing asset reference | Verify asset exists at the referenced path |
| `Failed to load` | Asset load error | Check asset path, cooking status |
| `Net driver` | Network error | Check connection, port, firewall |
| `LogSlate: Warning` | UI layout issue | Check widget hierarchy |
| `LogLinker: Warning: Asset not found` | Broken asset reference | Fix or remove the stale reference |

## Crash Log Investigation

Crash logs are located in:
```
$KC_PROJECT_ROOT/Saved/Crashes/<CrashID>/
```

Key files:
- `CrashContext.runtime-xml` -- crash metadata, callstack, system info
- `<ProjectName>.log` -- full log up to the crash point
- `Diagnostics.txt` -- minidump analysis (if available)

## Enabling Verbose Logging at Runtime

Console command:
```
log LogCombat Verbose
log LogNet VeryVerbose
```

In `DefaultEngine.ini`:
```ini
[Core.Log]
LogCombat=Verbose
LogMySystem=VeryVerbose
```

## Assertions Reference

| Macro | Behavior |
|-------|----------|
| `check(expr)` | Crashes in Dev/Debug, stripped in Shipping |
| `ensure(expr)` | Logs callstack once, returns false |
| `ensureMsgf(expr, TEXT("..."))` | Logs message + callstack |
| `verify(expr)` | Crashes in Dev, evaluates in Shipping |
| `checkNoEntry()` | Marks unreachable code paths |

## Structured Logging (UE 5.2+)

```cpp
#include "Logging/StructuredLog.h"

UE_LOGFMT(LogCombat, Warning, "Actor {Name} took {Damage} damage",
    ("Name", GetName()), ("Damage", DamageAmount));
```

Use Unreal Insights to filter structured log entries by named fields.

## Noise Categories (Skip by Default)

These categories produce high-volume init-time output -- skip unless user asks:
- `LogInit`, `LogConfig`, `LogPakFile`, `LogShaderCompilers`
- `LogLinker` (asset loading -- useful for missing asset investigation)
- `LogStreaming`, `LogDerivedDataCache`
