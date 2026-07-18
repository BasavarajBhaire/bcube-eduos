from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from eduos.compiler.compiler import CompilationError, EducationalCompiler


class CompilerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "eduos/registries").mkdir(parents=True)
        (self.root / "assets").mkdir()

        logo = self.root / "assets/logo.png"
        illustration = self.root / "assets/illustration.png"
        logo.write_bytes(b"logo")
        illustration.write_bytes(b"illustration")

        template_registry = {
            "registry_version": "1.0.0",
            "status": "founder_locked",
            "templates": {
                "COVER_V1.0.0": {
                    "page_type": "cover",
                    "canvas": {"width_px": 2480, "height_px": 3508, "dpi": 300, "orientation": "portrait"},
                    "regions": {"title": {"x": 100, "y": 100, "w": 1000, "h": 200}},
                    "rules": {"show_page_number": False},
                }
            },
        }
        (self.root / "eduos/registries/template-registry.json").write_text(json.dumps(template_registry), encoding="utf-8")

        assets = {
            "registry_version": "1.0.0",
            "assets": [
                {
                    "asset_id": "LOGO_BCUBE.PRIMARY.V1.0.0",
                    "family": "LOGO_BCUBE",
                    "variant": "PRIMARY",
                    "version": "1.0.0",
                    "type": "BRAND",
                    "status": "GOLD",
                    "path": "assets/logo.png",
                    "sha256": hashlib.sha256(b"logo").hexdigest(),
                    "dependencies": [],
                },
                {
                    "asset_id": "SCENE.COVER.V1.0.0",
                    "family": "SCENE",
                    "variant": "COVER",
                    "version": "1.0.0",
                    "type": "SCENE",
                    "status": "GOLD",
                    "path": "assets/illustration.png",
                    "sha256": hashlib.sha256(b"illustration").hexdigest(),
                    "dependencies": [],
                },
            ],
        }
        (self.root / "eduos/registries/asset-registry.json").write_text(json.dumps(assets), encoding="utf-8")

        self.manifest = self.root / "page.json"
        self.manifest.write_text(json.dumps({
            "identity": {"prompt_id": "CC-NURSERY-V3-P001", "book": "Communication Champions", "level": "Nursery"},
            "page": {"type": "cover", "title": "Communication Champions", "visible_text": ["Communication Champions"]},
            "composition": {"template": "COVER_V1.0.0"},
            "assets": {"logo": "LOGO_BCUBE.PRIMARY.V1.0.0", "illustration": "SCENE.COVER.V1.0.0", "characters": []},
        }), encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_compiles_verified_page_to_plan(self) -> None:
        result = EducationalCompiler(self.root).compile(self.manifest)
        self.assertEqual("COMPILED", result.status)
        self.assertEqual("COVER_V1.0.0", result.plan.template_id)
        self.assertEqual(2, len(result.verified_assets))

    def test_rejects_non_gold_asset(self) -> None:
        path = self.root / "eduos/registries/asset-registry.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["assets"][0]["status"] = "REVIEW"
        path.write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaises(CompilationError):
            EducationalCompiler(self.root).compile(self.manifest)


if __name__ == "__main__":
    unittest.main()
