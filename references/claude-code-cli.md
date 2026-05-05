# Claude Code CLI Notes

Verified on 2026-05-05 from current Anthropic and OpenAI documentation.

## Sources

- Anthropic Claude Code programmatic usage: https://code.claude.com/docs/en/headless
- Anthropic Claude Code CLI reference: https://code.claude.com/docs/en/cli-reference
- Anthropic Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Anthropic Claude Code settings and permissions: https://code.claude.com/docs/en/settings
- OpenAI Codex skills: https://developers.openai.com/codex/skills

## Operational Facts

- `claude -p` or `claude --print` runs Claude Code non-interactively and exits.
- `--bare` is recommended for scripted calls because it skips automatic discovery of hooks, skills, plugins, MCP servers, auto memory, and CLAUDE.md.
- `--output-format json` returns structured output with a text result and metadata; `stream-json` returns newline-delimited events.
- `--json-schema` can request validated structured output in the `structured_output` field when used with JSON output.
- `--allowedTools` pre-approves specific tools or permission-rule patterns such as `Read`, `Edit`, or `Bash(git diff *)`.
- `--permission-mode` accepts modes including `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, and `bypassPermissions`; this skill must not use `bypassPermissions`.
- `--max-turns` limits agentic turns in print mode; use it for all delegated calls.
- `--max-budget-usd` limits spend for a print-mode run.
- `--agent` can select a Claude Code agent for a session. `--agents` can load custom agent definitions as JSON.
- Project subagents live under `.claude/agents/`; user subagents live under `~/.claude/agents/`.
- In `-p` mode, interactive slash commands and user-invoked Claude skills are not available; describe the task directly instead.
- Claude Code can connect to external tools through MCP, including local stdio servers, but Codex's in-app browser is not documented as a public MCP server. Use the Codex browser bridge protocol when Claude needs Codex-only browser observations.

## Recommended Defaults

Use these defaults unless the user or task requires otherwise:

```text
--bare
--output-format json
--permission-mode dontAsk
--allowedTools Read,Grep,Glob
--max-turns 4
```

For editing tasks, use explicit write permissions and a small tool list:

```text
--permission-mode acceptEdits
--allowedTools Read,Edit,Bash(<specific command pattern>)
```
