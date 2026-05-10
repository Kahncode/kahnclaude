#!/usr/bin/env python3
"""Resolve code review dimension names to standards file paths."""

import argparse
import sys
from pathlib import Path

DIMENSIONS = {
    "correctness": "review-code-correctness.md",
    "style": "review-code-style.md",
    "readability": "review-code-readability.md",
    "pragmatism": "review-code-pragmatism.md",
    "solid": "review-code-solid.md",
    "architecture": "review-code-architecture.md",
    "performance": "review-code-performance.md",
    "robustness": "review-code-robustness.md",
    "debuggability": "review-code-debuggability.md",
    "interface": "review-code-interface.md",
    "ue-best-practice": "review-code-ue-best-practice.md",
    "networking": "review-code-networking.md",
}

STANDARDS_PATH = Path("project/docs/standards/code")


def resolve_dimension(dimension: str) -> Path:
    """Resolve dimension name to absolute file path."""
    normalized = dimension.lower().strip()

    if normalized not in DIMENSIONS:
        raise ValueError(
            f"Unknown dimension: {dimension}. Valid: {', '.join(sorted(DIMENSIONS))}"
        )

    full_path = STANDARDS_PATH / DIMENSIONS[normalized]

    if not full_path.is_file():
        raise FileNotFoundError(f"Standards file not found: {full_path}")

    return full_path.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dimension", nargs="?", help="Dimension to resolve")
    parser.add_argument("--list", action="store_true", help="List all dimensions")
    parser.add_argument("--batch", help="Comma-separated dimensions")

    args = parser.parse_args()

    if args.list:
        for dim in sorted(DIMENSIONS):
            print(dim)
        return 0

    if args.batch:
        for dim in args.batch.split(","):
            try:
                print(resolve_dimension(dim.strip()))
            except (ValueError, FileNotFoundError) as e:
                print(f"ERROR: {e}", file=sys.stderr)
                return 1
        return 0

    if not args.dimension:
        parser.print_help()
        return 1

    try:
        print(resolve_dimension(args.dimension))
        return 0
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
