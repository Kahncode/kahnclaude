# Review Code: SOLID — Reference

## SOLID Criteria

### Single Responsibility Principle (SRP) [WARNING]

A class or function should have only one reason to change.

**Flags:**
- Classes handling multiple unrelated concerns (e.g., UI + persistence + validation)
- Functions with "and" in their natural description ("loads data and formats it and sends it")
- God classes with 10+ public methods spanning different domains
- Functions taking boolean flags that switch behavior entirely

**Ask:** "If requirement X changes, does this class/function need to change for unrelated reason Y?"

### Open/Closed Principle (OCP) [WARNING]

Software entities should be open for extension but closed for modification.

**Flags:**
- Adding new cases to switch/if-else chains instead of using polymorphism
- Modifying base class to accommodate new subclass behavior
- Core classes with `// Added for FeatureX` scattered throughout
- Functions growing parameter lists to handle new variations

**Ask:** "Can I add new behavior without modifying existing code?"

### Liskov Substitution Principle (LSP) [WARNING]

Subclasses must be substitutable for their base classes without altering correctness.

**Flags:**
- Subclass methods throwing `NotImplementedException` or similar
- Overrides that ignore or violate base class contracts
- Subclasses that require type-checking before use (`if (is SubType)`)
- Derived classes with stricter preconditions or weaker postconditions

**Ask:** "Can I use this subclass anywhere the base class is expected without surprises?"

### Interface Segregation Principle (ISP) [WARNING]

Clients should not be forced to depend on interfaces they do not use.

**Flags:**
- Interfaces with 10+ methods where implementers stub most of them
- Classes implementing interfaces but leaving methods empty or throwing
- "Kitchen sink" interfaces covering unrelated capabilities
- Single interface where 2-3 focused interfaces would serve different clients

**Ask:** "Do all implementers of this interface actually need all these methods?"

### Dependency Inversion Principle (DIP) [WARNING]

High-level modules should not depend on low-level modules; both should depend on abstractions.

**Flags:**
- Direct instantiation of concrete dependencies (`new ConcreteService()`)
- High-level policy classes importing low-level implementation details
- Hard-coded dependencies on specific database, network, or file implementations
- Missing constructor injection or interface parameters

**Ask:** "Can I swap this dependency without modifying this class?"

## UE5 Considerations

- **Components over inheritance:** UE5 favors composition via `UActorComponent`. Flag deep inheritance hierarchies (3+ project-level concrete classes).
- **Subsystems:** Use `UGameInstanceSubsystem`, `UWorldSubsystem` for DIP-compliant singletons.
- **Interfaces:** `UINTERFACE` / `IMyInterface` for ISP-compliant polymorphism.
- **Delegates:** Prefer delegates/events over direct coupling for OCP compliance.

## When NOT to Flag

- UE5 engine patterns that intentionally violate SOLID for performance (e.g., monolithic `Tick`)
- Small utility classes where splitting would be over-engineering
- Established project patterns documented in CLAUDE.md or ARCHITECTURE.md
- Performance-critical code where abstraction overhead is measured and unacceptable
