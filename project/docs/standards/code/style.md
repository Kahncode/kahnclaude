# Style

Does this code follow project and Epic conventions?

Do not flag personal style preferences — only project/Epic standards.

**Critical rule**: Style must match the NEIGHBOR code style, not just global rules. If the surrounding file uses a consistent pattern, new code must follow that pattern even if it differs from the global standard.

## Epic Naming Conventions

| Prefix | Applies to |
|--------|-----------|
| `T` | Template classes (`TArray`, `TMap`, `TSharedPtr`) |
| `U` | `UObject` subclasses |
| `A` | `AActor` subclasses |
| `S` | `SWidget` (Slate) subclasses |
| `I` | Abstract interface classes |
| `E` | Enums |
| `F` | Plain structs and most other classes |
| `b` | Boolean variables (`bIsAlive`, `bHasFired`) |

General: PascalCase for types, functions, properties. No `m_` or Hungarian beyond Epic prefixes. `Out` prefix for out-parameters. Macros: `ALL_CAPS_WITH_UNDERSCORES`.

## Naming Clarity

Names must communicate intent without requiring context lookup.

**Flags:**
- Single-letter variables outside loop indices
- Abbreviations that aren't universally known (`mgr`, `impl`, `ctx`)
- Generic names (`data`, `info`, `item`, `value`, `temp`)
- Names that don't match what the thing does

**Ask:** "Would a new team member understand this name without reading the implementation?"

## Comments

Comments should explain **why**, never **what** (the code shows what).

**Flags:**
- Stale comments that contradict the code
- Comments that restate the code (`// increment counter` above `counter++`)
- Commented-out code blocks (delete or explain why kept)
- Missing context on non-obvious workarounds

**Ask:** "Does this comment add information the code doesn't already convey?"

## Code Formatting

- **Tabs**, not spaces
- **Allman braces** — opening brace on its own line
- Space after `if`/`for`/`while`/`switch`, no space between function name and `(`
- No trailing whitespace, one blank line between methods

## East Const

Place `const` **after** the type:
```cpp
FVector const& Location = GetLocation();   // correct
float const Elapsed = 1.f;                 // correct
const FVector& Location = GetLocation();   // wrong
```

## Include Order

1. Module PCH (`MyGame.h`)
2. Own header (`MyComponent.h`)
3. Engine/plugin headers
4. Third-party (wrapped in `THIRD_PARTY_INCLUDES_START/END`)
5. `.generated.h` — **ALWAYS last** in owning header

Use `#pragma once` in all headers.

## Portable Types

| UE Alias | Instead of |
|----------|-----------|
| `int32`/`uint32` | `int`/`unsigned int` |
| `int8`/`uint8` | `char`/`unsigned char` |
| `TCHAR` | `wchar_t`/`char` |
| `nullptr` | `NULL` or `0` |

Wrap string literals in `TEXT()`.

## UE Containers (not STL)

| Use | Instead of |
|-----|-----------|
| `TArray<T>` | `std::vector` |
| `TMap<K,V>` | `std::unordered_map` |
| `TSet<T>` | `std::set` |
| `FString` | `std::string` |
| `TSharedPtr<T>` | `std::shared_ptr` |

**WARNING**: STL containers in UE code (`std::vector`, `std::map`, etc.)

## Modern C++ Rules

- Use `auto` only when the type is obvious from context or extremely verbose. Never `auto` for `UPROPERTY` members
- Prefer range-based `for` with `auto&` or `const auto&`
- Mark overrides with `override`; sealed classes/methods with `final`
- Use `= delete` and `= default` instead of empty or private implementations
- Prefer `TOptional<T>` over sentinel/magic-number return values

## Inclusive Terminology

| Avoid | Use instead |
|-------|------------|
| `whitelist` / `blacklist` | `allowlist` / `blocklist` |
| `master` / `slave` | `primary` / `secondary` |

Apply to: variable names, comments, log messages, UI strings, documentation, branch names.

## Copyright Notice

Every source file must begin with the copyright header as specified by the team or studio.

---

## Unnecessary Complexity [WARNING]

**Flags:**
- Nested conditionals that could be flattened with early returns
- Boolean logic that could be simplified (`if (x) return true; else return false;`)
- State machines for linear flows
- Multiple variables tracking the same state

**Fix:** Extract guard clauses, flatten nesting, use direct returns.

## Clever Code [WARNING]

**Flags:**
- One-liners that pack multiple operations (ternary chains, compound assignments)
- Bitwise tricks when arithmetic is clearer
- Regex when simple string operations work
- Implicit behavior relying on obscure language features

**Ask:** "Will a new team member understand this immediately?"

## Deep Nesting [WARNING]

**Flags:**
- More than 3 levels of indentation (excluding class/function scope)
- Nested loops with nested conditionals
- Callback pyramids or nested lambdas

**Fix:** Guard clauses for early exit, extract inner blocks to named functions.

## Long Chains [INFO]

**Flags:**
- More than 4 chained method calls
- Chains where intermediate values might need inspection

**Fix:** Assign intermediate results to named variables.

## Defensive Overkill [INFO]

Validating invariants that cannot be violated by design.

**Flags:**
- Null checks after infallible construction
- Range checks on enum values
- Type checks after guaranteed cast

**Ask:** "Can this condition actually fail in practice?"

**Fix:** Remove checks that cannot fail. Add checks only at system boundaries.

---

## Severity Classification

- **CRITICAL**: None typical for style
- **WARNING**: Missing Epic prefix, STL containers in UE code, wrong include order, `.generated.h` not last
- **INFO**: East const suggestion, `DisplayName`/`ToolTip` suggestions, minor formatting
