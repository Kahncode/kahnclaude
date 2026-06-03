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
  - Deep inheritance (>3 levels beyond framework base)
  - Premature abstraction (Factory for single type, Strategy with one strategy)
  - Over-engineering for hypothetical future requirements

- **Size limits**
  - File >300 lines — split
  - Function >50 lines — extract helpers

## Design Principles

- Prefer composition over deep inheritance
- Use dependency injection for testability
- Interface-based design for polymorphism
- Single responsibility at every level (function, class, module)

## Interface Design

- **Parameters**: >4 params → use a params struct or builder pattern
- **Access modifiers**: tightest that works (private > protected > public)
- **Return types**: prefer `Optional<T>` or `Result<T, E>` over sentinels or magic values
- **Naming**: verb phrases for events/callbacks (`OnHealthChanged` not `HealthUpdate`)

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
- `force` flags never checked
- `Options` structs with one field
- `Context` parameters passed but ignored
- Default parameters that are never overridden

**Fix:** Remove unused parameters. Add them when actually needed.

## Over-Generalization [WARNING]

**Flags:**
- Config files for single-use values
- Data tables with one row
- String-based dispatch instead of direct calls
- Plugin architecture for fixed feature set

**Ask:** "Will this actually vary, or is configurability speculative?"

---

## Initialization Order Issues

**Problem**: During initialization, components/services may initialize in any order.

**Two-Phase Pattern**:
1. **Collect**: gather references, register callbacks, but don't use yet
2. **Process**: use references only after all dependencies have initialized

**Red flags**:
- Accessing another service's state during init without null-check
- Assuming a dependency has completed initialization during your init
- Iterating over collections that are still being populated
