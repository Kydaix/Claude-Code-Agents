---
name: claude-code-agents
description: Invoke Claude Code from Codex for bounded delegation to Claude Code agents or subagents. Use when the user explicitly asks to run, invoke, compare with, or delegate work to Claude Code; when a task should be checked by an external Claude Code reviewer; or when existing Claude Code subagents in .claude/agents should handle a task. Do not use for normal Codex-only coding unless Claude Code invocation is requested or clearly part of the workflow.
---

# Claude Code Agents

Use this skill to run Claude Code as an external non-interactive agent from Codex. Prefer a bounded, auditable call that returns JSON and summarizes only the useful result back to the user.

## Workflow

1. Confirm the target working directory and scope. If the user did not specify a directory, use the current project directory.
2. Decide whether Claude should be read-only or allowed to edit. Default to read-only unless the user explicitly asked Claude Code to modify files.
3. Build a concise prompt with the task, relevant files or commands, constraints, and the expected output shape.
4. Invoke the wrapper script instead of hand-building a shell command:

```powershell
python <skill-dir>\scripts\invoke_claude_agent.py `
  --cwd <project-dir> `
  --prompt "Review the staged diff for correctness risks. Return findings with file paths and line numbers." `
  --allowed-tools "Read,Grep,Glob" `
  --permission-mode dontAsk `
  --max-turns 4 `
  --max-budget-usd 1
```

5. Read Claude's output, compare it against local context when needed, and report only validated or clearly attributed results. Do not paste raw transcripts unless the user asks.

## Common Invocations

Read-only review:

```powershell
python <skill-dir>\scripts\invoke_claude_agent.py --cwd <repo> --prompt "Review this repository for likely test gaps. Do not modify files." --allowed-tools "Read,Grep,Glob" --permission-mode dontAsk
```

Allow edits with limited tools:

```powershell
python <skill-dir>\scripts\invoke_claude_agent.py --cwd <repo> --prompt "Fix the failing unit tests, then summarize changed files." --allowed-tools "Read,Edit,Bash(npm test *)" --permission-mode acceptEdits --max-turns 6
```

Use an existing Claude Code subagent:

```powershell
python <skill-dir>\scripts\invoke_claude_agent.py --cwd <repo> --agent code-reviewer --prompt "Review the current diff for regressions. Do not edit files."
```

Use a runtime agent definition:

```powershell
python <skill-dir>\scripts\invoke_claude_agent.py --cwd <repo> --agents-file .\agents.json --agent security-reviewer --prompt "Audit the auth changes for security issues."
```

## Prompt Shape

Use this structure for delegated prompts:

```text
Task: <single concrete task>
Scope: <files, diff, branch, issue, or command outputs to consider>
Constraints: <read-only/editing rules, commands allowed, time or budget limits>
Output: <short summary, findings list, patch summary, JSON schema, etc.>
```

If Claude is allowed to edit, tell it not to revert unrelated changes and to summarize changed paths.

## Guardrails

- Prefer `--bare` for scripted calls so user, project, and plugin discovery do not change behavior unexpectedly.
- Always set `--max-turns`; add `--max-budget-usd` for open-ended tasks.
- Use explicit `--allowedTools` and `--permission-mode`. Never use `--dangerously-skip-permissions` or `bypassPermissions` from this skill.
- Do not include secrets, API keys, passwords, or private tokens in prompts.
- Deny or avoid sensitive paths such as `.env`, `.env.*`, `secrets/**`, and credential files.
- For edits, run local verification yourself when practical. Treat Claude output as another agent's proposal, not as automatically correct.

## Resources

- Read `references/claude-code-cli.md` when exact Claude Code CLI behavior or source links matter.
- Use `scripts/invoke_claude_agent.py` for repeatable CLI invocation, dry runs, JSON output capture, and basic environment checks.
