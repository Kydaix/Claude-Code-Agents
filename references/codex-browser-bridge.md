# Codex Browser Bridge

Use this protocol when Claude Code needs visual or browser state that Codex can access through the Codex in-app browser.

## Why this exists

Claude Code can use external tools through MCP, but Codex's in-app browser is exposed inside the Codex app through the Browser plugin rather than as a public MCP server. Claude Code therefore cannot directly drive that browser. Codex must mediate browser actions and return observations.

## First Claude pass

Invoke Claude with browser bridge instructions:

```powershell
python <skill-dir>\scripts\invoke_claude_agent.py `
  --cwd <repo> `
  --codex-browser-bridge `
  --prompt "Review the checkout page visually and identify layout regressions." `
  --allowed-tools "Read,Grep,Glob" `
  --permission-mode dontAsk
```

If Claude needs browser evidence, the wrapper writes a request file under:

```text
<repo>/.claude-code-agents/browser-bridge/*.request.json
```

The JSON has this shape:

```json
{
  "type": "codex_browser_request",
  "request_id": "checkout-layout",
  "url": "http://localhost:3000/checkout",
  "reason": "Need rendered layout evidence",
  "actions": ["Navigate to checkout", "Inspect mobile layout"],
  "observations_needed": ["Screenshot summary", "Overflowing controls"],
  "success_criteria": ["Can decide whether layout regressed"],
  "safety_notes": "No login, secrets, or data submission"
}
```

## Codex browser pass

Codex, not Claude, opens the Browser plugin and performs only the requested safe browser actions. Prefer local development routes, file-backed pages, and public unauthenticated pages.

Record the result:

```powershell
python <skill-dir>\scripts\record_browser_observation.py `
  --request-file <request.json> `
  --url "http://localhost:3000/checkout" `
  --title "Checkout" `
  --summary "At 390px width, the primary button wraps to two lines but stays inside the card. No horizontal overflow observed." `
  --screenshot <optional-screenshot-path>
```

Include a textual visual summary. Screenshot paths are useful for audit trails, but the summary is the evidence Claude can reliably consume through the prompt.

## Resume Claude

Resume the same Claude session using the observation:

```powershell
python <skill-dir>\scripts\invoke_claude_agent.py `
  --cwd <repo> `
  --resume <session-id> `
  --codex-browser-bridge `
  --browser-observation-file <observation.json> `
  --prompt "Continue and give final recommendations."
```

Repeat for at most a small number of rounds. If the browser request needs authentication, secrets, destructive actions, payment, account settings, or external data submission, stop and ask the user.

## Source links

- Codex in-app browser: https://developers.openai.com/codex/app/browser
- Codex MCP configuration: https://developers.openai.com/codex/mcp
- Claude Code MCP: https://code.claude.com/docs/en/mcp
