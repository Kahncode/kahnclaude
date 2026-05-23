# Interface

Is this API well-designed for its consumers?

Think from the **consumer's perspective** (C++ caller, Blueprint user, API consumer).

## Parameter Design

Flag functions with >4 parameters. Group into an `F`-prefixed params struct:

```cpp
// Bad — too many params
void ApplyDamage(AActor* Target, float Amount, EDamageType Type,
    AActor* Instigator, AController* InstigatorCtrl, bool bIgnoreArmor);

// Good — params struct
USTRUCT(BlueprintType)
struct FDamageParams
{
    GENERATED_BODY()
    UPROPERTY() TObjectPtr<AActor> Target;
    UPROPERTY() float Amount;
    UPROPERTY() EDamageType Type;
    UPROPERTY() TObjectPtr<AActor> Instigator;
    UPROPERTY() bool bIgnoreArmor = false;
};

void ApplyDamage(FDamageParams const& Params);
```

## Access Specifier Tightness

Use the tightest specifier that works:

| Instead of | Prefer when |
|---|---|
| `EditAnywhere` | `EditDefaultsOnly` — only class defaults need editing |
| `EditAnywhere` | `VisibleAnywhere` — value set by C++, not editable |
| `BlueprintReadWrite` | `BlueprintReadOnly` — unless Blueprint actually writes |

## Blueprint Exposure

- All BP-exposed functions/properties must have `Category="..."`
- `BlueprintPure` only for const functions with no side effects
- `BlueprintNativeEvent` when C++ has a default; `BlueprintImplementableEvent` when it does not
- Missing `BlueprintCallable` on functions designers need is an under-exposure gap
- Internal implementation exposed to Blueprint is over-exposure

## UPARAM for Clarity

Use `UPARAM(DisplayName="...")` when auto-generated pin names are unclear:
```cpp
void GetHealthInfo(UPARAM(DisplayName="Current") float& OutCurrent,
                   UPARAM(DisplayName="Max") float& OutMax);
```

## Return Type Design

- Prefer `TOptional<T>` over sentinel/magic-number return values
- Use `TSubclassOf<T>` over raw `UClass*` for class references
- Use `TObjectPtr<T>` for UObject pointers in UPROPERTY headers
- Use `TSoftObjectPtr<T>` for asset references that support async loading

## DataTable and DataAsset Design

- `FTableRowBase` structs: prefer `FGameplayTag` or enums over raw `FString` IDs (type-safe, toolable)
- Use `TSoftObjectPtr` / `TSoftClassPtr` for asset references in data rows — hard references force synchronous loading
- `UPROPERTY(Config)` for environment/deployment settings that differ between machines
- DataTable for frequently-tuned tabular values (weapon stats, item prices)
- DataAsset (`UPrimaryDataAsset`) for complex structured data with nested assets
- Hardcoded values that designers need to tune → move to DataTable or DataAsset

## Delegate Event Quality

- Blueprint-visible events should use clear verb phrases: `OnHealthChanged` not `HealthUpdate`
- When C++ changes observable state, the corresponding delegate must be broadcast
- Delegate parameters visible in Blueprint should have meaningful types — flag raw indices or opaque integer handles

---

## Severity Classification

- **CRITICAL**: Blueprint-exposed property that can corrupt state
- **WARNING**: >4 parameters, overly permissive specifiers, missing `Category` on BP items, hardcoded designer-tunable values
- **INFO**: `UPARAM` suggestions, `DisplayName`/`ToolTip` additions, tighter access specifiers
