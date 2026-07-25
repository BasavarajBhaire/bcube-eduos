#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OVERRIDES = ROOT / "bcube-publishing-sdk/books/learning-page-overrides-v1.json"
CONTRACT = ROOT / "bcube-publishing-sdk/contracts/learning-page-contract-v2.json"
PIPELINE = ROOT / "scripts/run_bcube_learning_pipeline.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_phase2.py"
CONSOLE = ROOT / "tools/publishing-console/templates/index.html"

PILOTS = {
    "EL-LKG-V4-P023",
    "CC-NURSERY-V4-P022",
    "CE-NURSERY-V4-P010",
    "YS-UKG-V4-P010",
    "CM-UKG-V4-P032",
}


class Phase2PilotTests(unittest.TestCase):
    def test_five_page_overrides_are_interactive_and_classroom_only(self) -> None:
        registry = json.loads(OVERRIDES.read_text(encoding="utf-8"))
        self.assertEqual(PILOTS, set(registry["pages"]))
        for page_id, page in registry["pages"].items():
            self.assertIn("phase2", page, page_id)
            self.assertFalse(page["phase2"]["parent_panel"], page_id)
            self.assertTrue(page["guidance"]["teacher"]["model"].strip(), page_id)
            self.assertTrue(page["learning"]["student_instruction"].strip(), page_id)
            self.assertTrue(page["deterministic_components"], page_id)
            self.assertNotIn("generic", page["learning"]["student_instruction"].casefold())

    def test_read_match_has_exact_word_picture_contract(self) -> None:
        page = json.loads(OVERRIDES.read_text(encoding="utf-8"))["pages"]["EL-LKG-V4-P023"]
        phase2 = page["phase2"]
        self.assertEqual(["cat", "sun", "bus", "cup"], phase2["main_words"])
        self.assertEqual(["pen", "dog", "hen"], phase2["small_words"])
        self.assertEqual({"cat", "sun", "bus", "cup", "pen", "dog", "hen"}, set(phase2["asset_crops"]))
        self.assertEqual(7, len(page["illustration"]["required_objects"]))

    def test_choice_layout_supports_phase2_speaking_and_observation(self) -> None:
        spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
        choice = spec["layout_variants"]["choice-circle"]
        self.assertIn("speak", choice["activities"])
        self.assertIn("observe", choice["activities"])
        self.assertIn("model_phrase", choice["allowed_component_types"])

    def test_pipeline_routes_to_phase2_composer(self) -> None:
        source = PIPELINE.read_text(encoding="utf-8")
        self.assertIn("compose_learning_page_phase2.py", source)
        self.assertTrue(COMPOSER.is_file())
        composer = COMPOSER.read_text(encoding="utf-8")
        for page_id in PILOTS:
            self.assertIn(page_id, composer)
        self.assertIn('"parent_panel":None', composer)

    def test_console_marks_phase2_and_hides_parent_panel(self) -> None:
        html = CONSOLE.read_text(encoding="utf-8")
        for page_id in PILOTS:
            self.assertIn(page_id, html)
        self.assertIn("PHASE 2 PILOT", html)
        self.assertIn("!lessonPage||phase2", html)


if __name__ == "__main__":
    unittest.main()
