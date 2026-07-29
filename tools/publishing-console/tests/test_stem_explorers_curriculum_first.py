from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BLUEPRINT = ROOT / "curriculum/stem-explorers/lkg/curriculum-first-p008-p043-v1.json"
PROMPTS = ROOT / "production-prompts/stem-explorers/lkg/v4/phase2-illustration-prompts.json"


class StemExplorersCurriculumFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        cls.prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))

    def test_scope_is_exactly_p008_through_p043(self) -> None:
        expected = {f"ST-LKG-V4-P{number:03d}" for number in range(8, 44)}
        self.assertEqual(set(self.blueprint["pages"]), expected)
        self.assertEqual(set(self.prompts["pages"]), expected)

    def test_generic_investigation_instruction_is_removed(self) -> None:
        for page_id, page in self.blueprint["pages"].items():
            with self.subTest(page_id=page_id):
                self.assertNotEqual(page["instruction"], "Investigation Discussion")
                self.assertGreaterEqual(len(page["instruction"]), 20)
                self.assertTrue(page["expected_response"])
                self.assertTrue(page["mechanic"])

    def test_response_safe_and_no_parent_panel(self) -> None:
        for page_id, page in self.blueprint["pages"].items():
            with self.subTest(page_id=page_id):
                self.assertFalse(page["parent_panel"])
                gates = " ".join(page["validation_gates"]).lower()
                self.assertIn("independent answers are unmarked", gates)
                self.assertIn("every box, circle, line and blank area", gates)

    def test_every_asset_has_a_content_aligned_prompt(self) -> None:
        for page_id, page in self.blueprint["pages"].items():
            with self.subTest(page_id=page_id):
                prompt = self.prompts["pages"][page_id]
                self.assertEqual(prompt["asset_names"], list(page["illustration_assets"]))
                self.assertIn(page["title"], prompt["prompt"])
                self.assertIn(page["instruction"], prompt["prompt"])
                self.assertNotIn("one dominant learning scene", prompt["prompt"].lower())

    def test_high_risk_pages_have_required_controls(self) -> None:
        pages = self.blueprint["pages"]
        self.assertEqual(pages["ST-LKG-V4-P010"]["renderer_controls"]["number_boxes_per_category"], 3)
        self.assertEqual(pages["ST-LKG-V4-P016"]["renderer_controls"]["columns"], ["PREDICT", "RESULT"])
        self.assertEqual(pages["ST-LKG-V4-P026"]["renderer_controls"]["grid"], [6, 6])
        self.assertTrue(pages["ST-LKG-V4-P040"]["renderer_controls"]["drawing_box"])


if __name__ == "__main__":
    unittest.main()
