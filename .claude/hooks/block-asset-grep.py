#!/usr/bin/env python3
"""
block-asset-grep.py — Block content searches over Unreal binary assets.

Event: PreToolUse
Matcher: Bash|PowerShell|Grep

Recursive grep/rg/findstr/Select-String over a Content folder, a whole Plugins tree,
or *.uasset/*.umap reads tens of GB and outlives the shell as an orphaned process.
Content/Python (plain .py) stays searchable.
No-op outside an Unreal project (no *.uproject in or one level below the project, no UE_PROJECT).
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from hook_project import find_uproject, layout_hint
except ImportError as import_error:  # helper missing: allow everything rather than block
    print(f"block-asset-grep: {import_error}; allowing", file=sys.stderr)
    sys.exit(0)

REASON = (
    "BLOCKED: content search over Unreal binary assets (Content / Plugins / .uasset / .umap) "
    "thrashes the disk and orphans. Find assets by file name (Glob **/Name*.uasset), "
    "find referencers via the asset registry (unreal-asset-inspections skill), "
    "and limit code searches to Source / Config / Content/Python."
)

ASSET_EXTENSION = re.compile(r"\.(uasset|umap)\b", re.IGNORECASE)
SEGMENT_SPLIT = re.compile(r"\|\||&&|[;|\n]")
SEARCH_TOOLS = {"grep", "egrep", "fgrep", "rg", "findstr", "select-string", "sls"}
LISTING_TOOLS = {"get-childitem", "gci", "dir", "ls"}
# Flags whose value is the next token, so it is not mistaken for a path.
# Single-letter flags are case-sensitive (grep -c counts, -C N is context); longer ones are lowercased.
VALUE_FLAGS = {"-e", "-f", "-m", "-A", "-B", "-C", "-d", "-D", "-g", "-t", "-T", "-j", "-M", "-pattern",
               "--glob", "--iglob", "--type", "--type-not", "--regexp", "--file"}
PATTERN_FLAGS = {"-e", "-f", "--regexp", "--file", "-pattern"}
PATH_FLAGS = {"-path", "-literalpath", "-include", "-filter"}
RECURSE_LISTING_FLAGS = {"-recurse", "-r", "-R", "-s"}
SOURCE_EXTENSIONS = frozenset(
    "h hpp inl cpp c cs ini py json md txt log usf ush uplugin uproject build target "
    "ps1 bat sh xml yaml yml csv toml".split())
# Glob folders whose files are text: `{Source,Config}/**/*`, `Content/Python/**`.
SOURCE_FOLDERS = ("source", "config")
GIT_BASH_DRIVE = re.compile(r"^/([a-zA-Z])(?:/|$)")
# "*.cpp", ".h", "*.{cpp,h}", "LyraCharacter.cpp", "**/Ticker*.cs", "*.Build.cs"
SOURCE_ONLY_FILTER = re.compile(r"^(?:[^{}]*\.)?(\{[\w,]+\}|\w+)$", re.IGNORECASE)


def root_grep_reason(layout: str) -> str:
    return ("BLOCKED: Grep from the workspace root with no glob/type walks Engine/ and Content/ and times out. "
            f"Pass a narrow `path` ({layout}, docs, .claude) or a `glob`/`type` filter.")


def include_filters(tokens: list[str]) -> list[str]:
    """--include=X, -g X / --glob X / --iglob X values (rg/grep file filters)."""
    found = []
    for i, token in enumerate(tokens):
        lower = token.lower()
        if lower.startswith("--include="):
            found.append(token.partition("=")[2])
        elif lower in ("-g", "--glob", "--iglob", "--include") and i + 1 < len(tokens):
            found.append(tokens[i + 1])
    return [f.strip("'\"") for f in found]


def is_source_filter(name: str) -> bool:
    match = SOURCE_ONLY_FILTER.match(name)
    if not match or "." not in name and "{" not in name:
        return False
    exts = match.group(1).strip("{}").lower().split(",")
    return all(e in SOURCE_EXTENSIONS for e in exts)


def expand_braces(glob: str, limit: int = 256) -> list[str]:
    """`{Source/**/*.{h,cpp},Config/*.ini}` -> Source/**/*.h, Source/**/*.cpp, Config/*.ini."""
    start = glob.find("{")
    if start < 0:
        return [glob]
    depth, bounds = 0, [start]
    for i in range(start, len(glob)):
        depth += {"{": 1, "}": -1}.get(glob[i], 0)
        if glob[i] == "," and depth == 1 or depth == 0:
            bounds.append(i)
            if depth == 0:
                break
    else:
        return [glob]
    head, tail, out = glob[:start], glob[bounds[-1] + 1:], []
    for a, b in zip(bounds, bounds[1:]):
        out.extend(expand_braces(head + glob[a + 1:b] + tail, limit))
        if len(out) >= limit:
            break
    return out[:limit]


def is_source_glob(glob: str, base: str | None = None) -> bool:
    """One brace-free glob alternative that only matches text files, or a folder that is not an asset tree.
    With `base` (the Grep path) the glob's literal folder prefix is checked like a search path."""
    parts = [p for p in glob.lower().split("/") if p]
    if not parts or glob.startswith("!") or ASSET_EXTENSION.search(glob):
        return False
    if is_source_filter(parts[-1]) or any(p in SOURCE_FOLDERS for p in parts):
        return True
    literal = []
    for part in parts:
        if re.search(r"[*?\[{]", part):
            break
        literal.append(part)
    if base is None or not literal:
        return parts[:2] == ["content", "python"]
    return not is_asset_path("/".join(literal), base)


def only_source_files(tokens: list[str], base: str | None = None) -> bool:
    filters = include_filters(tokens)
    return bool(filters) and all(is_source_glob(g, base) for f in filters for g in expand_braces(f))


def excludes_content(tokens: list[str]) -> bool:
    return any(t.lower().strip("'\"") in ("--exclude-dir=content", "--exclude-dir=*content*") for t in tokens)


def norm(path: str) -> str:
    return re.sub(r"[\\/]+$", "", os.path.normpath(path).replace("\\", "/").lower())


def windows_path(path: str) -> str:
    """Git Bash `/c/src/x` -> `c:/src/x`; `~` expanded; quotes stripped."""
    return GIT_BASH_DRIVE.sub(lambda m: m.group(1) + ":/", os.path.expanduser(path.strip("'\"")))


def resolve(path: str, base: str = "") -> str:
    """A relative path joins the folder of an earlier `cd` (or the tool-call cwd)."""
    raw = windows_path(path)
    if base and raw and not os.path.isabs(raw):
        raw = os.path.normpath(os.path.join(windows_path(base), raw))
    return raw


def is_asset_path(path: str, base: str = "") -> bool:
    full = resolve(path, base)
    parts = [p for p in re.split(r"[\\/]+", full.lower()) if p]
    if not parts or ASSET_EXTENSION.search(path):
        return bool(parts)
    in_source = "source" in parts
    if parts[-1] == "plugins" and not in_source:
        return True
    for i, part in enumerate(parts):
        if part == "content" and "source" not in parts[:i]:
            return not (i + 1 < len(parts) and parts[i + 1] == "python")
    return not in_source and holds_assets(full)


def holds_assets(full: str) -> bool:
    """The workspace root, or a workspace folder that holds Content/ or Plugins/ (<Project>/, Engine/)."""
    project = windows_path(os.environ.get("CLAUDE_PROJECT_DIR", ""))
    if project:
        root, here = norm(project), norm(full)
        if here == root:
            return True
        if os.path.isabs(full) and not here.startswith(root + "/"):
            return False
    return any(os.path.isdir(os.path.join(full, d)) for d in ("Content", "Plugins"))


def tokenize(segment: str) -> list[str]:
    try:
        return [t.strip("'\"") for t in shlex.split(segment, posix=False)]
    except ValueError:
        return segment.split()


def classify_args(tokens: list[str]) -> tuple[set[str], list[str], list[str], bool]:
    """Return (flags, positional args, flag values, pattern-given-by-flag)."""
    flags, positional, values = set(), [], []
    pattern_by_flag = False
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "--":
            positional.extend(tokens[i + 1:])
            break
        # A quoted pattern such as "-d in args" holds whitespace; a flag never does.
        is_flag = token.startswith("-") or token.startswith("/") and len(token) == 2
        if is_flag and not re.search(r"\s", token):
            name, _, inline = token.partition("=")
            name = name if len(name) == 2 and name[0] == "-" else name.lower()
            flags.add(name)
            if inline:
                values.append(inline)
            elif name in VALUE_FLAGS or name in PATH_FLAGS:
                if i + 1 < len(tokens):
                    values.append(tokens[i + 1])
                pattern_by_flag |= name in PATTERN_FLAGS
                i += 1
        else:
            positional.append(token)
        i += 1
    return flags, positional, values, pattern_by_flag


def is_recursive(tool: str, flags: set[str]) -> bool:
    if tool == "rg":
        return True
    if tool == "findstr":
        return "/s" in flags
    if tool in ("select-string", "sls"):
        return False
    return any(f in ("--recursive", "-d") or re.fullmatch(r"-\w*[rR]\w*", f) for f in flags)


def search_hits_assets(tool: str, args: list[str], cwd: str) -> bool:
    flags, positional, values, pattern_by_flag = classify_args(args)
    if any(ASSET_EXTENSION.search(v) for v in values):
        return True
    if only_source_files(args) or excludes_content(args):
        return False
    if tool in ("select-string", "sls"):
        return any(is_asset_path(v, cwd) for v in values)
    if not is_recursive(tool, flags):
        return False
    paths = positional if pattern_by_flag else positional[1:]
    if not paths:
        return is_asset_path(cwd)
    return any(is_asset_path(p, cwd) for p in paths)


def listing_hits_assets(args: list[str]) -> bool:
    flags, positional, values, _ = classify_args(args)
    if not (RECURSE_LISTING_FLAGS & flags):
        return False
    return any(is_asset_path(p, "") or ASSET_EXTENSION.search(p) for p in positional + values)


def split_segments(command: str) -> list[str]:
    """Split on ; | && || and newlines outside quotes (a grep pattern like "a\\|b" stays whole)."""
    segments, start, quote, i = [], 0, "", 0
    while i < len(command):
        ch = command[i]
        if quote:
            if ch == "\\" and quote == '"':
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "'\"":
            quote = ch
        else:
            match = SEGMENT_SPLIT.match(command, i)
            if match:
                segments.append(command[start:i])
                i = start = match.end()
                continue
        i += 1
    segments.append(command[start:])
    return segments


def shell_hits_assets(command: str, cwd: str) -> bool:
    previous_lists_assets = False
    for segment in split_segments(command):
        tokens = tokenize(segment.strip())
        if not tokens:
            continue
        tool = re.sub(r"\.exe$", "", tokens[0].replace("\\", "/").split("/")[-1].lower())
        if tool in ("cd", "set-location", "pushd") and len(tokens) > 1:
            target = next((t for t in tokens[1:] if not t.startswith("-")), "")
            cwd = resolve(target, cwd) if target else cwd
        elif tool == "find" and find_exec_hits_assets(tokens[1:], cwd):
            return True
        elif tool in LISTING_TOOLS:
            previous_lists_assets = listing_hits_assets(tokens[1:])
            continue
        elif tool in SEARCH_TOOLS:
            if previous_lists_assets or search_hits_assets(tool, tokens[1:], cwd):
                return True
        previous_lists_assets = False
    return False


def find_exec_hits_assets(args: list[str], cwd: str) -> bool:
    """find <Content|Plugins> ... -exec/xargs grep: the hook's search-tool check never sees it."""
    if not any(a.lower() in SEARCH_TOOLS for a in args):
        return False
    roots = [a for a in args if not a.startswith("-") and not a.startswith("(")][:1] or [cwd]
    return is_asset_path(roots[0], cwd) or any(ASSET_EXTENSION.search(a) for a in args)


def grep_tool_unscoped(tool_input: dict, cwd: str, project_dir: str) -> bool:
    path = tool_input.get("path") or cwd
    if tool_input.get("glob") or tool_input.get("type"):
        return False
    return bool(project_dir) and norm(windows_path(path)) == norm(windows_path(project_dir))


def excludes_content_glob(glob: str, path: str) -> bool:
    """`!Content/**` / `!**/Content/**`: everything but Content (not from the workspace root, which has none)."""
    if not glob.startswith("!"):
        return False
    if not any(re.match(r"(.*[/*])?content([/*]|$)", g.lower()) for g in expand_braces(glob[1:])):
        return False
    project = os.environ.get("CLAUDE_PROJECT_DIR", "")
    return not project or norm(windows_path(path)) != norm(windows_path(project))


def grep_tool_hits_assets(tool_input: dict, cwd: str) -> bool:
    for key in ("glob", "type"):
        if ASSET_EXTENSION.search(str(tool_input.get(key) or "")):
            return True
        if str(tool_input.get(key) or "").lower() in ("uasset", "umap"):
            return True
    glob = str(tool_input.get("glob") or "")
    path = tool_input.get("path") or cwd
    if only_source_files(["--glob", glob], path) or "/source/" in f"/{glob.lower()}":
        return False
    if excludes_content_glob(glob, path):
        return False
    if str(tool_input.get("type") or "").lower() in ("cpp", "c", "cs", "py", "h", "ini", "json", "md"):
        return False
    return is_asset_path(tool_input.get("path") or cwd, cwd)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    cwd = data.get("cwd", "") or ""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
    uproject = find_uproject(project_dir)
    if not uproject:
        sys.exit(0)
    if data.get("tool_name") == "Grep":
        blocked = grep_tool_hits_assets(tool_input, cwd)
        if not blocked and grep_tool_unscoped(tool_input, cwd, project_dir):
            deny(root_grep_reason(layout_hint(project_dir, uproject, ("Source", "Config"))))
            return
    else:
        blocked = shell_hits_assets(tool_input.get("command", "") or "", cwd)
    if not blocked:
        sys.exit(0)
    deny(REASON)


def deny(reason: str) -> None:
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, sys.stdout)


if __name__ == "__main__":
    main()
