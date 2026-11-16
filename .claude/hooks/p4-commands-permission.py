#!/usr/bin/env python3
"""
p4-commands-permission.py — Permission gate for P4 shell commands.

Event: PreToolUse
Matcher: Bash|PowerShell

Any blocked p4 subcommand anywhere in the command gets permissionDecision "deny".
Any destructive, workspace-switching or Engine/binary-opening p4 command anywhere gets "ask".
A single, unchained p4 command with a safe subcommand gets "allow".
Everything else gets no opinion (exit 0) and falls through to normal permissions.
"""
import functools
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from hook_project import project_var
except ImportError as import_error:  # helper missing: env vars only, generic rules still apply
    print(f"p4-commands-permission: {import_error}", file=sys.stderr)

    def project_var(name: str, project_dir: str) -> str:
        return os.environ.get(name, "")

SAFE_SUBCOMMANDS = frozenset({
    "status",
    "opened",
    "changes",
    "diff",
    "diff2",
    "describe",
    "client",
    "clients",
    "stream",
    "streams",
    "shelve",
    "edit",
    "add",
    "filelog",
    "files",
    "fstat",
    "where",
    "info",
    "change",
    "reopen",
    "set",
    "print",
    "property",
    "revert",
    "sync",
})


def project_dir() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR", "")


@functools.cache
def own_extra_clients() -> frozenset[str]:
    """The user's other workspaces (P4CLIENT_DEVTOOLS, comma list): `p4 -c <these>` is not "another workspace"."""
    names = project_var("P4CLIENT_DEVTOOLS", project_dir()).split(",")
    return frozenset(n.strip().lower() for n in names if n.strip())


BLOCKED_SUBCOMMANDS = frozenset({
    "submit",
    "obliterate",
    "admin",
    "protect",
    "counter",
    "populate",
})

BLOCK_REASONS = {
    "submit": "Create a pending changelist or shelve instead.",
    "obliterate": "p4 obliterate permanently destroys files.",
    "admin": "p4 admin commands are not allowed.",
    "protect": "p4 protect commands are not allowed.",
    "counter": "p4 counter commands are not allowed.",
    "populate": "p4 populate creates a submitted change.",
}

# Destroy or overwrite local work in the shared workspace: always prompt.
ASK_SUBCOMMANDS = frozenset({"revert", "clean", "delete", "unshelve", "move", "rename", "switch"})

# Rewrite workspace files or the have list, or open files into a CL. `-n` (preview) stays no-opinion.
WORKSPACE_ASK_SUBCOMMANDS = frozenset({
    "sync", "flush", "reconcile", "unload", "integrate", "integ", "copy", "merge", "undo", "retype"})

# Only these forms are read-only; any other form switches or rewrites workspace/stream/env state.
READ_ONLY_FORMS = {
    "client": lambda args: not args or "-o" in args,
    "stream": lambda args: not args or "-o" in args,
    "set": lambda args: not any("=" in a for a in args),
    "property": lambda args: "-l" in args,
}

ENGINE_OR_BINARY = re.compile(
    r"(^|[\\/])(Engine|Binaries)[\\/]|\.(exe|dll|pdb|lib)$", re.IGNORECASE)
BINARY = re.compile(r"(^|[\\/])Binaries[\\/]|\.(exe|dll|pdb|lib|modules|target)$", re.IGNORECASE)

# Local-only setup files (LOCAL_ONLY_PATHS; CLAUDE.md "Local-Only Files"): never opened into a CL without asking.
DEFAULT_LOCAL_ONLY_PATHS = ".claude/,docs/,scripts/,.temp/,CLAUDE.local.md"
SEP = r"[\\/]"

# Safe subcommands whose -d flag deletes a workspace, changelist, shelf or stream.
DELETE_FLAG_SUBCOMMANDS = frozenset({"client", "change", "shelve", "stream"})

# p4 global options that consume the next token (e.g. `p4 -c ws submit`, `p4 -F %clientName% info`).
GLOBAL_OPTIONS_WITH_VALUE = frozenset("bcCdFHLpPQruvxz")

# `p4 …` / `p4.exe …`, or a full path ending in p4[.exe] (`& "C:\Program Files\Perforce\p4.exe" revert`).
# A bare `/c/p4 ` folder path is not an invocation: the full-path form needs `.exe` or a closing quote.
P4_INVOCATION = re.compile(
    r"(?<![\w.\-/\\])p4(?:\.exe)?(?=\s)|(?<=[\\/])p4(?:\.exe[\"']?|[\"'])(?=\s)", re.IGNORECASE)
SHELL_SEPARATORS = re.compile(r"[;|&\n`]|\$\(")
# Where one p4 invocation's arguments end; `)` closes `$(p4 -F %Client% client -o)`.
INVOCATION_END = re.compile(r"[;|&\n`)]|\$\(")
WILDCARD = re.compile(r"\.\.\.|\*")


def local_only_entries() -> list[str]:
    raw = project_var("LOCAL_ONLY_PATHS", project_dir()) or DEFAULT_LOCAL_ONLY_PATHS
    return [e.strip() for e in raw.split(",") if e.strip()]


def root_anchors() -> list[str]:
    """`/<depot>/` + optional `<stream>/` from P4_DEPOT_ROOT/P4_STREAM, and `/<workspace folder>/`."""
    depot = project_var("P4_DEPOT_ROOT", project_dir()).strip("/")
    stream = project_var("P4_STREAM", project_dir()).strip("/")
    anchors = []
    if depot:
        rest = stream[len(depot) + 1:] if stream.lower().startswith(depot.lower() + "/") else ""
        tail = f"({SEP.join(re.escape(p) for p in rest.split('/'))}{SEP})?" if rest else ""
        anchors.append(f"{SEP}{re.escape(depot)}{SEP}{tail}")
    folder = os.path.basename(os.path.normpath(project_dir())) if project_dir() else ""
    if folder and folder.lower() != depot.lower():
        anchors.append(f"{SEP}{re.escape(folder)}{SEP}")
    return anchors


@functools.cache
def local_only_pattern() -> re.Pattern:
    """Folders (`x/`) match at the path start, `./` or under a root anchor; files match by name."""
    entries = local_only_entries()
    folders = [re.escape(e.rstrip("/\\")) for e in entries if e.endswith(("/", "\\"))]
    files = [re.escape(e) for e in entries if not e.endswith(("/", "\\"))]
    parts = []
    if folders:
        anchors = "|".join(["^", rf"^\.{SEP}", *root_anchors()])
        parts.append(f"({anchors})({'|'.join(folders)})({SEP}|$)")
    if files:
        parts.append(f"(^|{SEP})({'|'.join(files)})$")
    return re.compile("|".join(parts) or r"(?!)", re.IGNORECASE)


def local_only_reason() -> str:
    names = local_only_entries()
    listed = ", ".join(names[:-1]) + f" and {names[-1]}" if len(names) > 1 else "".join(names)
    return f"{listed} are local-only (LOCAL_ONLY_PATHS); never p4 add/edit them."


def parse_invocation(tail: str) -> tuple[str, list[str], str]:
    """Return (subcommand, args, `-c` client or "") for the text following a `p4` token."""
    segment = INVOCATION_END.split(tail, maxsplit=1)[0]
    tokens = [t.strip("'\"") for t in segment.split()]
    i, client = 0, ""
    while i < len(tokens) and tokens[i].startswith("-"):
        is_bare_value_option = len(tokens[i]) == 2 and tokens[i][1] in GLOBAL_OPTIONS_WITH_VALUE
        if tokens[i] == "-c" and i + 1 < len(tokens):
            client = tokens[i + 1]
        i += 2 if is_bare_value_option else 1
    if i >= len(tokens):
        return "", [], client
    return tokens[i].lower(), tokens[i + 1:], client


def own_client() -> str:
    """P4CLIENT from the workspace .p4config, else the environment ("" when unknown)."""
    config = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", ""), ".p4config")
    try:
        with open(config, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                key, _, value = line.strip().partition("=")
                if key.strip().upper() == "P4CLIENT" and value.strip():
                    return value.strip()
    except OSError:
        pass
    return os.environ.get("P4CLIENT", "")


def other_client_reason(client: str) -> str | None:
    own = {own_client().lower()} | own_extra_clients()
    if client and client.lower() not in own:
        return f"p4 -c {client} targets another workspace than this one."
    return None


def file_args(args: list[str]) -> list[str]:
    """Positional args, skipping flag values such as `-c <CL>`."""
    files, skip = [], False
    for a in args:
        if skip:
            skip = False
        elif a.startswith("-"):
            skip = a in ("-c", "-t", "-x")
        else:
            files.append(a)
    return files


def is_binary_keep_local_revert(subcommand: str, args: list[str]) -> bool:
    """`p4 revert -k <binaries>` un-opens rebuilt binaries and keeps the local files (code-dev rule)."""
    files = file_args(args)
    return subcommand == "revert" and "-k" in args and bool(files) and all(BINARY.search(f) for f in files)


def is_lossless_form(subcommand: str, args: list[str]) -> bool:
    """Forms that cannot lose local edits: revert -n (any), revert -a/-k, named-file sync, change -d (empty CLs only)."""
    files = file_args(args)
    no_wildcard = bool(files) and not any(WILDCARD.search(f) for f in files)
    if subcommand == "revert":
        return "-n" in args or (no_wildcard and any(a in ("-a", "-k") for a in args))
    if subcommand == "sync":
        return no_wildcard and not any(a in ("-f", "-k", "-p") for a in args)
    return subcommand == "change" and "-d" in args and "-f" not in args


def ask_reason(subcommand: str, args: list[str]) -> str | None:
    if is_binary_keep_local_revert(subcommand, args) or is_lossless_form(subcommand, args):
        return None
    if subcommand in ASK_SUBCOMMANDS:
        return f"p4 {subcommand} can destroy or overwrite local work in the shared workspace."
    if subcommand in DELETE_FLAG_SUBCOMMANDS and "-d" in args:
        return f"p4 {subcommand} -d deletes a workspace, changelist, shelf or stream."
    if subcommand == "sync" and any(a in ("-f", "-k") for a in args):
        return "p4 sync -f/-k overwrites local files or the have list."
    if subcommand in WORKSPACE_ASK_SUBCOMMANDS and "-n" not in args:
        return f"p4 {subcommand} rewrites workspace files or the have list, or opens files in the shared workspace."
    if subcommand in ("reopen", "edit") and any(WILDCARD.search(a) for a in file_args(args)):
        return f"p4 {subcommand} with a wildcard sweeps files from every session in the shared workspace."
    if subcommand == "resolve" and any(a in ("-at", "-ay", "-af") for a in args):
        return "p4 resolve -at/-ay/-af discards one side of the merge."
    if subcommand in READ_ONLY_FORMS and not READ_ONLY_FORMS[subcommand](args):
        return f"p4 {subcommand} in a write form switches or rewrites workspace/stream/env state."
    if subcommand in ("edit", "add") and any(ENGINE_OR_BINARY.search(a) for a in args):
        return "Opening Engine/ or binary files needs explicit approval (CLAUDE.md; binaries stay local)."
    if subcommand in ("edit", "add", "reopen") and any(local_only_pattern().search(a) for a in file_args(args)):
        return local_only_reason()
    return None


def decide(command: str) -> tuple[str, str] | None:
    invocations = [parse_invocation(command[m.end():]) for m in P4_INVOCATION.finditer(command)]
    if not invocations:
        return None

    for subcommand, _, _ in invocations:
        if subcommand in BLOCKED_SUBCOMMANDS:
            return "deny", f"BLOCKED: p4 {subcommand} — {BLOCK_REASONS[subcommand]}"

    for subcommand, args, client in invocations:
        reason = ask_reason(subcommand, args) or other_client_reason(client)
        if reason:
            return "ask", reason

    # Auto-allowing a chained command would also approve whatever else is chained to it.
    if len(invocations) != 1 or SHELL_SEPARATORS.search(command):
        return None

    subcommand, args, _ = invocations[0]
    if subcommand not in SAFE_SUBCOMMANDS:
        return None
    return "allow", f"Safe p4 command: p4 {subcommand}"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    decision = decide(command) if command else None
    if decision is None:
        sys.exit(0)

    permission, reason = decision
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": permission,
            "permissionDecisionReason": reason,
        }
    }, sys.stdout)


if __name__ == "__main__":
    main()
