from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from page_composer import CompositionPreflightError, build_plan  # noqa: E402


class ComposerPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "assets").mkdir()
        for name in ("logo.png", "scene.png", "star.png"):
            (self.root / "assets" / name).write_bytes(name.encode("utf-8"))

        self.template_registry = self.root / "template-registry.json"
        self.template_registry.write_text(
            json.dumps(
                {
                    "registry_version": "1.0.0",
                    "status": "founder_locked",
                    "templates": {
                        "COVER_V1.0.0": {
                            "page_type": "cover",
                            "canvas": {
                                "width_px": 2480,
                                "height_px": 3508,
                                "dpi": 300,
                                "orientation": "portrait",
                            },
                            "regions": {
                                "logo": {"x": 100, "y": 100, "w": 400, "h": 180},
                                "title": {"x": 300, "y": 150, "w": 1880, "h": 250},
                                "hero": {"x": 180, "y": 500, "w": 2120, "h": 2400},
                            },
                            "rules": {"show_page_number": False},
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        def asset(asset_id: str, variant: str, filename: str) -> dict[str, object]:
            path = self.root / "assets" / filename
            return {
                "asset_id": asset_id,
                "family": asset_id.split(".")[0],
                "variant": variant,
                "version": "1.0.0",
                "type": "BRAND" if "LOGO" in asset_id else "CHARACTER",
                "status": "GOLD",
                "path": f"assets/{filename}",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "mime_type": "image/png",
                "dependencies": [],
            }

        self.asset_registry = self.root / "asset-registry.json"
        self.asset_registry.write_text(
            json.dumps(
                {
                    "registry_version": "1.0.0",
                    "assets": [
                        asset("LOGO_BCUBE.PRIMARY.V1.0.0", "PRIMARY", "logo.png"),
                        asset("COVER_SCENE.MAIN.V1.0.0", "MAIN", "scene.png"),
                        asset("STAR.WELCOME.V1.0.0", "WELCOME", "star.png"),
                    ],
                }
            ),
            encoding="utf-8",
        )

        self.manifest = {
            "identity": {"prompt_id": "TEST-P001"},
            "page": {
                "number": 0,
                "type": "cover",
                "title": "Test Cover",
                "visible_text": ["Test Cover"],
                "show_page_number": False,
            },
            "assets": {
                "logo": "LOGO_BCUBE.PRIMARY.V1.0.0",
                "illustration": "COVER_SCENE.MAIN.V1.0.0",
                "characters": ["STAR.WELCOME.V1.0.0"],
            },
            "composition": {"template": "COVER_V1.0.0", "background": "#FFFFFF"},
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def build(self) -> dict[str, object]:
        return build_plan(
            self.manifest,
            repository_root=self.root,
            template_registry_path=self.template_registry,
            asset_registry_path=self.asset_registry,
        )

    def test_all_dependencies_resolve_before_plan(self) -> None:
        plan = self.build()
        self.assertEqual(plan["template"]["template_id"], "COVER_V1.0.0")
        self.assertEqual(len(plan["resolved_assets"]), 3)

    def test_unknown_asset_rejects_composition(self) -> None:
        self.manifest["assets"]["illustration"] = "UNKNOWN.MAIN.V1.0.0"
        with self.assertRaises(CompositionPreflightError):
            self.build()

    def test_checksum_drift_rejects_composition(self) -> None:
        (self.root / "assets" / "logo.png").write_bytes(b"changed")
        with self.assertRaises(CompositionPreflightError):
            self.build()

    def test_unknown_template_rejects_composition(self) -> None:
        self.manifest["composition"]["template"] = "UNKNOWN_V1.0.0"
        with self.assertRaises(CompositionPreflightError):
            self.build()

    def test_page_type_mismatch_rejects_composition(self) -> None:
        self.manifest["page"]["type"] = "lesson"
        with self.assertRaises(CompositionPreflightError):
            self.build()

    def test_page_number_on_cover_rejects_composition(self) -> None:
        self.manifest["page"]["show_page_number"] = True
        with self.assertRaises(CompositionPreflightError):
            self.build()


if __name__ == "__main__":
    unittest.main()
