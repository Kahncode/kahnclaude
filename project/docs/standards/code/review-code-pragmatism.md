# Review Code: Pragmatism — Reference

## Pragmatism Criteria

"Keep It Simple" + "You Aren't Gonna Need It" — write the minimal necessary code. Prefer straightforward solutions over clever or speculative ones.

### Judgment Process

1. **Check Jira ticket** if linked in CL description — use requirements as scope
2. **Fall back to CL description** as scope definition
3. **If neither exists**, apply "minimal necessary code" heuristic — flag anything speculative without explicit justification

---

## Unnecessary Complexity [WARNING]

Logic that could be expressed more simply.

**Flags:**
- Nested conditionals that could be flattened with early returns
- Boolean logic that could be simplified (`if (x) return true; else return false;`)
- State machines for linear flows
- Multiple variables tracking the same state
- Redundant checks or double-validation

**Ask:** "Is there a simpler way to express this logic?"

**Fix pattern:** Extract guard clauses, flatten nesting, use direct returns.

---

## Over-Engineered Solutions [WARNING]

Design patterns or abstractions where direct code would suffice.

**Flags:**
- Factory for single type creation
- Strategy pattern with one strategy
- Observer pattern with one subscriber
- Wrapper classes that add no behavior
- Configuration systems for hardcoded values
- Base class with single concrete subclass
- Interface implemented by one type
- Generic `T` parameter used with single type

**Ask:** "Does this abstraction earn its complexity, or is it ceremony?"

**Fix pattern:** Inline the abstraction, use direct code.

---

## Speculative Parameters [WARNING]

Adding unused parameters "for future use" or "extensibility."

**Flags:**
- `bForce` flags never checked
- `Options` structs with one field
- `Context` parameters passed but ignored
- Default parameters that are never overridden

**Ask:** "Is this parameter used in the current change, or reserved for later?"

**Fix pattern:** Remove unused parameters. Add them when actually needed.

---

## Over-Generalization [WARNING]

Making something data-driven or configurable when hardcoded would suffice.

**Flags:**
- Config files for single-use values
- DataTables with one row
- String-based dispatch instead of direct calls
- Plugin architecture for fixed feature set

**Ask:** "Will this actually vary, or is configurability speculative?"

**Fix pattern:** Hardcode the value. Extract to config when a second use case appears.

---

## Clever Code [WARNING]

Code that prioritizes brevity or cleverness over readability.

**Flags:**
- One-liners that pack multiple operations (ternary chains, compound assignments)
- Bitwise tricks when arithmetic is clearer
- Regex when simple string operations work
- Implicit behavior relying on obscure language features
- "Golf" solutions optimizing character count

**Ask:** "Will a new team member understand this immediately?"

**Fix pattern:** Expand into explicit steps with clear variable names.

---

## Deep Nesting [WARNING]

Excessive indentation levels that obscure control flow.

**Flags:**
- More than 3 levels of indentation (excluding class/function scope)
- Nested loops with nested conditionals
- Try-catch wrapping try-catch
- Callback pyramids or nested lambdas

**Ask:** "Can I reduce nesting with early returns, extraction, or inversion?"

**Fix pattern:** 
- Guard clauses for early exit
- Extract inner blocks to named functions
- Invert conditions to reduce nesting

---

## Long Chains [INFO]

Method chains or fluent APIs that sacrifice debuggability.

**Flags:**
- More than 4 chained method calls
- Chains mixing queries and commands
- Chains where intermediate values might need inspection
- Builder patterns with 8+ chained calls

**Ask:** "Would breaking this chain improve debuggability?"

**Fix pattern:** Assign intermediate results to named variables.

---

## Defensive Overkill [INFO]

Validating invariants that cannot be violated by design.

**Flags:**
- Null checks after infallible construction
- Range checks on enum values
- Type checks after guaranteed cast
- Assertions on compiler-enforced constraints

**Ask:** "Can this condition actually fail in practice?"

**Fix pattern:** Remove checks that cannot fail. Add checks only at system boundaries.

---

## Premature Optimization [WARNING]

Complex algorithms or caching when simple implementation would suffice.

**Flags:**
- Object pools for rarely-allocated types
- Caching results computed once
- Spatial acceleration for small datasets
- Lock-free structures in single-threaded context

**Ask:** "Is there measured performance data, or is this speculative optimization?"

**Fix pattern:** Start simple. Optimize when profiling shows a bottleneck.

---

## UE5 Considerations

- **Blueprints as complexity indicator:** If C++ is too complex for Blueprint exposure, it may be too complex period.
- **Tick simplicity:** `Tick` functions should be scannable at a glance — complex tick logic should dispatch to named functions.
- **Macro soup:** Excessive UE macro nesting (UFUNCTION inside GENERATED_BODY workarounds) signals design issues.
- **Replication complexity:** Required by engine patterns — do not flag standard replication setup.

## When NOT to Flag

- Complexity required by UE5 engine patterns (e.g., replication setup)
- Performance-critical code where simplicity has measured cost
- Established idioms in the codebase documented in ARCHITECTURE.md
- Third-party API integration requiring specific patterns
- Abstraction required by existing architecture patterns
- Parameters matching established API conventions
- Optimization in documented hot paths
- Defensive checks at system boundaries (user input, network, external APIs)
- Code explicitly called out in task requirements
