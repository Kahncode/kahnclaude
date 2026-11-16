# Debuggability

Is this code diagnosable in production?

## Log Categories

Every module/system should define its own log category. Avoid generic/temp loggers in production.

```python
# Example: Python logging
import logging
logger = logging.getLogger(__name__)
```

```typescript
// Example: TypeScript/Node
const logger = createLogger({ module: 'inventory' });
```

## Verbosity Levels

| Level | Use for |
|-------|---------|
| `Fatal/Critical` | Unrecoverable errors — crash or shutdown |
| `Error` | Serious failures — broken functionality |
| `Warning` | Unexpected but recoverable conditions |
| `Info` | Key operational events visible in production |
| `Debug` | Normal operational info — often stripped in prod |
| `Trace/Verbose` | Detailed diagnostics for debugging |

## Log Message Quality

Messages must include context: **what happened, which object, what values**.

```python
# Good
logger.warning(f"ApplyDamage: {self.name} received {damage:.1f} from {instigator.name}. Health: {self.health:.1f}")

# Bad
logger.info("damage applied")
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

Every public function in a critical system should log at debug/trace level on entry and exit. Decision points that affect application state should log at info/warning depending on importance.

```python
# Good: logs the decision path
def try_add_item(self, item):
    logger.debug(f"try_add_item: {item.name} to {self.owner.name}")
    
    if not self.can_add_item(item):
        logger.info(f"try_add_item: Rejected {item.name} — inventory full or invalid")
        return False
    
    self.items.append(item)
    logger.info(f"try_add_item: Added {item.name}. Count: {len(self.items)}/{self.max_slots}")
    return True

# Bad: no visibility into what happened
def try_add_item(self, item):
    if self.can_add_item(item):
        self.items.append(item)
```

### Don't Over-Log

Avoid logging inside tight loops or high-frequency operations at info level — use debug/trace or add throttling. Excessive logging impacts performance and buries important messages.

## Error Handling

- Try/catch or error returns around all I/O and external calls
- Never swallow errors silently — log with enough context to diagnose
- User-facing error messages must be helpful, not internal stack traces
- Distinguish expected errors (user-facing) from unexpected errors (logged internally)

## Debug Output in Production

Always guard debug output with environment/build checks:

```python
# Guard debug output
if settings.DEBUG:
    print(f"Debug: {diagnostic_info}")
```

```typescript
// Guard debug output
if (process.env.NODE_ENV !== 'production') {
  console.log('Debug:', diagnosticInfo);
}
```

## Assertions

| Type | When | Behavior |
|------|------|----------|
| `assert` | Programming error — invariant violation | Crashes in dev, may be stripped in prod |
| Soft assert | Unexpected but recoverable | Logs error, continues execution |
| Contract checks | API preconditions | Returns error/throws at boundary |

Use assertions for invariants that should never be violated. Don't use assertions for user input validation or expected error conditions.

## Performance Metrics

For performance-sensitive systems, add tracking:
- Operation timers (start/end timestamps)
- Counter metrics (requests, failures, cache hits)
- Distribution metrics (latency percentiles)

---

## Severity Classification

- **CRITICAL**: None typical for this dimension
- **WARNING**: Generic loggers in production, missing error context, swallowed exceptions, unguarded debug output
- **INFO**: Verbosity suggestions, metric tracking additions, structured logging opportunities
