"""
Dump all property values from a loaded UE5 asset via Python Remote Execution.

Usage:
    python dump_asset_properties.py <asset_path>

    asset_path - Game-relative path, e.g. /Game/AI/Definitions/Passengers/BD_Passenger_TC

Connects to a running Unreal Editor instance and reads every editor-visible
property on the asset, printing a sorted key=value listing for human review.
"""

from __future__ import annotations

import json
import os
import sys
import time
import textwrap

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


def build_dump_command(asset_path: str) -> str:
    """Build the Python command that runs inside the Unreal Editor.

    Enumerates all editor-visible properties on the asset and serializes
    them to JSON, handling common Unreal types (vectors, rotators, enums,
    soft/hard object references, etc.).
    """
    return textwrap.dedent(f"""\
        import unreal
        import json

        def serialize_value(val, depth=0):
            \"\"\"Convert an unreal value to a JSON-safe representation.\"\"\"
            if depth > 4:
                return str(val)
            if val is None:
                return None
            if isinstance(val, (bool, int, float, str)):
                return val
            # Unreal enum
            type_name = type(val).__name__
            if hasattr(val, '__int__'):
                try:
                    return {{"_enum": type_name, "value": int(val), "name": str(val)}}
                except Exception:
                    pass
            # Unreal struct types (FVector, FRotator, FLinearColor, etc.)
            if hasattr(val, '__dict__') or hasattr(val, 'get_editor_property'):
                try:
                    result = {{}}
                    for attr in dir(val):
                        if attr.startswith('_'):
                            continue
                        if callable(getattr(type(val), attr, None)):
                            continue
                        try:
                            sub = getattr(val, attr)
                            result[attr] = serialize_value(sub, depth + 1)
                        except Exception:
                            pass
                    if result:
                        result['_type'] = type_name
                        return result
                except Exception:
                    pass
            # Array/list
            if isinstance(val, (list, tuple)):
                return [serialize_value(v, depth + 1) for v in val]
            return str(val)

        asset_path = '{asset_path}'
        obj = unreal.load_asset(asset_path)
        if obj is None:
            print(json.dumps({{"error": f"Could not load asset: {{asset_path}}"}}))
        else:
            cls = obj.get_class()
            cls_name = cls.get_name() if cls else 'Unknown'
            props = {{}}

            for attr_name in sorted(dir(obj)):
                if attr_name.startswith('_'):
                    continue
                if callable(getattr(type(obj), attr_name, None)):
                    continue
                try:
                    val = obj.get_editor_property(attr_name)
                    props[attr_name] = serialize_value(val)
                except Exception:
                    pass

            result = {{
                "asset": asset_path,
                "class": cls_name,
                "property_count": len(props),
                "properties": props,
            }}
            print(json.dumps(result, indent=2, default=str))
    """)


def connect_to_editor() -> tuple[remote_execution.RemoteExecution, str] | None:
    """Discover and connect to a running Unreal Editor node.

    Returns:
        Tuple of (RemoteExecution instance, node_id) or None on failure.
    """
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
    node_id: str = node["node_id"]
    print(f"Connected to node: {node_id}")
    return re, node_id


def extract_json_from_output(result: dict) -> dict | None:
    """Parse JSON from the remote execution result payload."""
    if not result.get("success"):
        print(f"Command failed: {result.get('result', 'Unknown error')}")
        raw = result.get("output", "")
        if raw:
            print(f"Output: {raw}")
        return None

    raw_output = result.get("output", "")

    # Normalize to string
    if isinstance(raw_output, list):
        lines: list[str] = []
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

    # Try line by line
    for line in raw_output.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                pass

    print("Could not parse JSON from editor output.")
    print(f"Raw output:\n{raw_output}")
    return None


def dump_asset(asset_path: str) -> dict | None:
    """Read all properties from the given asset in the running editor.

    Args:
        asset_path: Game-relative asset path (e.g. /Game/AI/...).

    Returns:
        Parsed JSON dict with asset class and properties, or None on failure.
    """
    connection = connect_to_editor()
    if connection is None:
        return None

    re, node_id = connection

    try:
        re.open_command_connection(node_id)
        command = build_dump_command(asset_path)
        print("Executing property dump...", flush=True)

        result = re.run_command(
            command,
            unattended=True,
            exec_mode=remote_execution.MODE_EXEC_FILE,
        )

        re.close_command_connection()
        return extract_json_from_output(result)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return None
    finally:
        re.stop()


def print_flat_properties(data: dict) -> None:
    """Print properties in a flat, diff-friendly format."""
    props = data.get("properties", {})
    print(f"\nAsset: {data.get('asset', '?')}")
    print(f"Class: {data.get('class', '?')}")
    print(f"Properties ({data.get('property_count', len(props))}):")
    print("-" * 70)

    for key in sorted(props.keys()):
        val = props[key]
        # Format nested dicts compactly on one line if small
        if isinstance(val, dict):
            type_tag = val.pop("_type", None)
            enum_info = val.pop("_enum", None)
            if enum_info:
                print(f"  {key} = {val.get('name', val.get('value', val))}")
                continue
            if type_tag:
                compact = ", ".join(f"{k}={v}" for k, v in sorted(val.items()))
                print(f"  {key} = {type_tag}({compact})")
            else:
                print(f"  {key} = {json.dumps(val, default=str)}")
        elif isinstance(val, list):
            print(f"  {key} = [{len(val)} items] {json.dumps(val, default=str)}")
        else:
            print(f"  {key} = {val}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    asset_path = sys.argv[1]
    data = dump_asset(asset_path)

    if data is None:
        sys.exit(1)

    if "error" in data:
        print(f"\nERROR: {data['error']}")
        sys.exit(1)

    # Print human-readable flat listing
    print_flat_properties(data)

    # Also save raw JSON for later diffing
    out_file = "asset_dump.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nFull JSON saved to: {out_file}")


if __name__ == "__main__":
    main()
