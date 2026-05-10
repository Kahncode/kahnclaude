"""
Find all assets that reference a given Unreal asset via the Asset Registry.

Usage:
    python find_asset_referencers.py <asset_path>

    asset_path - Game-relative path, e.g. /Game/AI/Definitions/Passengers/BD_Passenger_TC

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


def build_referencers_command(asset_path: str) -> str:
    """Build the Python command to run inside the Unreal Editor."""
    return textwrap.dedent(f"""\
        import unreal
        import json

        package_name = '{asset_path}'

        registry = unreal.AssetRegistryHelpers.get_asset_registry()

        # get_referencers requires an AssetRegistryDependencyOptions as 2nd arg
        dep_options = unreal.AssetRegistryDependencyOptions()
        dep_options.include_soft_package_references = True
        dep_options.include_hard_package_references = True
        dep_options.include_searchable_names = False
        dep_options.include_soft_management_references = False

        referencers = registry.get_referencers(package_name, dep_options)

        result = {{
            "target": package_name,
            "referencer_count": len(referencers),
            "referencers": [str(r) for r in referencers],
        }}
        print(json.dumps(result, indent=2))
    """)


def build_referencers_command_alt(asset_path: str) -> str:
    """Alternative approach using EditorAssetLibrary."""
    return textwrap.dedent(f"""\
        import unreal
        import json

        asset_path = '{asset_path}'

        # find_package_referencers_for_asset returns a dict of package->locators
        refs_map = unreal.EditorAssetLibrary.find_package_referencers_for_asset(asset_path)

        referencers = list(refs_map.keys()) if refs_map else []

        result = {{
            "target": asset_path,
            "method": "EditorAssetLibrary.find_package_referencers_for_asset",
            "referencer_count": len(referencers),
            "referencers": [str(r) for r in referencers],
        }}
        print(json.dumps(result, indent=2))
    """)


def run_command_on_editor(command: str) -> dict | None:
    """Connect to the running editor and execute a command."""
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

    print("Executing remote command...", flush=True)
    result = re.run_command(
        command, unattended=True, exec_mode=remote_execution.MODE_EXEC_FILE
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
        raw_output = result.get("output", "")
        if isinstance(raw_output, list):
            for item in raw_output:
                if isinstance(item, dict):
                    print(f"  [{item.get('type', '?')}] {item.get('output', '')}")
                else:
                    print(f"  {item}")
        else:
            print(f"  {raw_output}")

    return None


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    asset_path = sys.argv[1]
    # Fix MSYS/Git-Bash path mangling: it converts /Game/... to C:/Program Files/Git/Game/...
    if "Program Files/Git/Game" in asset_path:
        asset_path = asset_path.replace(
            asset_path[: asset_path.index("/Game")], ""
        )

    print(f"\n=== Finding referencers of: {asset_path} ===\n")

    # Try primary approach: AssetRegistry.get_referencers
    print("--- Method 1: AssetRegistryHelpers.get_asset_registry().get_referencers ---")
    command = build_referencers_command(asset_path)
    data = run_command_on_editor(command)

    if data and "referencers" in data:
        print(f"\nFound {data['referencer_count']} referencer(s):")
        for ref in sorted(data["referencers"]):
            print(f"  {ref}")
        return

    # Fallback: EditorAssetLibrary approach
    print("\n--- Method 2: EditorAssetLibrary.find_package_referencers_for_asset ---")
    command_alt = build_referencers_command_alt(asset_path)
    data = run_command_on_editor(command_alt)

    if data and "referencers" in data:
        print(f"\nFound {data['referencer_count']} referencer(s):")
        for ref in sorted(data["referencers"]):
            print(f"  {ref}")
        return

    print("\nBoth methods failed to retrieve referencers.")
    sys.exit(1)


if __name__ == "__main__":
    main()
