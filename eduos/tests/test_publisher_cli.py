from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from eduos.kernel.runtime import RuntimeResult
from eduos.publisher.cli import publish_manifest


class PublisherCliTests(unittest.TestCase):
    def test_publish_manifest_returns_runtime_contract(self) -> None:
        manifest = {
            "identity": {"prompt_id": "TEST-P001"},
            "page": {"type": "cover"},
            "assets": {"logo": "LOGO.TEST.V1.0.0", "illustration": "ILLUSTRATION.TEST.V1.0.0"},
            "composition": {"template": "COVER_V1.0.0"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            runtime_result = RuntimeResult(
                status="PREFLIGHT_PASSED",
                prompt_id="TEST-P001",
                template_id="COVER_V1.0.0",
                assets=("LOGO.TEST.V1.0.0", "ILLUSTRATION.TEST.V1.0.0"),
                plan={"canvas": {}},
                events=("manifest.loaded", "composition.preflight_passed"),
            )
            with patch("eduos.publisher.cli.EduOSRuntime") as runtime_type:
                runtime_type.return_value.preflight.return_value = runtime_result
                result = publish_manifest(manifest_path, root)

        self.assertEqual(result["status"], "PREFLIGHT_PASSED")
        self.assertEqual(result["prompt_id"], "TEST-P001")
        self.assertEqual(result["template_id"], "COVER_V1.0.0")
        self.assertEqual(len(result["asset_ids"]), 2)


if __name__ == "__main__":
    unittest.main()
