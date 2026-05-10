# Review Code: Style — Reference

Do not flag personal style preferences — only project/Epic standards.

**Critical rule**: Style must match the NEIGHBOR code style, not just global rules. If the surrounding file uses a consistent pattern, new code must follow that pattern even if it differs from the global standard. Flag only when new code breaks consistency with its immediate context.

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

## Review Guidelines

### What to IGNORE
- Correctness bugs (other dimension)
- Performance concerns (other dimension)
- Architecture decisions (other dimension)
- Pre-existing style violations not in the diff

### Severity Classification
- **CRITICAL**: None typical for style
- **WARNING**: Missing Epic prefix, STL containers in UE code, wrong include order, `.generated.h` not last
- **INFO**: East const suggestion, `DisplayName`/`ToolTip` suggestions, minor formatting
