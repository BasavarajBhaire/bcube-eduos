#!/usr/bin/env python3
from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OVERRIDES = ROOT / "bcube-publishing-sdk/books/learning-page-overrides-v1.json"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_phase2.py"
RUNTIME_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"
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
        cls.runtime_composer = RUNTIME_COMPOSER.read_text(encoding="utf-8")

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

    def test_composer_routes_through_validated_runtime_contract(self):
        self.assertIn("RUNTIME_COMPOSER", self.composer)
        self.assertIn("compose_runtime_learning_page.py", self.composer)
        self.assertNotIn("PILOT_IDS", self.composer)
        self.assertNotIn("phase2_fallback", self.composer)

    def test_dispatcher_is_fail_closed_not_generic(self):
        self.assertIn("Fail-closed dispatcher", self.composer)
        self.assertIn("Runtime dispatch requires", self.composer)
        self.assertNotIn("compose_learning_page_character_v2.py", self.composer)
        self.assertNotIn("render_modern_rollout", self.composer)

    def test_runtime_rejects_legacy_panels(self):
        self.assertIn('("parent_panel", "home_connection", "generic_response_panel")', self.runtime_composer)
        self.assertIn("must be false", self.runtime_composer)

    def test_runtime_has_exact_mechanic_renderers(self):
        self.assertIn("dispatch = {", self.runtime_composer)
        self.assertIn('"count-choice-grid"', self.runtime_composer)
        self.assertIn('"fallback_used": False', self.runtime_composer)

    def test_pipeline_uses_phase2_composer(self):
        self.assertIn("compose_learning_page_phase2.py", PIPELINE.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
