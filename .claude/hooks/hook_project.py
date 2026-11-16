"""Shared by the user-level hooks: project vars and Unreal layout, never raising.

Hooks run in every project; a missing var or vars file means '' (the hook then allows).
"""
import glob as globlib
import os
import sys
from pathlib import Path

# project_vars lives in ~/.claude/scripts/lib (user install) or <project>/.claude/scripts/lib (project install)
for _lib in (Path.home() / ".claude" / "scripts" / "lib",
             Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".claude" / "scripts" / "lib"):
    if _lib.is_dir():
        sys.path.insert(0, str(_lib))


def project_var(name: str, project_dir: str) -> str:
    """Env var, else the project's own .claude/rules/project-vars.md; '' when unset or unreadable."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        from project_vars import VARS_REL, get
        vars_file = Path(project_dir) / VARS_REL
        return get(name, "", vars_file) if project_dir and vars_file.is_file() else ""
    except Exception as err:  # a hook never crashes on project vars
        print(f"{Path(sys.argv[0]).name}: project var {name} unreadable: {err}", file=sys.stderr)
        return ""


def find_uproject(project_dir: str) -> str:
    """The *.uproject in the project folder or one level below, else UE_PROJECT ('' = not Unreal)."""
    if project_dir:
        for pattern in ("*.uproject", "*/*.uproject"):
            found = globlib.glob(os.path.join(globlib.escape(project_dir), pattern))
            if found:
                return found[0]
    return project_var("UE_PROJECT", project_dir)


def uproject_folder(project_dir: str, uproject: str) -> str:
    """Folder of the .uproject relative to the project ('' = the project root), e.g. `MyGame/`."""
    try:
        rel = os.path.relpath(os.path.dirname(uproject), project_dir) if project_dir and uproject else ""
    except ValueError:
        rel = ""
    if not rel or rel.startswith(".."):
        rel = project_var("UE_PROJECT_NAME", project_dir) or "<Project>"
    return "" if rel == "." else rel.replace("\\", "/") + "/"


def layout_hint(project_dir: str, uproject: str, folders: tuple[str, ...]) -> str:
    """`<Project>/Source, <Project>/Config, Engine/Source/<Area>` from the real layout."""
    prefix = uproject_folder(project_dir, uproject)
    parts = [prefix + folder for folder in folders]
    if project_dir and os.path.isdir(os.path.join(project_dir, "Engine")):
        parts.append("Engine/Source/<Area>")
    return ", ".join(parts)
