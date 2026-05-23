# Architecture & Design

Does the solution fit the problem?

## Criteria

- **SOLID violations**
  - SRP: multiple reasons to change, "and" in function description
  - OCP: switch/if-else chains growing with new cases
  - LSP: subclass breaks base contract, requires type-checking
  - ISP: fat interfaces with stubbed methods
  - DIP: direct instantiation of concrete dependencies

- **Coupling/cohesion issues**
  - God classes (10+ public methods spanning different domains)
  - Mixed concerns in single class/function
  - Circular dependencies between modules

- **Anti-patterns**
  - Deep inheritance (>3 project-level classes beyond engine base)
  - Premature abstraction (Factory for single type, Strategy with one strategy)
  - Over-engineering for hypothetical future requirements

- **Size limits**
  - File >300 lines — split
  - Function >50 lines — extract helpers

## UE5 Considerations

- Prefer components over deep inheritance
- Use subsystems (`UGameInstanceSubsystem`, `UWorldSubsystem`) for singletons
- Use `UINTERFACE`/`IMyInterface` for polymorphism

## Interface Design

- **Parameters**: >4 params → use `F`-prefixed params struct
- **Access specifiers**: tightest that works (`EditDefaultsOnly` > `EditAnywhere`, `BlueprintReadOnly` > `BlueprintReadWrite`)
- **Blueprint exposure**: `Category` required on all BP items; `BlueprintPure` only for const/side-effect-free
- **Return types**: `TOptional<T>` over sentinels; `TObjectPtr<T>` for UObject pointers; `TSoftObjectPtr<T>` for async asset refs
- **Data**: DataTable for tabular tuning values; DataAsset for complex nested structures; soft refs for data rows
- **Delegates**: verb phrases (`OnHealthChanged` not `HealthUpdate`); broadcast when observable state changes

---

## Over-Engineering [WARNING]

**Flags:**
- Factory for single type creation
- Strategy pattern with one strategy
- Observer pattern with one subscriber
- Wrapper classes that add no behavior
- Base class with single concrete subclass
- Interface implemented by one type
- Generic `T` parameter used with single type

**Ask:** "Does this abstraction earn its complexity, or is it ceremony?"

## Speculative Parameters [WARNING]

**Flags:**
- `bForce` flags never checked
- `Options` structs with one field
- `Context` parameters passed but ignored
- Default parameters that are never overridden

**Fix:** Remove unused parameters. Add them when actually needed.

## Over-Generalization [WARNING]

**Flags:**
- Config files for single-use values
- DataTables with one row
- String-based dispatch instead of direct calls
- Plugin architecture for fixed feature set

**Ask:** "Will this actually vary, or is configurability speculative?"

---

## UE5 Init Ordering Race

**Problem**: During initialization, actors/components/subsystems may initialize in any order.

**Two-Phase Pattern**:
1. **Collect (BeginPlay)**: gather refs, register, but don't use
2. **Process**: use refs only after all actors have initialized (timer, delegate, or game state event)

**Red flags**:
- Accessing another actor's state in `BeginPlay` without null-check
- Assuming a subsystem has completed `Initialize()` during `BeginPlay`
- Using `TActorIterator` in `BeginPlay` (not all actors have begun play)
