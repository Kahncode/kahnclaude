"""Read the current project's `.claude/rules/project-vars.md` (```ini blocks of KEY=VALUE).

Lookup order for a name: real env var (non-empty) > project-vars.md. Values may reference
other vars as {{NAME}}; those expand recursively. Scripts import `get`; shells use the CLI:
    python -I -X utf8 project_vars.py --get EDITOR_PROCESS
    python -I -X utf8 project_vars.py --check <dir> [<dir> ...] [--template <file>]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

VARS_REL = Path(".claude") / "rules" / "project-vars.md"
PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
CHECK_SUFFIXES = {".md", ".py", ".ps1", ".bat", ".json", ".js", ".html", ".txt"}
# Names used to describe the syntax itself, and third-party skill folders, are not project vars.
SYNTAX_EXAMPLES = {"NAME", "VAR", "X"}
CHECK_SKIP_DIRS = {"__pycache__", "synced"}
_MISSING = object()


def find_vars_file(start: str | os.PathLike | None = None) -> Path | None:
    """$CLAUDE_PROJECT_DIR first, else walk up from `start` (default cwd)."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir and (Path(project_dir) / VARS_REL).is_file():
        return Path(project_dir) / VARS_REL
    here = Path(start or os.getcwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / VARS_REL).is_file():
            return folder / VARS_REL
    return None


def parse(text: str) -> dict[str, str]:
    """KEY=VALUE lines inside ```ini fences; `#`/`;` lines are comments."""
    values: dict[str, str] = {}
    in_ini = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_ini = line[3:].strip().lower() == "ini" if not in_ini else False
            continue
        if not in_ini or not line or line[0] in "#;" or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _expand(value: str, raw: dict[str, str], depth: int = 0) -> str:
    if depth > 10:
        raise ValueError(f"project-vars: {{{{...}}}} nesting too deep in {value!r}")
    def sub(match: re.Match) -> str:
        name = match.group(1)
        inner = os.environ.get(name) or raw.get(name)
        return match.group(0) if inner is None else _expand(inner, raw, depth + 1)
    return PLACEHOLDER.sub(sub, value)


def load(vars_file: Path | None = None) -> dict[str, str]:
    """All vars, env-overridden and expanded. Empty dict when no file is found."""
    vars_file = vars_file or find_vars_file()
    raw = parse(vars_file.read_text(encoding="utf-8")) if vars_file else {}
    merged = {k: os.environ.get(k) or v for k, v in raw.items()}
    return {k: _expand(v, merged) for k, v in merged.items()}


def get(name: str, default=_MISSING, vars_file: Path | None = None) -> str:
    """Value of `name`; raises KeyError naming the file to edit when absent and no default."""
    env_value = os.environ.get(name)
    values = load(vars_file)
    value = env_value or values.get(name)
    if value:
        return _expand(value, values)
    if default is not _MISSING:
        return default
    where = vars_file or find_vars_file() or "<project>/.claude/rules/project-vars.md (not found)"
    raise KeyError(f"{name} is not set: add it to {where} (template: ~/.claude/templates/unreal-project/project-vars.md)")


def used_placeholders(root: Path) -> dict[str, set[str]]:
    """{{NAME}} -> files using it, for every text file under `root`."""
    found: dict[str, set[str]] = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CHECK_SUFFIXES or CHECK_SKIP_DIRS & set(path.parts):
            continue
        for name in set(PLACEHOLDER.findall(path.read_text(encoding="utf-8", errors="replace"))) - SYNTAX_EXAMPLES:
            found.setdefault(name, set()).add(str(path.relative_to(root)))
    return found


def check(roots: list[Path], vars_files: list[Path]) -> int:
    """Print placeholders used under `roots` but missing from any of `vars_files`; exit code 1 if any."""
    used: dict[str, set[str]] = {}
    for root in roots:
        for name, files in used_placeholders(root).items():
            used.setdefault(name, set()).update(f"{root.name}/{f}" for f in files)
    status = 0
    for vars_file in vars_files:
        defined = set(parse(vars_file.read_text(encoding="utf-8")))
        missing = sorted(set(used) - defined)
        for name in missing:
            print(f"MISSING in {vars_file}: {name}  (used by {', '.join(sorted(used[name])[:3])})")
        status |= 1 if missing else 0
    print(f"{len(used)} placeholders used under {', '.join(map(str, roots))}; {'OK' if status == 0 else 'missing vars above'}")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--get", metavar="NAME")
    parser.add_argument("--default", help="value printed when NAME is unset (else exit 2)")
    parser.add_argument("--file", type=Path, help="vars file (default: find from $CLAUDE_PROJECT_DIR / cwd)")
    parser.add_argument("--dump", action="store_true", help="print every resolved var")
    parser.add_argument("--check", type=Path, nargs="+", metavar="DIR", help="list {{VAR}}s under the DIRs not defined in the vars file(s)")
    parser.add_argument("--template", type=Path, action="append", default=[], help="extra vars file for --check")
    args = parser.parse_args()
    if args.check:
        files = [f for f in [args.file or find_vars_file(), *args.template] if f]
        return check(args.check, files)
    if args.dump:
        for key, value in load(args.file).items():
            print(f"{key}={value}")
        return 0
    if args.get:
        try:
            print(get(args.get, args.default if args.default is not None else _MISSING, args.file))
            return 0
        except KeyError as err:
            print(err.args[0], file=sys.stderr)
            return 2
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
