#!/usr/bin/env python3
"""Stop the active Play In Editor (PIE) session in the running Unreal Editor."""

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

CODE = """
import unreal
subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not subsystem.is_in_play_in_editor():
    print("PIE is not running")
else:
    subsystem.editor_request_end_play()
    print("PIE stopped")
"""


def main() -> int:
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
    result = remote.run_command(CODE, unattended=True, exec_mode=MODE_EXEC_FILE)
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
