from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import invoke_claude_agent


class InvokeClaudeAgentTests(unittest.TestCase):
    def test_split_csv_accepts_repeated_comma_separated_values(self) -> None:
        self.assertEqual(
            invoke_claude_agent.split_csv(["Read,Grep", " Glob ,,"]),
            ["Read", "Grep", "Glob"],
        )

    def test_compose_prompt_requires_prompt_without_observation(self) -> None:
        with self.assertRaises(SystemExit):
            invoke_claude_agent.compose_prompt(None, None)

    def test_compose_prompt_wraps_browser_observation_as_evidence(self) -> None:
        prompt = invoke_claude_agent.compose_prompt(
            "Continue.",
            '{"type":"codex_browser_observation","summary":"ok"}',
        )

        self.assertIn("Codex browser observation follows.", prompt)
        self.assertIn("Additional instruction:\nContinue.", prompt)

    def test_find_browser_request_from_fenced_json(self) -> None:
        request = invoke_claude_agent.find_browser_request_in_text(
            """Please inspect:
```codex-browser-request
{"type":"codex_browser_request","request_id":"home-page","url":"http://localhost:3000"}
```
"""
        )

        self.assertIsNotNone(request)
        self.assertEqual(request["request_id"], "home-page")

    def test_write_browser_request_sanitizes_generated_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = invoke_claude_agent.write_browser_request(
                {"type": "codex_browser_request", "request_id": "home page/../x"},
                cwd=tmp,
                bridge_dir=".bridge",
                output_path=None,
            )

            written = Path(path)
            self.assertTrue(written.is_file())
            self.assertEqual(written.parent, Path(tmp) / ".bridge")
            self.assertNotIn("/", written.name)
            self.assertEqual(
                json.loads(written.read_text(encoding="utf-8"))["request_id"],
                "home page/../x",
            )


if __name__ == "__main__":
    unittest.main()
