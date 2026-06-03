# Interface Design

Is this API well-designed for its consumers?

Think from the **consumer's perspective** — the developer calling your code.

## Parameter Design

Flag functions with >4 parameters. Group into a params object or use builder pattern:

```python
# Bad — too many params
def apply_damage(target, amount, damage_type, instigator, controller, ignore_armor):
    pass

# Good — params object
@dataclass
class DamageParams:
    target: Actor
    amount: float
    damage_type: DamageType
    instigator: Actor
    ignore_armor: bool = False

def apply_damage(params: DamageParams):
    pass
```

```typescript
// Good — options object
interface DamageOptions {
  target: Actor;
  amount: number;
  damageType: DamageType;
  instigator: Actor;
  ignoreArmor?: boolean;
}

function applyDamage(options: DamageOptions): void { }
```

## Access Modifier Tightness

Use the tightest modifier that works:

| Instead of | Prefer when |
|---|---|
| `public` | `private` — no external callers |
| `public` | `protected` — only subclasses need access |
| mutable | readonly — value set once, not modified |

## API Exposure

- Public APIs need documentation (docstrings, JSDoc, etc.)
- Internal implementation should not be exposed publicly
- Consider whether consumers actually need each public method
- Missing public methods that consumers need is an under-exposure gap

## Return Type Design

- Prefer `Optional<T>` or `Result<T, E>` over sentinel/magic-number return values
- Use specific types over generic ones (`UserId` vs `string`)
- Avoid raw primitives when a value object is clearer

## Configuration vs Code

- Configuration for values that vary between environments
- Data files/tables for frequently-tuned values (game balance, feature flags)
- Hardcoded values that operators/designers need to tune → move to config

## Event/Callback Quality

- Events should use clear verb phrases: `onHealthChanged` not `healthUpdate`
- When state changes, fire the corresponding event
- Event parameters should have meaningful types — avoid raw indices or opaque handles

---

## Severity Classification

- **CRITICAL**: Public API that can corrupt state or cause security issues
- **WARNING**: >4 parameters, overly permissive access, missing documentation on public APIs
- **INFO**: Documentation improvements, naming suggestions, tighter access modifiers
