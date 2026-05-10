# Review Code: Architecture — Reference

## Architecture Criteria

### Code Organization

- Follow project rules in CLAUDE.md and ARCHITECTURE.md
- No circular dependencies between modules
- No dead code — no commented-out blocks, no unreachable code, no unused imports
- File size: no file over 300 lines — split if larger
- Function size: no function over 50 lines — extract helpers

### Module Structure (UE5)

- Headers in `Private/` should not be included by other modules
- Implementation files should not be in `Public/`
- Cross-module types need `MODULENAME_API` export macro
- Missing API macros on public-facing types cause linker errors
- Composition vs inheritance: flag deep project-level inheritance (3+ levels beyond engine base) — prefer Components or Interfaces

---

## Review Guidelines

### What to IGNORE
- Correctness bugs (other dimension)
- Naming and formatting (other dimensions)
- Performance unless it stems from architectural problems

### Severity Classification
- **CRITICAL**: Circular dependency that blocks compilation
- **WARNING**: File >300 lines, function >50 lines, dead code, SOLID violation, deep inheritance
- **INFO**: Composition opportunities, tighter encapsulation suggestions
