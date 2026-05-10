# Review Code: UE Best Practice — Reference

## UE5 CRITICAL Patterns

- **Raw UObject pointer without `UPROPERTY()`** — GC will collect the object, causing a crash
- **Replicated property without `DOREPLIFETIME`** — property will not replicate, causing desync
- **Server RPC without `WithValidation`** — cheat vector, clients can send arbitrary data
- **Unchecked `Cast<T>()` dereference** — nullptr crash if cast fails
- **Missing `GENERATED_BODY()`** — reflection and GC break silently
- **Blueprint-exposed property that can corrupt state** — write access to internal state
- **Hard reference to large asset** — forces synchronous load, hitches or OOM

## UObject Lifecycle

- Never `new`/`delete` UObjects — use `NewObject<T>()` / GC
- `CreateDefaultSubobject<T>()` in constructors ONLY; `NewObject<T>()` at runtime
- Never store raw `UObject*` without `UPROPERTY()` — GC will collect it
- Use `TWeakObjectPtr<T>` for non-owning references
- Use `TObjectPtr<T>` for UPROPERTY UObject pointers in headers (UE5 convention)

## Super:: Calls

These overrides almost always require `Super::`:
- `BeginPlay`, `EndPlay`, `Tick`
- `GetLifetimeReplicatedProps`
- `SetupPlayerInputComponent`
- `PostInitializeComponents`

Missing `Super::` causes: components not initializing, replication not registering, input not binding.

## Blueprint Exposure Rules

- All BP-exposed items must have `Category="..."`
- Choose tightest access: `EditDefaultsOnly` > `EditAnywhere`, `BlueprintReadOnly` > `BlueprintReadWrite`
- `BlueprintNativeEvent` when C++ has a default; `BlueprintImplementableEvent` when it does not
- Dynamic multicast delegates need `UPROPERTY(BlueprintAssignable)`

## UE5 WARNING Patterns

- STL containers in UE code (`std::vector`, `std::map`) — use `TArray`, `TMap`, `TSet`
- Missing Epic naming prefixes (F/U/A/E/I/T/S/b)
- `LogTemp` in production code
- Tick abuse (>20 lines, heavy logic in Tick)
- `TActorIterator`/`GetAllActorsOfClass` in hot paths
- `AddOnScreenDebugMessage` without `#if !UE_BUILD_SHIPPING`
- Raw `assert()` instead of UE assertion macros
- Hardcoded values that designers need to tune

## Architecture Patterns

- **Composition over inheritance**: prefer components over deep project-level inheritance
- **Subsystems over singletons**: `UGameInstanceSubsystem`, `UWorldSubsystem`, `ULocalPlayerSubsystem`
- **Interfaces for polymorphism**: `UINTERFACE`/`IMyInterface` over forced base class
- **Template wrappers**: `TSubclassOf<T>`, `TObjectPtr<T>`, `TSoftObjectPtr<T>`

## Gameplay Ability System (GAS)

- One `UAbilitySystemComponent` per pawn (or `APlayerState` for persistence across respawns)
- Attribute Sets: derive from `UAttributeSet`, use `ATTRIBUTE_ACCESSORS` macro for getter/setter boilerplate
- Gameplay Effects for stat modifications — never modify attributes directly in code
- Gameplay Tags for state management — define in `DefaultGameplayTags.ini` or a DataTable
- Abilities derive from `UGameplayAbility` — keep them focused on one action

## Delegate Patterns

| Macro | Use when |
|-------|----------|
| `DECLARE_DELEGATE` | Single-binding, C++ only |
| `DECLARE_MULTICAST_DELEGATE` | Multiple bindings, C++ only |
| `DECLARE_DYNAMIC_DELEGATE` | Single-binding, Blueprint-compatible |
| `DECLARE_DYNAMIC_MULTICAST_DELEGATE` | Multiple bindings, Blueprint-compatible (most common for events) |

- Prefer `AddUObject` over `AddRaw` — auto-unbinds on destruction
- Never bind lambdas that capture `this` on UObjects without ensuring the object outlives the delegate
- Use `RemoveAll(this)` or `Clear()` in `EndPlay` to prevent dangling callbacks

## Deprecation

Use `UE_DEPRECATED(5.x, "Use NewFunction() instead.")` on deprecated symbols. Deprecated symbols must compile cleanly. Remove no sooner than one major version after deprecation.

---

## Review Guidelines

### What to IGNORE
- General correctness not related to UE5 patterns (other dimension)
- Style details like braces and naming (other dimension)
- Performance unless it is a UE5-specific anti-pattern

### Severity Classification
- **CRITICAL**: GC hazard, missing DOREPLIFETIME, missing GENERATED_BODY, unchecked Cast, Server RPC without WithValidation, hard ref to large asset
- **WARNING**: Missing Super::, missing Category, Tick abuse, STL containers, LogTemp, overly permissive specifiers, hardcoded tunable values
- **INFO**: Container choice, Reserve() opportunities, DisplayName/ToolTip, soft reference opportunities
