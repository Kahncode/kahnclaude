"""
Read properties from a UE5 .uasset via the Editor's Python Remote Execution protocol.

Usage:
    py read_uasset_property.py <asset_path> [property_name]

    asset_path   - Game-relative path, e.g. /Game/AI/Definitions/Passengers/BD_Passenger_TC
    property_name - (optional) A specific property to print. If omitted, dumps all properties.

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


def build_dump_command(asset_path: str, property_name: str | None = None) -> str:
    """Build the Python command to run inside the Unreal Editor."""
    # This script runs inside the editor's Python interpreter where `unreal` is available.
    if property_name:
        return textwrap.dedent(f"""\
            import unreal
            import json

            asset_path = '{asset_path}'
            prop_name = '{property_name}'

            obj = unreal.load_asset(asset_path)
            if obj is None:
                print(json.dumps({{"error": f"Could not load asset: {{asset_path}}"}}))
            else:
                try:
                    val = getattr(obj, prop_name, '__NOT_FOUND__')
                    if val == '__NOT_FOUND__':
                        # Try get_editor_property for UPROPERTY fields
                        val = obj.get_editor_property(prop_name)
                    # Convert unreal types to string for serialization
                    print(json.dumps({{"asset": asset_path, "property": prop_name, "value": str(val)}}))
                except Exception as e:
                    print(json.dumps({{"error": str(e)}}))
        """)
    else:
        # Dump all properties by listing the object's editor properties
        return textwrap.dedent(f"""\
            import unreal
            import json

            asset_path = '{asset_path}'
            obj = unreal.load_asset(asset_path)
            if obj is None:
                print(json.dumps({{"error": f"Could not load asset: {{asset_path}}"}}))
            else:
                # Get the CDO or instance properties
                props = {{}}
                # Try to enumerate known property names from the class
                cls = obj.get_class()
                cls_name = cls.get_name() if cls else 'Unknown'

                # Use dir() to find potential properties, then read them
                for attr_name in dir(obj):
                    if attr_name.startswith('_'):
                        continue
                    if callable(getattr(type(obj), attr_name, None)):
                        continue
                    try:
                        val = obj.get_editor_property(attr_name)
                        props[attr_name] = str(val)
                    except Exception:
                        pass

                result = {{
                    "asset": asset_path,
                    "class": cls_name,
                    "properties": props,
                }}
                print(json.dumps(result, indent=2))
        """)


def run(asset_path: str, property_name: str | None = None) -> dict | None:
    """Connect to the running editor and execute the property-read command."""
    re = remote_execution.RemoteExecution()
    re.start()

    print("Discovering Unreal Editor nodes...", flush=True)
    # Wait for node discovery (up to 6 seconds)
    for _ in range(6):
        time.sleep(1)
        nodes = re.remote_nodes
        if nodes:
            break
    else:
        print("ERROR: No Unreal Editor instance found. Is the editor running with Python Remote Execution enabled?")
        re.stop()
        return None

    node = nodes[0]
    node_id = node["node_id"]
    print(f"Connected to node: {node_id}")

    re.open_command_connection(node_id)

    command = build_dump_command(asset_path, property_name)
    print("Executing remote command...", flush=True)

    result = re.run_command(command, unattended=True, exec_mode=remote_execution.MODE_EXEC_FILE)

    re.close_command_connection()
    re.stop()

    if result.get("success"):
        # The result dict has 'output' which may be a string or list of dicts/strings
        raw_output = result.get("output", "")
        # Normalize to a single string
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

        # Try to parse the entire output as JSON first (may be multi-line)
        stripped = raw_output.strip()
        if stripped.startswith("{"):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass
        # Try line-by-line
        for line in raw_output.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    pass
        # Fall back to printing raw output
        print("Raw output from editor:")
        print(f"  {raw_output}")
    else:
        print(f"Command failed: {result.get('result', 'Unknown error')}")
        print(f"Full result: {json.dumps(result, indent=2, default=str)}")

    return None


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    asset_path = sys.argv[1]
    property_name = sys.argv[2] if len(sys.argv) > 2 else None

    data = run(asset_path, property_name)
    if data:
        if "error" in data:
            print(f"\nERROR: {data['error']}")
            sys.exit(1)
        else:
            print(f"\nResult:")
            print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
