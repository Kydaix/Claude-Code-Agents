#!/usr/bin/env python3
"""Record a Codex in-app browser observation for Claude Code."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
from pathlib import Path


def read_optional_file(path: str | None) -> str | None:
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8-sig")


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-") or "browser-observation"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a codex_browser_observation JSON file after Codex uses the in-app browser."
    )
    parser.add_argument("--request-file", required=True, help="Browser request JSON emitted by Claude.")
    parser.add_argument("--summary", required=True, help="Concise visual/browser observation summary.")
    parser.add_argument("--url", help="Observed URL.")
    parser.add_argument("--title", help="Observed page title.")
    parser.add_argument("--screenshot", action="append", help="Path to screenshot evidence. Repeatable.")
    parser.add_argument("--dom-excerpt", help="Short DOM excerpt or visible text.")
    parser.add_argument("--dom-excerpt-file", help="File containing DOM excerpt or visible text.")
    parser.add_argument("--console-log-file", help="File containing relevant console logs.")
    parser.add_argument("--notes", action="append", help="Additional note. Repeatable.")
    parser.add_argument("--output", help="Observation JSON output path.")
    args = parser.parse_args()

    request_path = Path(args.request_file).resolve()
    request = json.loads(request_path.read_text(encoding="utf-8-sig"))
    request_id = str(request.get("request_id") or request_path.stem.replace(".request", ""))

    observation = {
        "type": "codex_browser_observation",
        "request_id": request_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source": "codex_in_app_browser",
        "request": request,
        "summary": args.summary,
        "url": args.url,
        "title": args.title,
        "screenshots": args.screenshot or [],
        "dom_excerpt": args.dom_excerpt or read_optional_file(args.dom_excerpt_file),
        "console_logs": read_optional_file(args.console_log_file),
        "notes": args.notes or [],
    }

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = request_path.with_name(f"{safe_name(request_id)}.observation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(observation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
