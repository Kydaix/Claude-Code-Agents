from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import record_browser_observation


class RecordBrowserObservationTests(unittest.TestCase):
    def test_safe_name_removes_path_separators(self) -> None:
        self.assertEqual(
            record_browser_observation.safe_name("home page/../x"),
            "home-page-..-x",
        )

    def test_load_browser_request_rejects_non_request_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "observation.json"
            path.write_text('{"type":"codex_browser_observation"}', encoding="utf-8")

            with self.assertRaises(SystemExit):
                record_browser_observation.load_browser_request(path)

    def test_load_browser_request_accepts_codex_browser_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "request.json"
            path.write_text(
                json.dumps({"type": "codex_browser_request", "request_id": "home"}),
                encoding="utf-8",
            )

            request = record_browser_observation.load_browser_request(path)

            self.assertEqual(request["request_id"], "home")


if __name__ == "__main__":
    unittest.main()
