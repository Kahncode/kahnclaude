#!/usr/bin/env python3
"""Execute arbitrary Python code in the running Unreal Editor via Remote Execution.

Usage:
    py editor-py.py --code "print(unreal.EditorLevelLibrary.get_editor_world().get_name())"
    py editor-py.py --file "/path/to/script.py"

Requires KC_UE_ENGINE environment variable to locate the Remote Execution module.
"""

import argparse
import os
import sys
import time

_ENGINE_ROOT = os.environ.get("KC_UE_ENGINE", "")
_RE_PATH = os.path.join(
    _ENGINE_ROOT,
    "Plugins", "Experimental", "PythonScriptPlugin", "Content", "Python",
)
if _RE_PATH not in sys.path:
    sys.path.insert(0, _RE_PATH)

from remote_execution import RemoteExecution, MODE_EXEC_FILE  # noqa: E402


def run_code(code: str, timeout: float = 30.0) -> int:
    """Send code to the editor and return exit code."""
    remote = RemoteExecution()
    remote.start()

    deadline = time.time() + timeout
    while not remote.remote_nodes:
        if time.time() > deadline:
            print("ERROR: No Unreal Editor instance found", file=sys.stderr)
            remote.stop()
            return 1
        time.sleep(0.25)

    node = remote.remote_nodes[0]
    remote.open_command_connection(node["node_id"])
    result = remote.run_command(code, unattended=True, exec_mode=MODE_EXEC_FILE)
    remote.close_command_connection()
    remote.stop()

    for line in result.get("output", []):
        text = line.get("output", "")
        if line.get("type") == "Error":
            print(f"[ERR] {text}", file=sys.stderr)
        else:
            print(text)

    return 0 if result.get("success", False) else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute Python in the running Unreal Editor"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--code", help="Inline Python code to execute")
    group.add_argument("--file", help="Path to a Python script file to execute")
    args = parser.parse_args()

    if not _ENGINE_ROOT:
        print("ERROR: KC_UE_ENGINE environment variable not set", file=sys.stderr)
        return 1

    if args.file:
        if not os.path.isfile(args.file):
            print(f"ERROR: File not found: {args.file}", file=sys.stderr)
            return 1
        with open(args.file, encoding="utf-8") as f:
            code = f.read()
    else:
        code = args.code

    return run_code(code)


if __name__ == "__main__":
    sys.exit(main())
