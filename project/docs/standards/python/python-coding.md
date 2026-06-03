# Python Coding Standards — Reference

## Language & Types

- Target **Python 3.12+**. Use `match`, `TypeVarTuple`, `@override`, `Self`, `ExceptionGroup`
- **Full type annotations** on all function parameters, return types, and class attributes
- **Exhaustive container types**: `list[tuple[SomeType, float]]` not `list[tuple]`; `dict[str, int]` not `dict`
- Use `Protocol` for structural subtyping, `TypedDict` for typed dicts, `ParamSpec` for decorator typing, `TypeGuard` for type narrowing

## Data Modeling

- Prefer `dataclasses` or `pydantic` over raw `dict` for structured data
- Never use `**kwargs` in public APIs — define explicit parameters
- No mutable default arguments (`def f(items=[])` — use `None` + conditional)

## Stdlib Preferences

| Prefer | Over | Why |
|--------|------|-----|
| `pathlib.Path` | `os.path` | Object-oriented, cross-platform |
| `structlog` / `logging` | `print()` | Structured, filterable |
| `tomllib` | Third-party TOML | Stdlib in 3.11+ |
| `dataclasses` | Raw `dict` | Type-safe, self-documenting |

## Project Architecture

- `src/` layout with `pyproject.toml`. Pin dependencies with `uv`/`Poetry`/`pip-tools`
- Explicit `__init__.py` exports, avoid circular imports
- `pydantic-settings` or env vars for configuration — no hardcoded config values

## Error Handling

- All I/O in `try`/`except` with meaningful error messages including context
- Distinguish expected errors (return to caller) from unexpected errors (log and raise)
- Never swallow exceptions silently (`except: pass`)

## Docstrings

Google-style on public APIs with `Args:`, `Returns:`, `Raises:` sections when non-obvious.

## Testing

- **pytest** with `pytest-asyncio`, `pytest-cov`, `hypothesis` for property-based testing
- Fixtures, `parametrize`, `conftest.py` for shared setup
- Mock at boundaries, not internals
- Naming: `test_<function>_<scenario>_<expected>`

## Async & Concurrency

- `asyncio` for standard async I/O, `anyio` for library-agnostic code
- Structured concurrency with task groups
- `async I/O` vs `threading` vs `multiprocessing` — choose based on workload (I/O-bound vs CPU-bound)

## Memory & Performance

- `__slots__` on data-heavy classes, weak references for caches
- Generators and `memoryview` for large data streams
- Profile with `cProfile` (function-level) and `line_profiler` (line-level)

## Hooks (KahnClaude-specific)

- Use only Python stdlib (no external dependencies)
- Type hints on all functions
- Exit codes: `0` = allow, `2` = block with message, `1` = warn
- Print blocking reasons to `stderr` when exiting with code 2
