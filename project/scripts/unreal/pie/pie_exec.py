#!/usr/bin/env python3
"""Execute a console command in the active PIE session.

Usage:
    KC_UE_ENGINE="/path/to/UnrealEngine" py scripts/unreal/pie/pie_exec.py "AddItems chest 1"
    KC_UE_ENGINE="/path/to/UnrealEngine" py scripts/unreal/pie/pie_exec.py "God"
"""

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

CODE_TEMPLATE = """
import unreal
editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_sub.get_game_world()
if game_world is None:
    print("ERROR: PIE is not running")
else:
    unreal.SystemLibrary.execute_console_command(game_world, {command!r})
    print(f"Executed: {command!r}")
"""


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: pie_exec.py <console_command>", file=sys.stderr)
        return 1

    command = " ".join(sys.argv[1:])
    code = CODE_TEMPLATE.format(command=command)

    remote = RemoteExecution()
    remote.start()

    deadline = time.time() + 30.0
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


if __name__ == "__main__":
    sys.exit(main())
