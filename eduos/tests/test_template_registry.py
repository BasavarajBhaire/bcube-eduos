import json
import tempfile
import unittest
from pathlib import Path

from eduos.src.template_registry import TemplateRegistry, TemplateRegistryError


REGISTRY = Path("eduos/registries/template-registry.json")


class TemplateRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = TemplateRegistry(REGISTRY)

    def test_cover_template_resolves_locked_geometry(self) -> None:
        template = self.registry.resolve("COVER_V1.0.0")
        self.assertEqual(template["canvas"]["width_px"], 2480)
        self.assertEqual(template["canvas"]["height_px"], 3508)
        self.assertFalse(template["rules"]["page_number_allowed"])
        self.assertEqual(template["rules"]["logo_mode"], "approved_asset_only")

    def test_child_template_inherits_lesson_regions(self) -> None:
        template = self.registry.resolve("TRACE_V1.0.0")
        self.assertIn("hero", template["regions"])
        self.assertIn("activity", template["regions"])
        self.assertEqual(template["rules"]["activity_kind"], "tracing")
        self.assertEqual(template["rules"]["max_activities"], 1)

    def test_unknown_template_fails_closed(self) -> None:
        with self.assertRaises(TemplateRegistryError):
            self.registry.resolve("UNKNOWN_V1.0.0")

    def test_unversioned_template_reference_is_rejected(self) -> None:
        with self.assertRaises(TemplateRegistryError):
            self.registry.resolve("COVER")

    def test_inheritance_cycle_is_rejected(self) -> None:
        payload = {
            "registry_version": "1.0.0",
            "status": "founder_locked",
            "templates": {
                "A_V1.0.0": {"page_type": "a", "extends": "B_V1.0.0", "rules": {}},
                "B_V1.0.0": {"page_type": "b", "extends": "A_V1.0.0", "rules": {}},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            registry = TemplateRegistry(path)
            with self.assertRaises(TemplateRegistryError):
                registry.resolve("A_V1.0.0")


if __name__ == "__main__":
    unittest.main()
