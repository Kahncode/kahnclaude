# Review Code: Readability — Reference

## Magic Numbers and Strings

Unnamed constants must be replaced with named constants or config values:

```cpp
// Bad — magic number
if (Health < 25.f)
    PlayLowHealthEffect();

// Good — named constant
static float constexpr LowHealthThreshold = 25.f;
if (Health < LowHealthThreshold)
    PlayLowHealthEffect();
```

**WARNING** severity: hardcoded values that designers need to tune should be `UPROPERTY(EditDefaultsOnly)` or in a DataTable.

## Naming Quality

- Names should be descriptive and self-explanatory
- Variables and functions convey intent without needing a comment
- Avoid abbreviations unless universally understood (`HP` fine, `PlyrHlth` not)
- Boolean names read as predicates: `bIsAlive`, `bHasPermission`
- Out parameters prefixed with `Out`: `OutHitResult`

## Comments

- Comments explain **why**, not **what** — the code shows what
- Complex conditionals should have a comment explaining their overall purpose
- No stale comments — comments that contradict the code are actively harmful
- Public APIs should have brief `/** */` doc comments with `@param` and `@return`

## Complex Expressions

Compound boolean conditions should either:
- Be extracted into a well-named boolean variable
- Have a comment explaining their overall purpose

```cpp
// Bad — what does this mean?
if (bIsAlive && Health > 0.f && !bIsStunned && AbilitySystem && AbilitySystem->CanActivate())

// Good — named condition
bool const bCanAct = bIsAlive && Health > 0.f && !bIsStunned;
bool const bAbilityReady = AbilitySystem && AbilitySystem->CanActivate();
if (bCanAct && bAbilityReady)
```

---

## Review Guidelines

### What to IGNORE
- Correctness bugs (other dimension)
- Performance concerns (other dimension)
- Style conformance details like brace placement (style dimension)
- Pre-existing readability issues not in the diff

### Severity Classification
- **CRITICAL**: None typical for readability
- **WARNING**: Magic numbers, deep nesting (>4 levels), poor naming, stale comments
- **INFO**: Better naming alternatives, documentation suggestions, clarity improvements
