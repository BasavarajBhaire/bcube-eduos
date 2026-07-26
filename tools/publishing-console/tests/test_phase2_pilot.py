#!/usr/bin/env python3
from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OVERRIDES = ROOT / "bcube-publishing-sdk/books/learning-page-overrides-v1.json"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_phase2.py"
PIPELINE = ROOT / "scripts/run_bcube_learning_pipeline.py"

PAGES = {
    "EL-LKG-V4-P023",
    "CC-NURSERY-V4-P022",
    "CE-NURSERY-V4-P010",
    "ST-LKG-V4-P010",
    "CM-UKG-V4-P032",
    "AC-NURSERY-V4-P012",
}
SUPPORTED = {
    "A05 Read/Look & Match",
    "A05 Read / Look & Match",
    "A06 Sort & Classify",
    "A10 Speak, Listen & Respond",
    "A12 Observe, Find & Name",
}

class Phase2RolloutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(OVERRIDES.read_text(encoding="utf-8"))
        cls.composer = COMPOSER.read_text(encoding="utf-8")

    def test_required_pages_are_present(self):
        self.assertTrue(PAGES.issubset(set(self.registry["pages"])))

    def test_supported_pages_are_classroom_only(self):
        for page_id in PAGES:
            page = self.registry["pages"][page_id]
            self.assertFalse(page["phase2"]["parent_panel"], page_id)
            self.assertEqual("", page["guidance"]["parent_extension"], page_id)
            self.assertTrue(page["guidance"]["teacher"]["model"].strip(), page_id)
            self.assertTrue(page["learning"]["student_instruction"].strip(), page_id)
            self.assertTrue(page["phase2"]["asset_crops"], page_id)
            self.assertIn(page["phase2"]["archetype"], SUPPORTED, page_id)

    def test_straight_lines_uses_a12_scene_and_four_targets(self):
        phase2 = self.registry["pages"]["AC-NURSERY-V4-P012"]["phase2"]
        self.assertEqual("A12 Observe, Find & Name", phase2["archetype"])
        self.assertEqual(["ladder", "bench", "slide", "kite"], phase2["targets"])
        self.assertEqual({"scene", "ladder", "bench", "slide", "kite"}, set(phase2["asset_crops"]))

    def test_composer_routes_by_archetype_not_page_id(self):
        self.assertIn("SUPPORTED", self.composer)
        self.assertIn("arch in SUPPORTED", self.composer)
        self.assertNotIn("PILOT_IDS", self.composer)
        self.assertNotIn("page_id not in renderers", self.composer)

    def test_every_other_learning_page_uses_modern_rollout_not_legacy(self):
        self.assertIn("def compose_modern", self.composer)
        self.assertIn("render_modern_rollout", self.composer)
        self.assertIn("else: compose_modern", self.composer)
        self.assertNotIn("phase2_fallback", self.composer)
        self.assertNotIn("compose_learning_page_character_v2.py", self.composer)
        self.assertIn("'legacy_fallback_used':False", self.composer)

    def test_legacy_panels_are_explicitly_removed(self):
        self.assertIn("'parent_panel':None", self.composer)
        self.assertIn("'home_connection':None", self.composer)
        self.assertIn("'generic_say_or_tell':None", self.composer)
        self.assertIn("'home_connection_removed':True", self.composer)
        self.assertIn("'generic_say_or_tell_removed':True", self.composer)

    def test_modern_rollout_has_count_response(self):
        self.assertIn("if activity=='count'", self.composer)
        self.assertIn("Count each group. Circle the correct number.", self.composer)

    def test_pipeline_uses_phase2_composer(self):
        self.assertIn("compose_learning_page_phase2.py", PIPELINE.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
