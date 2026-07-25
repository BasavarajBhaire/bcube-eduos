#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "tools/publishing-console/app.py"
HTML = ROOT / "tools/publishing-console/templates/index.html"


def load_app_module():
    spec = importlib.util.spec_from_file_location("bcube_console_storage_test", APP)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {APP}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StructuredPageStorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_app_module()

    def test_existing_selectors_define_page_storage_path(self) -> None:
        path = self.module.safe_storage_path(
            self.module.STRUCTURED_PAGES,
            "nursery",
            "communication-champions",
            "CC-NURSERY-V4-P022",
            ".png",
        )
        self.assertEqual(
            self.module.ROOT / "production-renders/pages-by-level/Nursery/communication-champions/CC-NURSERY-V4-P022.png",
            path,
        )

    def test_existing_selectors_define_illustration_storage_path(self) -> None:
        path = self.module.safe_storage_path(
            self.module.STRUCTURED_ILLUSTRATIONS,
            "lkg",
            "stem-explorers",
            "ST-LKG-V4-P010",
            ".png",
        )
        self.assertEqual(
            self.module.ROOT / "production-renders/illustrations-by-level/LKG/stem-explorers/ST-LKG-V4-P010.png",
            path,
        )

    def test_approved_archetype_activity_set_is_locked(self) -> None:
        self.assertEqual({"match", "sort", "speak", "observe"}, self.module.APPROVED_ARCHETYPE_ACTIVITIES)

    def test_html_reuses_existing_level_book_page_selectors(self) -> None:
        html = HTML.read_text(encoding="utf-8")
        self.assertIn('select name="level" id="level"', html)
        self.assertIn('select name="book" id="book"', html)
        self.assertIn('select name="physical_page" id="physicalPage"', html)
        self.assertNotIn("Direct path mode", html)
        self.assertIn("structured_output_path", html)
        self.assertIn("filename must match Page ID", html)


if __name__ == "__main__":
    unittest.main()
