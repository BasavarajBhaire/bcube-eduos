from __future__ import annotations

import json
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BLUEPRINT = ROOT / "curriculum/logical-thinking-adventures/lkg/curriculum-first-p008-p043-v1.json"
RUNTIME = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"
PROMPTS = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/phase2-illustration-prompts.json"
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_logical_thinking_curriculum_first.py"


class LogicalThinkingCurriculumFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        cls.pages = cls.book["pages"]

    def test_complete_scope(self):
        self.assertEqual({f"LT-LKG-V4-P{n:03d}" for n in range(8, 44)}, set(self.pages))

    def test_response_safe_global_rules(self):
        rules = self.book["global_rules"]
        self.assertFalse(rules["parent_panel"])
        self.assertFalse(rules["home_connection"])
        self.assertFalse(rules["generic_response_panel"])
        self.assertTrue(rules["isolated_object_names_visible"])
        self.assertTrue(rules["independent_answers_unmarked"])

    def test_high_value_pages_have_sufficient_activity_depth(self):
        self.assertEqual(6, len(self.pages["LT-LKG-V4-P009"]["renderer_controls"]["rows"]))
        self.assertEqual(6, len(self.pages["LT-LKG-V4-P010"]["renderer_controls"]["rows"]))
        self.assertEqual(6, len(self.pages["LT-LKG-V4-P011"]["renderer_controls"]["correct_pairs"]))
        self.assertEqual(6, len(self.pages["LT-LKG-V4-P012"]["renderer_controls"]["targets"]))
        self.assertEqual(5, self.pages["LT-LKG-V4-P015"]["renderer_controls"]["draw_boxes"])

    def test_sort_pages_have_real_number_writing_places(self):
        self.assertEqual(4, self.pages["LT-LKG-V4-P017"]["renderer_controls"]["number_writing_boxes_per_category"])
        self.assertEqual(3, self.pages["LT-LKG-V4-P018"]["renderer_controls"]["number_writing_boxes_per_category"])
        self.assertEqual(3, self.pages["LT-LKG-V4-P021"]["renderer_controls"]["number_writing_boxes_per_category"])

    def test_assessment_pages_do_not_show_model_answers(self):
        self.assertTrue(self.pages["LT-LKG-V4-P038"]["model_example"]["assessment_safe"])
        self.assertTrue(self.pages["LT-LKG-V4-P039"]["model_example"]["assessment_safe"])
        self.assertFalse(self.pages["LT-LKG-V4-P039"]["renderer_controls"]["completed_example"])

    def test_direction_and_position_controls_are_large_and_open(self):
        self.assertTrue(self.pages["LT-LKG-V4-P035"]["renderer_controls"]["paths_dotted_not_solid"])
        self.assertFalse(self.pages["LT-LKG-V4-P035"]["renderer_controls"]["show_solution"])
        self.assertGreaterEqual(self.pages["LT-LKG-V4-P024"]["renderer_controls"]["minimum_choice_circle_mm"], 18)
        self.assertGreaterEqual(self.pages["LT-LKG-V4-P025"]["renderer_controls"]["minimum_choice_circle_mm"], 22)

    def test_prompt_pack_matches_runtime(self):
        prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))["pages"]
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))["pages"]
        self.assertEqual(set(self.pages), set(prompts))
        for page_id in self.pages:
            self.assertEqual(runtime[page_id]["illustration"]["assets"], prompts[page_id]["asset_names"], page_id)
            self.assertIn("Exact child action:", prompts[page_id]["prompt"], page_id)

    def test_runtime_loader_accepts_every_page(self):
        spec = importlib.util.spec_from_file_location("logical_thinking_runtime_loader_test", LOADER)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        for page_id, page in runtime["pages"].items():
            module.validate_page_contract(page_id, page)

    def test_composer_keeps_tasks_complete_and_response_safe(self):
        source = COMPOSER.read_text(encoding="utf-8")
        self.assertIn("def render_picture_logic_p034", source)
        self.assertIn("def render_complete_puzzle_p033", source)
        self.assertIn("def render_thinking_challenge_p036", source)
        self.assertIn("def render_brain_challenge_p038", source)
        self.assertIn("row_boxes = (", source)
        self.assertIn("p039_boxes = (", source)
        self.assertIn("is_last_odd", source)
        self.assertIn("order_boxes = 3", source)
        self.assertIn("Trace each path to the matching food or home.", source)

    def test_selection_layouts_separate_prompt_from_choices(self):
        source = COMPOSER.read_text(encoding="utf-8")
        self.assertIn('text.fitted_text(draw, "LOOK"', source)
        self.assertIn('text.fitted_text(draw, "CHOOSE"', source)
        self.assertIn('page_id == "LT-LKG-V4-P013"', source)
        self.assertIn("main_boxes = (", source)
        self.assertIn("choice_boxes = (", source)

    def test_answer_positions_are_not_a_column_shortcut(self):
        source = COMPOSER.read_text(encoding="utf-8")
        self.assertIn("permutations = ((1, 0, 2), (1, 2, 0), (0, 2, 1), (2, 1, 0), (2, 0, 1), (0, 1, 2))", source)
        self.assertIn("permutations = ((0, 3, 1, 2), (1, 2, 3, 0), (3, 0, 1, 2)", source)

    def test_final_activity_repairs_are_deterministic(self):
        source = COMPOSER.read_text(encoding="utf-8")
        self.assertIn("def render_complete_series_p016", source)
        self.assertIn('"SERIES"', source)
        self.assertIn('"CHOOSE"', source)
        self.assertIn("Continue the dog and cat pattern. Circle what comes next.", source)
        self.assertIn("paste_fit_aligned(canvas, image, [x0 + 55, y0 + 145, centre, y0 + 555], align=\"right\", inset=0)", source)
        self.assertIn("Complete magnifying glass: no crop fragments", source)
        self.assertEqual("animal_pattern", self.pages["LT-LKG-V4-P038"]["renderer_controls"]["tasks"][0])


if __name__ == "__main__":
    unittest.main()
