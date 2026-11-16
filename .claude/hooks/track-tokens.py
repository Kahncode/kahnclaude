#!/usr/bin/env python3
"""
track-tokens.py — Log a session's token usage to ~/.claude/token-log.jsonl.

Event: SessionEnd
Matcher: *

Sums the `usage` of every assistant message in the session transcript and appends
one JSON line: timestamp, session_id, model, input/output/cache-read/cache-write tokens.
Never blocks: always exits 0 (problems are reported on stderr).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path.home() / ".claude" / "token-log.jsonl"
USAGE_FIELDS = {
    "input_tokens": "input_tokens",
    "output_tokens": "output_tokens",
    "cache_read_input_tokens": "cache_read_tokens",
    "cache_creation_input_tokens": "cache_write_tokens",
}


def sum_usage(transcript: Path) -> tuple[dict[str, int], str]:
    """Total the usage fields of assistant messages; return (totals, last model seen)."""
    totals = {name: 0 for name in USAGE_FIELDS.values()}
    model = ""
    with transcript.open(encoding="utf-8", errors="replace") as lines:
        for line in lines:
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(msg, dict) or msg.get("type") != "assistant":
                continue
            message = msg.get("message")
            usage = message.get("usage") if isinstance(message, dict) else None
            if not isinstance(usage, dict):
                continue
            for src, dst in USAGE_FIELDS.items():
                value = usage.get(src)
                totals[dst] += value if isinstance(value, int) else 0
            model = message.get("model") or model
    return totals, model


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError as err:
        print(f"track-tokens: bad hook input: {err}", file=sys.stderr)
        return 0
    transcript = Path(payload.get("transcript_path") or "")
    if not transcript.is_file():
        return 0
    try:
        totals, model = sum_usage(transcript)
        if totals["input_tokens"] == 0 and totals["output_tokens"] == 0:
            return 0
        entry = {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "session_id": payload.get("session_id", ""),
            "model": model,
            **totals,
        }
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except OSError as err:
        print(f"track-tokens: could not log usage for {transcript}: {err}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
