from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from eduos.compiler.compiler import CompilationError, EducationalCompiler


class EducationalCompilationEngineTests(unittest.TestCase):
    def _fixture(self, root: Path, show_page_number: bool = False) -> tuple[Path, Path, Path]:
        asset_dir = root / "assets"
        asset_dir.mkdir()
        logo = asset_dir / "logo.png"
        illustration = asset_dir / "illustration.png"
        logo.write_bytes(b"logo")
        illustration.write_bytes(b"illustration")

        def digest(path: Path) -> str:
            return hashlib.sha256(path.read_bytes()).hexdigest()

        asset_registry = root / "asset-registry.json"
        asset_registry.write_text(json.dumps({
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
                    "sha256": digest(logo),
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
                    "sha256": digest(illustration),
                    "dependencies": [],
                },
            ],
        }), encoding="utf-8")

        template_registry = root / "template-registry.json"
        template_registry.write_text(json.dumps({
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
                        "logo": {"x": 100, "y": 80, "w": 320, "h": 140},
                        "title": {"x": 360, "y": 100, "w": 1700, "h": 240},
                        "hero": {"x": 180, "y": 500, "w": 2120, "h": 2400},
                        "page_number": {"x": 2200, "y": 3300, "w": 120, "h": 80},
                    },
                    "rules": {"show_page_number": False},
                }
            },
        }), encoding="utf-8")

        manifest = root / "page.json"
        manifest.write_text(json.dumps({
            "identity": {
                "prompt_id": "CC-NURSERY-V3-P001",
                "book": "Communication Champions",
                "level": "Nursery",
            },
            "page": {
                "number": 0,
                "type": "cover",
                "title": "Communication Champions",
                "visible_text": ["Communication Champions", "Nursery (3+)"],
                "show_page_number": show_page_number,
            },
            "assets": {
                "logo": "LOGO_BCUBE.PRIMARY.V1.0.0",
                "illustration": "SCENE.COVER.V1.0.0",
                "characters": [],
            },
            "composition": {"template": "COVER_V1.0.0"},
        }), encoding="utf-8")
        return manifest, template_registry, asset_registry

    def test_compiler_builds_page_object(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest, templates, assets = self._fixture(root)
            compiler = EducationalCompiler(root, templates, assets)
            result = compiler.compile(manifest)

            self.assertEqual(result.status, "COMPILED")
            self.assertEqual(result.page_object.canvas_width, 2480)
            self.assertEqual(result.page_object.canvas_height, 3508)
            self.assertEqual(result.page_object.dpi, 300)
            self.assertEqual(result.page_object.component("CC-NURSERY-V3-P001:logo").payload["asset_id"], "LOGO_BCUBE.PRIMARY.V1.0.0")
            self.assertEqual(result.page_object.component("CC-NURSERY-V3-P001:title").payload["text"], "Communication Champions")

    def test_cover_visible_page_number_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest, templates, assets = self._fixture(root, show_page_number=True)
            compiler = EducationalCompiler(root, templates, assets)
            with self.assertRaisesRegex(CompilationError, "cover page cannot display a page number"):
                compiler.compile(manifest)


if __name__ == "__main__":
    unittest.main()
