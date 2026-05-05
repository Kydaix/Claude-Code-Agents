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
