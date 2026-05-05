# Claude Code Agents Skill

Codex skill for delegating bounded tasks to Claude Code through `claude -p`.

## Install with Vercel Skills

Install globally for Codex:

```bash
npx skills add Kydaix/Claude-Code-Agents --skill claude-code-agents --agent codex --global --yes
```

Install into the current project for Codex:

```bash
npx skills add Kydaix/Claude-Code-Agents --skill claude-code-agents --agent codex --yes
```

List the skill without installing:

```bash
npx skills add Kydaix/Claude-Code-Agents --list
```

## Requirements

- Claude Code CLI available as `claude`
- Python 3 for `scripts/invoke_claude_agent.py`
- Claude Code authentication or `ANTHROPIC_API_KEY`, depending on your Claude Code setup

## Quick Use

After installation, invoke the skill explicitly:

```text
Use $claude-code-agents to ask Claude Code to review the current diff without editing files.
```

## Codex In-App Browser Bridge

Claude Code cannot directly operate Codex's in-app browser. This skill supports a Codex-mediated bridge:

1. Run Claude with `--codex-browser-bridge`.
2. Claude can emit a structured `codex_browser_request`.
3. Codex uses its Browser plugin to inspect the rendered page.
4. Codex records a `codex_browser_observation`.
5. The wrapper resumes Claude with the observation.

Example first pass:

```bash
python scripts/invoke_claude_agent.py \
  --cwd . \
  --codex-browser-bridge \
  --prompt "Review the local checkout page visually. Request browser evidence if needed."
```

After Codex satisfies the request:

```bash
python scripts/invoke_claude_agent.py \
  --cwd . \
  --resume <session-id> \
  --codex-browser-bridge \
  --browser-observation-file .claude-code-agents/browser-bridge/<id>.observation.json
```
