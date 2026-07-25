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
CE_SOURCE = ROOT / "production-prompts/curiosity-explorers/nursery/v4/pages/CE-NURSERY-V4-P010-what-do-you-see.json"
ST_SOURCE = ROOT / "production-prompts/stem-explorers/lkg/v4/pages/ST-LKG-V4-P010-living-and-non-living.json"

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
            phase2 = page["phase2"]
            self.assertFalse(phase2["parent_panel"], page_id)
            self.assertTrue(page["guidance"]["teacher"]["model"].strip(), page_id)
            self.assertTrue(page["learning"]["student_instruction"].strip(), page_id)
            self.assertTrue(page["deterministic_components"], page_id)
            self.assertTrue(phase2.get("asset_layout"), page_id)
            self.assertIsInstance(phase2.get("asset_crops"), dict, page_id)
            self.assertTrue(phase2["asset_crops"], page_id)

    def test_read_match_uses_fully_displaced_picture_orders(self) -> None:
        phase2 = self.registry["pages"]["EL-LKG-V4-P023"]["phase2"]
        self.assertTrue(phase2["require_full_derangement"])
        self.assertTrue(all(word != picture for word, picture in zip(phase2["main_words"], phase2["main_picture_order"])))
        self.assertTrue(all(word != picture for word, picture in zip(phase2["small_words"], phase2["small_picture_order"])))
        self.assertEqual({"cat","sun","bus","cup","pen","dog","hen"}, set(phase2["asset_crops"]))

    def test_i_can_speak_uses_standard_hero_stack_layout(self) -> None:
        phase2 = self.registry["pages"]["CC-NURSERY-V4-P022"]["phase2"]
        self.assertEqual("hero-left-stack-right-v1", phase2["asset_layout"])
        self.assertEqual({"model_scene","ball","toy car","teddy bear"}, set(phase2["asset_crops"]))

    def test_observation_page_uses_standard_scene_target_strip(self) -> None:
        phase2 = self.registry["pages"]["CE-NURSERY-V4-P010"]["phase2"]
        self.assertEqual("hero-top-four-bottom-v1", phase2["asset_layout"])
        self.assertEqual({"scene","kite","bench","tree","flower"}, set(phase2["asset_crops"]))
        source = json.loads(CE_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(["scene","kite","bench","tree","flower"], source["phase2"]["asset_order"])
        self.assertIn("upper 64%", source["illustration_asset_prompt"])

    def test_living_non_living_uses_standard_six_asset_grid(self) -> None:
        page = self.registry["pages"]["ST-LKG-V4-P010"]
        phase2 = page["phase2"]
        self.assertEqual("grid-3x2-v1", phase2["asset_layout"])
        self.assertEqual(["dog","tree","butterfly","rock","car","book"], phase2["items"])
        self.assertEqual(set(phase2["items"]), set(phase2["asset_crops"]))
        source = json.loads(ST_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(phase2["items"], source["phase2"]["asset_order"])
        self.assertIn("strict three-column by two-row grid", source["illustration_asset_prompt"])
        self.assertIn("Write its number", page["learning"]["student_instruction"])

    def test_creative_speaking_uses_separated_three_band_layout(self) -> None:
        phase2 = self.registry["pages"]["CM-UKG-V4-P032"]["phase2"]
        self.assertEqual("hero-three-three-v1", phase2["asset_layout"])
        expected={"model_scene","dinosaur","rabbit","robot","meet a new friend","ask to join a game","share an exciting idea"}
        self.assertEqual(expected, set(phase2["asset_crops"]))
        for name in phase2["situations"]:
            self.assertGreaterEqual(phase2["asset_crops"][name][1], 0.66)

    def test_choice_layout_supports_phase2_speaking_and_observation(self) -> None:
        spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
        choice = spec["layout_variants"]["choice-circle"]
        self.assertIn("speak", choice["activities"])
        self.assertIn("observe", choice["activities"])
        self.assertIn("model_phrase", choice["allowed_component_types"])

    def test_sort_classify_allows_numbered_response_boxes(self) -> None:
        spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
        sort_layout = spec["layout_variants"]["sort-classify"]
        self.assertIn("sort_bins", sort_layout["required_component_types"])
        self.assertIn("number_response_boxes", sort_layout["allowed_component_types"])
        components = self.registry["pages"]["ST-LKG-V4-P010"]["deterministic_components"]
        self.assertEqual(["sort_bins", "number_response_boxes"], [item["type"] for item in components])

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
