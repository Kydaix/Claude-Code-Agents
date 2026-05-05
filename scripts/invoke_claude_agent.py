#!/usr/bin/env python3
"""Invoke Claude Code as a bounded non-interactive agent."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


SAFE_PERMISSION_MODES = {"default", "acceptEdits", "plan", "auto", "dontAsk"}


def split_csv(values: Iterable[str] | None) -> list[str]:
    items: list[str] = []
    for value in values or []:
        for part in value.split(","):
            item = part.strip()
            if item:
                items.append(item)
    return items


def read_text_argument(value: str | None, file_value: str | None, label: str) -> str | None:
    if value and file_value:
        raise SystemExit(f"Use either --{label} or --{label}-file, not both.")
    if file_value:
        return Path(file_value).read_text(encoding="utf-8")
    return value


def existing_directory(path: str) -> str:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_dir():
        raise argparse.ArgumentTypeError(f"Directory does not exist: {resolved}")
    return str(resolved)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Invoke Claude Code with safe defaults for Codex skill delegation."
    )
    parser.add_argument("prompt_arg", nargs="?", help="Prompt text. Prefer --prompt for clarity.")
    parser.add_argument("--prompt", help="Prompt text to send to Claude Code.")
    parser.add_argument("--prompt-file", help="UTF-8 file containing the prompt.")
    parser.add_argument("--cwd", default=os.getcwd(), type=existing_directory, help="Working directory for Claude.")
    parser.add_argument("--claude-bin", default=shutil.which("claude") or "claude", help="Path to claude executable.")
    parser.add_argument("--agent", help="Existing or dynamically loaded Claude Code agent name.")
    parser.add_argument("--agents-json", help="JSON string passed to Claude Code --agents.")
    parser.add_argument("--agents-file", help="Path to a JSON file passed to Claude Code --agents.")
    parser.add_argument("--model", help="Model alias or full Claude model name.")
    parser.add_argument("--allowed-tools", action="append", default=["Read,Grep,Glob"], help="Comma-separated or repeatable tool allow list.")
    parser.add_argument("--disallowed-tools", action="append", help="Comma-separated or repeatable tool deny list.")
    parser.add_argument("--permission-mode", default="dontAsk", choices=sorted(SAFE_PERMISSION_MODES))
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--max-budget-usd", type=float, default=None)
    parser.add_argument("--output-format", choices=["text", "json", "stream-json"], default="json")
    parser.add_argument("--json-schema", help="JSON schema string for structured output.")
    parser.add_argument("--json-schema-file", help="UTF-8 file containing a JSON schema.")
    parser.add_argument("--append-system-prompt", help="Additional system prompt text.")
    parser.add_argument("--append-system-prompt-file", help="File passed through to Claude Code.")
    parser.add_argument("--resume", help="Resume a session ID or named session.")
    parser.add_argument("--continue-session", action="store_true", help="Continue most recent conversation.")
    parser.add_argument("--name", help="Display name for the Claude Code session.")
    parser.add_argument("--no-bare", action="store_true", help="Do not pass --bare.")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true", help="Print the command as JSON without running it.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    prompt = read_text_argument(args.prompt, args.prompt_file, "prompt") or args.prompt_arg
    if not prompt:
        raise SystemExit("A prompt is required via --prompt, --prompt-file, or positional prompt.")

    schema = read_text_argument(args.json_schema, args.json_schema_file, "json-schema")
    agents = read_text_argument(args.agents_json, args.agents_file, "agents")

    claude_bin = shutil.which(args.claude_bin) if args.claude_bin == "claude" else args.claude_bin
    if not claude_bin or not Path(claude_bin).exists():
        raise SystemExit("Claude Code CLI was not found. Install and authenticate `claude` first.")

    if args.max_turns < 1:
        raise SystemExit("--max-turns must be at least 1.")
    if args.max_budget_usd is not None and args.max_budget_usd <= 0:
        raise SystemExit("--max-budget-usd must be positive.")

    cmd = [claude_bin]
    if not args.no_bare:
        cmd.append("--bare")
    cmd.extend(["-p", prompt, "--output-format", args.output_format])
    cmd.extend(["--permission-mode", args.permission_mode, "--max-turns", str(args.max_turns)])

    if args.max_budget_usd is not None:
        cmd.extend(["--max-budget-usd", str(args.max_budget_usd)])
    allowed_tools = split_csv(args.allowed_tools)
    if allowed_tools:
        cmd.extend(["--allowedTools", ",".join(allowed_tools)])
    disallowed_tools = split_csv(args.disallowed_tools)
    if disallowed_tools:
        cmd.extend(["--disallowedTools", ",".join(disallowed_tools)])
    if args.agent:
        cmd.extend(["--agent", args.agent])
    if agents:
        cmd.extend(["--agents", agents])
    if args.model:
        cmd.extend(["--model", args.model])
    if schema:
        cmd.extend(["--json-schema", schema])
    if args.append_system_prompt:
        cmd.extend(["--append-system-prompt", args.append_system_prompt])
    if args.append_system_prompt_file:
        cmd.extend(["--append-system-prompt-file", args.append_system_prompt_file])
    if args.resume:
        cmd.extend(["--resume", args.resume])
    if args.continue_session:
        cmd.append("--continue")
    if args.name:
        cmd.extend(["--name", args.name])

    if args.dry_run:
        print(json.dumps({"cwd": args.cwd, "command": cmd}, indent=2))
        return 0

    completed = subprocess.run(
        cmd,
        cwd=args.cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout_seconds,
        check=False,
    )

    if args.output_format == "json":
        try:
            payload = json.loads(completed.stdout) if completed.stdout.strip() else {}
        except json.JSONDecodeError:
            payload = {"raw_stdout": completed.stdout}
        payload.setdefault("exit_code", completed.returncode)
        if completed.stderr.strip():
            payload["stderr"] = completed.stderr
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
