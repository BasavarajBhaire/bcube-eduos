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
    "ST-LKG-V4-P010",
    "CM-UKG-V4-P032",
}


class Phase2PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(OVERRIDES.read_text(encoding="utf-8"))

    def test_five_page_overrides_are_interactive_and_classroom_only(self) -> None:
        self.assertEqual(PILOTS, set(self.registry["pages"]))
        for page_id, page in self.registry["pages"].items():
            self.assertIn("phase2", page, page_id)
            self.assertFalse(page["phase2"]["parent_panel"], page_id)
            self.assertTrue(page["guidance"]["teacher"]["model"].strip(), page_id)
            self.assertTrue(page["learning"]["student_instruction"].strip(), page_id)
            self.assertTrue(page["deterministic_components"], page_id)
            self.assertIsInstance(page["phase2"].get("asset_crops"), dict, page_id)
            self.assertTrue(page["phase2"]["asset_crops"], page_id)

    def test_read_match_uses_fully_displaced_picture_orders(self) -> None:
        page = self.registry["pages"]["EL-LKG-V4-P023"]
        phase2 = page["phase2"]
        self.assertTrue(phase2["require_full_derangement"])
        self.assertTrue(all(word != picture for word, picture in zip(phase2["main_words"], phase2["main_picture_order"])))
        self.assertTrue(all(word != picture for word, picture in zip(phase2["small_words"], phase2["small_picture_order"])))
        self.assertEqual({"cat","sun","bus","cup","pen","dog","hen"}, set(phase2["asset_crops"]))

    def test_i_can_speak_maps_uploaded_assets_one_to_one(self) -> None:
        phase2 = self.registry["pages"]["CC-NURSERY-V4-P022"]["phase2"]
        self.assertEqual({"model_scene","ball","toy car","teddy bear"}, set(phase2["asset_crops"]))
        self.assertEqual(["ball","toy car","teddy bear"], phase2["choices"])

    def test_observation_page_maps_scene_and_four_targets(self) -> None:
        phase2 = self.registry["pages"]["CE-NURSERY-V4-P010"]["phase2"]
        self.assertEqual({"scene","kite","bench","tree","flower"}, set(phase2["asset_crops"]))
        self.assertEqual(4, phase2["target_count"])

    def test_correct_stem_lkg_sort_page_is_used(self) -> None:
        page = self.registry["pages"]["ST-LKG-V4-P010"]
        phase2 = page["phase2"]
        self.assertEqual(["dog","tree","butterfly","rock","car","book"], phase2["items"])
        self.assertEqual(set(phase2["items"]), set(phase2["asset_crops"]))
        self.assertEqual(["Living","Non-living"], phase2["categories"])
        self.assertIn("Write its number", page["learning"]["student_instruction"])

    def test_creative_speaking_maps_all_uploaded_assets(self) -> None:
        phase2 = self.registry["pages"]["CM-UKG-V4-P032"]["phase2"]
        expected={"model_scene","dinosaur","rabbit","robot","meet a new friend","ask to join a game","share an exciting idea"}
        self.assertEqual(expected, set(phase2["asset_crops"]))
        self.assertTrue(phase2["partner_turn_required"])

    def test_choice_layout_supports_phase2_speaking_and_observation(self) -> None:
        spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
        choice = spec["layout_variants"]["choice-circle"]
        self.assertIn("speak", choice["activities"])
        self.assertIn("observe", choice["activities"])
        self.assertIn("model_phrase", choice["allowed_component_types"])

    def test_pipeline_routes_to_crop_only_phase2_composer(self) -> None:
        self.assertIn("compose_learning_page_phase2.py", PIPELINE.read_text(encoding="utf-8"))
        composer = COMPOSER.read_text(encoding="utf-8")
        for page_id in PILOTS:
            self.assertIn(page_id, composer)
        self.assertNotIn("def icon(", composer)
        self.assertIn("crop_assets", composer)
        self.assertIn('"generic_replacement_icons_removed":True', composer)
        self.assertIn('"named_asset_crop_manifest_used":True', composer)
        self.assertIn('"parent_panel":None', composer)

    def test_console_marks_correct_pilots_and_hides_parent_panel(self) -> None:
        html = CONSOLE.read_text(encoding="utf-8")
        for page_id in PILOTS:
            self.assertIn(page_id, html)
        self.assertNotIn("YS-UKG-V4-P010", html)
        self.assertIn("PHASE 2 PILOT", html)
        self.assertIn("!lessonPage||phase2", html)


if __name__ == "__main__":
    unittest.main()
