"""
Set a property on a UE5 .uasset via the Editor's Python Remote Execution protocol.

Usage:
    python set_uasset_property.py <asset_path> <property_path> <value>

    asset_path    - Game-relative path, e.g. /Game/AI/Definitions/Passengers/BD_Passenger_TC
    property_path - Dot-separated property path, e.g. config.patrol_distance
    value         - The new value (auto-detected as float, int, bool, or string)

Requires a running Unreal Editor instance with Python Remote Execution enabled
(DefaultEngine.ini -> bRemoteExecution=True, default multicast 239.0.0.1:6766).
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
import time

engine_root = os.environ.get("KC_UE_ENGINE")
if not engine_root:
    print("ERROR: KC_UE_ENGINE environment variable is not set.", file=sys.stderr)
    sys.exit(1)
ENGINE_PYTHON_PATH = os.path.join(
    engine_root, "Plugins", "Experimental",
    "PythonScriptPlugin", "Content", "Python",
)
if ENGINE_PYTHON_PATH not in sys.path:
    sys.path.insert(0, ENGINE_PYTHON_PATH)

import remote_execution  # noqa: E402


def build_set_command(
    asset_path: str,
    property_path: str,
    value: str,
) -> str:
    """Build the Python command to run inside the Unreal Editor.

    Args:
        asset_path: Game-relative asset path.
        property_path: Dot-separated property path (e.g. 'config.patrol_distance').
        value: String representation of the value to set.
    """
    # Parse the property path into segments
    segments = property_path.split(".")

    if len(segments) == 1:
        # Simple top-level property
        return textwrap.dedent(f"""\
            import unreal
            import json

            asset_path = '{asset_path}'
            prop_name = '{segments[0]}'
            new_value = {value}

            obj = unreal.load_asset(asset_path)
            if obj is None:
                print(json.dumps({{"error": f"Could not load asset: {{asset_path}}"}}))
            else:
                try:
                    old_value = obj.get_editor_property(prop_name)
                    obj.set_editor_property(prop_name, new_value)
                    updated_value = obj.get_editor_property(prop_name)
                    unreal.EditorAssetLibrary.save_asset(asset_path)
                    print(json.dumps({{
                        "asset": asset_path,
                        "property": prop_name,
                        "old_value": str(old_value),
                        "new_value": str(updated_value),
                        "saved": True,
                    }}))
                except Exception as e:
                    print(json.dumps({{"error": str(e)}}))
        """)
    elif len(segments) == 2:
        # Nested struct property: get struct, modify field, set struct back, save
        struct_name = segments[0]
        field_name = segments[1]
        return textwrap.dedent(f"""\
            import unreal
            import json

            asset_path = '{asset_path}'
            struct_name = '{struct_name}'
            field_name = '{field_name}'
            new_value = {value}

            obj = unreal.load_asset(asset_path)
            if obj is None:
                print(json.dumps({{"error": f"Could not load asset: {{asset_path}}"}}))
            else:
                try:
                    struct_val = obj.get_editor_property(struct_name)
                    old_field = struct_val.get_editor_property(field_name)
                    struct_val.set_editor_property(field_name, new_value)
                    obj.set_editor_property(struct_name, struct_val)
                    # Re-read to confirm
                    confirmed = obj.get_editor_property(struct_name).get_editor_property(field_name)
                    unreal.EditorAssetLibrary.save_asset(asset_path)
                    print(json.dumps({{
                        "asset": asset_path,
                        "property": f"{{struct_name}}.{{field_name}}",
                        "old_value": str(old_field),
                        "new_value": str(confirmed),
                        "saved": True,
                    }}))
                except Exception as e:
                    print(json.dumps({{"error": str(e)}}))
        """)
    else:
        # Deeper nesting: get each struct level into a local variable,
        # set the leaf, then set each struct back up the chain.
        segments_repr = repr(segments)
        return textwrap.dedent(f"""\
            import unreal
            import json

            asset_path = '{asset_path}'
            new_value = {value}
            segments = {segments_repr}

            obj = unreal.load_asset(asset_path)
            if obj is None:
                print(json.dumps({{"error": f"Could not load asset: {{asset_path}}"}}))
            else:
                try:
                    # Walk down the chain, collecting each struct level
                    levels = [obj]
                    for seg in segments[:-1]:
                        levels.append(levels[-1].get_editor_property(seg))

                    leaf = segments[-1]
                    old_field = levels[-1].get_editor_property(leaf)

                    # Set the leaf value on the deepest struct
                    levels[-1].set_editor_property(leaf, new_value)

                    # Walk back up, setting each parent struct
                    for i in range(len(levels) - 1, 0, -1):
                        levels[i - 1].set_editor_property(segments[i - 1], levels[i])

                    # Re-read to confirm
                    check = obj
                    for seg in segments[:-1]:
                        check = check.get_editor_property(seg)
                    confirmed = check.get_editor_property(leaf)

                    unreal.EditorAssetLibrary.save_asset(asset_path)
                    print(json.dumps({{
                        "asset": asset_path,
                        "property": '{property_path}',
                        "old_value": str(old_field),
                        "new_value": str(confirmed),
                        "saved": True,
                    }}))
                except Exception as e:
                    print(json.dumps({{"error": str(e)}}))
        """)


def run(asset_path: str, property_path: str, value: str) -> dict | None:
    """Connect to the running editor and execute the property-set command."""
    re = remote_execution.RemoteExecution()
    re.start()

    print("Discovering Unreal Editor nodes...", flush=True)
    for _ in range(6):
        time.sleep(1)
        nodes = re.remote_nodes
        if nodes:
            break
    else:
        print(
            "ERROR: No Unreal Editor instance found. "
            "Is the editor running with Python Remote Execution enabled?"
        )
        re.stop()
        return None

    node = nodes[0]
    node_id = node["node_id"]
    print(f"Connected to node: {node_id}")

    re.open_command_connection(node_id)

    command = build_set_command(asset_path, property_path, value)
    print("Executing remote command...", flush=True)

    result = re.run_command(
        command,
        unattended=True,
        exec_mode=remote_execution.MODE_EXEC_FILE,
    )

    re.close_command_connection()
    re.stop()

    if result.get("success"):
        raw_output = result.get("output", "")
        if isinstance(raw_output, list):
            lines = []
            for item in raw_output:
                if isinstance(item, dict):
                    lines.append(item.get("output", str(item)))
                else:
                    lines.append(str(item))
            raw_output = "\n".join(lines)
        elif isinstance(raw_output, dict):
            raw_output = raw_output.get("output", str(raw_output))

        stripped = raw_output.strip()
        if stripped.startswith("{"):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass
        for line in raw_output.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    pass
        print("Raw output from editor:")
        print(f"  {raw_output}")
    else:
        print(f"Command failed: {result.get('result', 'Unknown error')}")
        print(f"Full result: {json.dumps(result, indent=2, default=str)}")

    return None


def main() -> None:
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    asset_path = sys.argv[1]
    property_path = sys.argv[2]
    value = sys.argv[3]

    data = run(asset_path, property_path, value)
    if data:
        if "error" in data:
            print(f"\nERROR: {data['error']}")
            sys.exit(1)
        else:
            print(f"\nResult:")
            print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
