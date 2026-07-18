from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from eduos.kernel.event_bus import EventBus
from eduos.kernel.runtime import EduOSRuntime, RuntimeFailure


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        (self.root / "assets").mkdir()
        asset_file = self.root / "assets" / "gold.txt"
        asset_file.write_text("gold", encoding="utf-8")

        import hashlib
        checksum = hashlib.sha256(asset_file.read_bytes()).hexdigest()

        self.templates = self.root / "templates.json"
        self.templates.write_text(json.dumps({
            "registry_version": "1.0.0",
            "status": "founder_locked",
            "templates": {
                "COVER_V1.0.0": {
                    "page_type": "cover",
                    "canvas": {"width_px": 2480, "height_px": 3508, "dpi": 300, "orientation": "portrait"},
                    "regions": {"hero": {"x": 100, "y": 100, "w": 1000, "h": 1000}},
                    "rules": {}
                }
            }
        }), encoding="utf-8")

        self.assets = self.root / "assets.json"
        self.assets.write_text(json.dumps({
            "registry_version": "1.0.0",
            "assets": [
                {
                    "asset_id": "TEST.GOLD.V1.0.0",
                    "family": "TEST",
                    "variant": "GOLD",
                    "version": "1.0.0",
                    "type": "BRAND",
                    "status": "GOLD",
                    "path": "assets/gold.txt",
                    "sha256": checksum,
                    "dependencies": []
                }
            ]
        }), encoding="utf-8")

    def manifest(self) -> dict:
        return {
            "identity": {"prompt_id": "TEST-P001"},
            "page": {"type": "cover", "title": "Test", "visible_text": [], "number": 0, "show_page_number": False},
            "composition": {"template": "COVER_V1.0.0"},
            "assets": {"logo": "TEST.GOLD.V1.0.0", "illustration": "TEST.GOLD.V1.0.0", "characters": []}
        }

    def test_duplicate_asset_reference_fails_closed(self) -> None:
        runtime = EduOSRuntime(self.root, self.templates, self.assets)
        with self.assertRaises(RuntimeFailure):
            runtime.preflight(self.manifest())

    def test_unknown_template_emits_failure_event(self) -> None:
        manifest = self.manifest()
        manifest["assets"] = {"logo": "TEST.GOLD.V1.0.0", "illustration": None, "characters": []}
        manifest["composition"]["template"] = "UNKNOWN_V1.0.0"
        bus = EventBus()
        runtime = EduOSRuntime(self.root, self.templates, self.assets, bus)
        with self.assertRaises(RuntimeFailure):
            runtime.preflight(manifest)
        self.assertIn("runtime.failed", [event.name for event in bus.history])


if __name__ == "__main__":
    unittest.main()
