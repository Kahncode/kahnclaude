# Blueprint Asset Review — Reference

## Review Philosophy

Apply the same principles as code review: be constructive, cite specific assets and properties, suggest concrete fixes, and explain **why** something is a problem.

## Severity Classification

| Level | Meaning |
|-------|---------|
| **CRITICAL** | Will cause runtime failures, data loss, or incorrect gameplay behavior |
| **WARNING** | Suboptimal design that increases maintenance cost or fragility |
| **INFO** | Improvement suggestion — not blocking |

## Review Dimensions

### 1. Exposure Design

- Are properties appropriately exposed to Blueprint? (not over-exposed internals, not under-exposed designer-facing values)
- Are there properties that should be `BlueprintReadOnly` but are `BlueprintReadWrite`?
- Are internal implementation details leaking through to Blueprint?
- Do exposed properties have sensible defaults for designers who don't know the C++ side?

### 2. Specifier Quality

- Do Blueprint-exposed properties have proper `Category` organization?
- Do non-obvious names have `DisplayName` and `ToolTip` metadata?
- Are output parameters using `UPARAM(DisplayName="...")`?
- Is the tightest access specifier being used? (`EditDefaultsOnly` vs `EditAnywhere`, `BlueprintReadOnly` vs `BlueprintReadWrite`)

### 3. Native vs Blueprint Split

- Is performance-critical logic in C++ and iteration/customization in Blueprint?
- Are `BlueprintNativeEvent` used where C++ defaults make sense?
- Are `BlueprintImplementableEvent` used only where C++ has no meaningful default?
- Are interfaces used for polymorphic Blueprint behavior instead of deep inheritance?
- Is the Blueprint graph complexity reasonable, or should logic move to C++?

### 4. DataTable / DataAsset Design

- Do row structs use `FGameplayTag` or enums instead of raw `FString` IDs?
- Are asset references using `TSoftObjectPtr`/`TSoftClassPtr` instead of hard references?
- Is the right data container being used? (Config vs DataTable vs DataAsset)
- Are hardcoded values that designers need to tune moved to data?
- Do DataTable rows have all required fields populated (no empty/zero defaults that look accidental)?

### 5. Delegate and Event Architecture

- Are multicast delegates marked `BlueprintAssignable` where Blueprint needs to bind?
- Do event names use clear verb phrases (`OnHealthChanged`, not `HealthUpdate`)?
- When C++ changes observable state, is the corresponding delegate broadcast?
- Do delegate parameters use meaningful types (not raw indices or opaque handles)?

### 6. Property Value Sanity

- Are default values sensible for the asset's purpose?
- Are there placeholder or debug values left in production assets? (e.g., `999`, `TODO`, test names)
- Are numeric values within expected ranges for gameplay?
- Are soft references pointing to valid asset paths?
- Do boolean flags have consistent default states across similar assets?

## Output Format

For each finding:
```
[CRITICAL | WARNING | INFO]

Asset: /Game/Path/To/Asset
Property: property_name (current value: X)
Issue: [What's wrong]
Why: [Gameplay or maintenance consequence]
Fix: [Specific change — new value or design recommendation]
```

End with: `Summary: X critical, Y warnings, Z info items.`

If no issues: `"No issues found."`
