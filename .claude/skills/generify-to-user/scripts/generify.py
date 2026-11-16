"""Stage, check and install a project -> user-level migration.

Work dir layout (one per run, under {{TEMP_BASE}}\\generify-<slug>\\):
    stage/user/<rel>     -> installs to ~/.claude/<rel>
    stage/project/<rel>  -> installs to <PROJECT_ROOT>/<rel>
    manifest.json        -> moved sources + hash of every file copied in for editing
Subcommands:
    stage   --work W [--keep-source] SRC=DEST ...   copy project items into stage/user/DEST (SRC: under PROJECT_ROOT
            or absolute); --keep-source for a SPLIT: also stages SRC as its project half and never lists it for removal
    edit    --work W FILE ...       copy an existing project or ~/.claude file into the stage to edit it
    check   --work W [--extra a,b]  leak / vars / syntax / KC_ / cache / pronoun checks on stage/user
    install --work W [--dry]        copy the stage into place; refuses files changed since they were staged
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

USER = Path.home() / ".claude"
sys.path.insert(0, str(USER / "scripts" / "lib"))
from project_vars import check as vars_check, find_vars_file, load  # noqa: E402

SKIP_DIRS = {"__pycache__", "evals"}
TEMPLATE = USER / "templates" / "unreal-project" / "project-vars.md"
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".bat", ".json", ".js", ".html", ".txt", ".ini", ".xml"}
LEAK_VARS = ["UE_PROJECT_NAME", "GAME_NAME", "JIRA_PROJECT_KEY", "CONFLUENCE_SPACE_KEY", "P4USER", "P4CLIENT",
             "P4CLIENT_DEVTOOLS", "JIRA_CLOUD_ID", "CONFLUENCE_SPACE_ID", "CONFLUENCE_ROOT_PAGE_ID",
             "DISCORD_GUILD_ID", "SLACK_ESCALATE_GROUP_ID", "ADMIN_PANEL_CONTACT", "GENERIFY_LEAK_TERMS"]
# Generic service words in hostnames (horde.<studio>.<tld>) that must not count as leaks.
HOST_WORDS = {"www", "wiki", "api", "ap", "app", "swarm", "horde", "jira", "confluence", "atlassian", "github",
              "gitlab", "sentry", "slack", "perforce", "p4", "dev", "docs"}
# Per-project memory legitimately names the project; it is staged but not leak-checked.
NO_LEAK_CHECK = ("projects",)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def project_root() -> Path:
    vars_file = find_vars_file()
    if not vars_file:
        raise SystemExit("No .claude/rules/project-vars.md found: run from the project root.")
    return Path(load(vars_file).get("PROJECT_ROOT") or vars_file.parents[2])


def manifest(work: Path) -> dict:
    path = work / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"moves": [], "originals": {}}


def save_manifest(work: Path, data: dict) -> None:
    (work / "manifest.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def stage_target(path: Path, root: Path) -> Path:
    """Where an existing file lives inside the stage (user tree or project tree)."""
    path = path.resolve()
    if path.is_relative_to(USER):
        return Path("user") / path.relative_to(USER)
    if path.is_relative_to(root):
        return Path("project") / path.relative_to(root)
    raise SystemExit(f"{path} is neither under {USER} nor under {root}")


def copy_item(src: Path, dst: Path, originals: dict, dest_real: Path) -> list[str]:
    """Copy a file or folder, skipping caches/evals/workspaces; return skipped fixture folders."""
    skipped = []
    files = [src] if src.is_file() else [p for p in src.rglob("*") if p.is_file()]
    for file in files:
        rel = file.relative_to(src) if src.is_dir() else Path(file.name)
        parts = set(rel.parts[:-1])
        if parts & SKIP_DIRS or any(p.endswith("-workspace") for p in parts):
            if "evals" in parts:
                skipped.append(str(src / rel.parts[0]))
            continue
        target = dst / rel if src.is_dir() else dst
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        real = (dest_real / rel if src.is_dir() else dest_real).resolve()
        originals[str(real)] = sha(real)
    return sorted(set(skipped))


def cmd_stage(work: Path, pairs: list[str], keep_source: bool) -> int:
    """keep_source (a SPLIT): the source stays in the project and is also staged as an edit copy for its project half."""
    root, data = project_root(), manifest(work)
    for pair in pairs:
        src_s, _, dest_s = pair.partition("=")
        src = Path(src_s) if Path(src_s).is_absolute() else root / src_s
        if not src.exists() or not dest_s:
            raise SystemExit(f"bad pair {pair!r}: need an existing SRC and a DEST under ~/.claude")
        clash = (USER / dest_s).is_file() and src.is_file()
        if clash:
            # Merge: start from the existing user-level file; the project file is input only, never installed.
            skipped = copy_item(USER / dest_s, work / "stage" / "user" / dest_s, data["originals"], USER / dest_s)
            incoming = work / "incoming" / dest_s
            incoming.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, incoming)
            print(f"  merge input: {incoming}")
        else:
            skipped = copy_item(src, work / "stage" / "user" / dest_s, data["originals"], USER / dest_s)
        if keep_source:
            copy_item(src, work / "stage" / stage_target(src, root), data["originals"], src)
        data["moves"].append({"src": str(src), "dest": str(USER / dest_s), "keep": keep_source})
        kept = "  (SPLIT: project half staged as an edit copy; the source stays)" if keep_source else ""
        print(f"staged {src} -> ~/.claude/{dest_s}{'  (EXISTS at user level: staged that file; merge the generic lines into it)' if clash else ''}{kept}")
        for folder in skipped:
            print(f"  fixtures left in the project (not staged): {folder}")
    save_manifest(work, data)
    return 0


def cmd_edit(work: Path, files: list[str]) -> int:
    root, data = project_root(), manifest(work)
    for name in files:
        path = Path(name) if Path(name).is_absolute() else root / name
        target = work / "stage" / stage_target(path, root)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            shutil.copy2(path, target)
        data["originals"][str(path.resolve())] = sha(path)  # '' = new file: install refuses if it appears meanwhile
        print(f"edit copy: {target}")
    save_manifest(work, data)
    return 0


def leak_terms(extra: list[str]) -> list[str]:
    values = load()
    terms = [v for name in LEAK_VARS for v in re.split(r"[,;]", values.get(name, "")) if v]
    terms += values.get("ADMIN_PANEL_CONTACT", "").split()
    for name, value in values.items():
        if name.endswith("_URL") or name == "P4PORT":
            host = re.sub(r"^\w+://|^ssl:", "", value).split("/")[0].split(":")[0]
            terms += [label for label in host.split(".")[:-1] if label.lower() not in HOST_WORDS and "<" not in label]
    root = values.get("PROJECT_ROOT", "")
    terms += [root, root.replace("\\", "/")] if root else []
    city = values.get("STUDIO_TZ", "").rpartition("/")[2]
    terms += [city, values.get("P4_DEPOT_ROOT", "").strip("/")] + extra
    return sorted({t.strip() for t in terms if len(t.strip()) >= 3}, key=str.lower)


def text_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES]


def unchanged_lines(work: Path) -> dict[Path, set[str]]:
    """Edit copies of existing user-level files: their original lines are old content, not new leaks."""
    originals, top = manifest(work)["originals"], work / "stage" / "user"
    result = {}
    for staged in (p for p in top.rglob("*") if p.is_file()):
        real = USER / staged.relative_to(top)
        if originals.get(str(real.resolve())) and real.is_file():
            result[staged] = set(real.read_text(encoding="utf-8", errors="replace").splitlines())
    return result


def scan(files: list[Path], base: Path, pattern: re.Pattern, label: str, old: dict[Path, set[str]]) -> int:
    hits = 0
    for path in files:
        for no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pattern.search(line) and line not in old.get(path, ()):
                hits += 1
                print(f"{label} {path.relative_to(base)}:{no}: {line.strip()[:160]}")
    return hits


def syntax_errors(files: list[Path]) -> int:
    bad = 0
    for path in files:
        if path.suffix == ".py":
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as err:
                bad += 1
                print(f"SYNTAX {path}: {err}")
        elif path.suffix == ".ps1":
            ps = ("$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$null,[ref]$e);"
                  "if($e){$e|%{$_.ToString()};exit 1}")
            run = subprocess.run(["powershell", "-NoProfile", "-Command", ps, str(path)], capture_output=True, text=True)
            if run.returncode:
                bad += 1
                print(f"SYNTAX {path}: {run.stdout.strip()[:300]}")
    return bad


def cmd_check(work: Path, extra: list[str]) -> int:
    user_tree = work / "stage" / "user"
    files = [f for f in text_files(user_tree) if f.relative_to(user_tree).parts[0] not in NO_LEAK_CHECK]
    terms, old = leak_terms(extra), unchanged_lines(work)
    print(f"leak terms ({len(terms)}): {', '.join(terms)}  (edit copies: only changed lines are checked)")
    issues = scan(files, user_tree, re.compile("|".join(map(re.escape, terms)), re.I), "LEAK", old) if terms else 0
    issues += scan(files, user_tree, re.compile(r"\bKC_|\bKC\b"), "KC_PREFIX", old)
    issues += scan([f for f in files if f.suffix == ".md"], user_tree, re.compile(r"\b(she|her|hers|he|him|his)\b", re.I), "PRONOUN", old)
    issues += syntax_errors(files)
    caches = [str(p) for p in user_tree.rglob("__pycache__")]
    issues += len(caches)
    for cache in caches:
        print(f"CACHE {cache}")
    vars_files = [f for f in (find_vars_file(), TEMPLATE) if f]
    staged_vars = [work / "stage" / stage_target(f, project_root()) for f in vars_files]
    vars_files = [s if s.is_file() else f for s, f in zip(staged_vars, vars_files)]
    issues += vars_check([user_tree], vars_files) if user_tree.is_dir() else 0
    print(f"{'CLEAN' if issues == 0 else f'{issues} issue(s)'}: {len(files)} staged user-level files")
    return 1 if issues else 0


def install_plan(work: Path) -> list[tuple[Path, Path]]:
    root = project_root()
    pairs = []
    for tree, base in (("user", USER), ("project", root)):
        top = work / "stage" / tree
        pairs += [(p, base / p.relative_to(top)) for p in top.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    return pairs


def cmd_install(work: Path, dry: bool) -> int:
    originals = manifest(work)["originals"]
    plan = install_plan(work)
    conflicts = []
    for _, dest in plan:
        known = originals.get(str(dest.resolve()))
        if dest.exists() and (known is None or known != sha(dest)):
            conflicts.append(dest)
    for dest in conflicts:
        print(f"CONFLICT {dest}: exists and was not staged, or changed since it was staged")
    if conflicts or dry:
        for src, dest in plan:
            print(f"{'new ' if not dest.exists() else 'over'} {dest}")
        removals = [m["src"] for m in manifest(work)["moves"] if not m.get("keep")]
        print(f"{len(plan)} files, {len(conflicts)} conflicts; nothing copied. Would remove: {', '.join(removals) or 'none'}")
        return 1 if conflicts else 0
    for src, dest in plan:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    removals = [m["src"] for m in manifest(work)["moves"] if not m.get("keep")]
    print(f"installed {len(plan)} files. Sources to remove now (through the project's Claude repo): {len(removals) or 'none'}")
    for src in removals:
        print(f"  {src}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["stage", "edit", "check", "install"])
    parser.add_argument("items", nargs="*")
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--extra", default="", help="extra comma-separated leak terms (people, codenames)")
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--keep-source", action="store_true", help="stage: a SPLIT; the source keeps the project half")
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    if args.command == "stage":
        return cmd_stage(args.work, args.items, args.keep_source)
    if args.command == "edit":
        return cmd_edit(args.work, args.items)
    if args.command == "check":
        return cmd_check(args.work, [t for t in args.extra.split(",") if t])
    return cmd_install(args.work, args.dry)


if __name__ == "__main__":
    sys.exit(main())
