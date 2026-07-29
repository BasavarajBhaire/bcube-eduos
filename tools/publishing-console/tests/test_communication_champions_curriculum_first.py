from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "curriculum/communication-champions/lkg/phase2-page-audit-v1.json"
RUNTIME = ROOT / "runtime-contracts/lkg/communication-champions.json"
PROMPTS = ROOT / "production-prompts/communication-champions/lkg/v4/phase2-illustration-prompts.json"
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_communication_champions_curriculum_first.py"


class CommunicationChampionsCurriculumFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))

    def test_complete_scope(self):
        expected = {f"CC-LKG-V4-P{number:03d}" for number in range(8, 44)}
        self.assertEqual(expected, set(self.audit["pages"]))
        self.assertEqual(expected, set(self.runtime["pages"]))
        self.assertEqual(expected, set(self.prompts["pages"]))

    def test_every_page_is_response_safe(self):
        for page_id, page in self.runtime["pages"].items():
            self.assertFalse(page["layout"]["parent_panel"], page_id)
            self.assertFalse(page["layout"]["home_connection"], page_id)
            self.assertFalse(page["layout"]["generic_response_panel"], page_id)
            self.assertTrue(page["layout"]["independent_answers_unmarked"], page_id)
            self.assertFalse(page["validation"]["allow_fallback"], page_id)

    def test_prompt_assets_match_runtime_crops(self):
        for page_id, prompt in self.prompts["pages"].items():
            runtime = self.runtime["pages"][page_id]
            self.assertEqual(prompt["asset_names"], runtime["illustration"]["assets"], page_id)
            self.assertEqual(set(prompt["asset_names"]), set(runtime["illustration"]["asset_crops"]), page_id)
            self.assertIn("Exact child response path:", prompt["prompt"], page_id)
            self.assertIn("No asset may touch", prompt["prompt"], page_id)

    def test_page_specific_mechanics_are_preserved(self):
        pages = self.runtime["pages"]
        self.assertEqual(3, pages["CC-LKG-V4-P010"]["activity"]["mechanics"]["activity_count"])
        self.assertEqual(5, len(pages["CC-LKG-V4-P018"]["activity"]["mechanics"]["correct_pairs"]))
        self.assertEqual(4, pages["CC-LKG-V4-P033"]["activity"]["mechanics"]["writing_boxes"])
        self.assertTrue(pages["CC-LKG-V4-P035"]["activity"]["mechanics"]["drawing_box"])
        self.assertEqual(6, len(pages["CC-LKG-V4-P043"]["activity"]["mechanics"]["checks"]))

    def test_runtime_loader_accepts_every_page(self):
        spec = importlib.util.spec_from_file_location("communication_runtime_loader_test", LOADER)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        for page_id, page in self.runtime["pages"].items():
            module.validate_page_contract(page_id, page)

    def test_composer_has_task_specific_layouts(self):
        source = COMPOSER.read_text(encoding="utf-8")
        for function in ("render_match", "render_action_strips", "render_number_sequence", "render_scene_prompts", "render_retell", "render_journal", "render_certificate", "render_celebration"):
            self.assertIn(f"def {function}", source)
        self.assertIn("elif physical in {14,16,18}", source)
        self.assertIn("elif physical==10", source)
        self.assertIn("elif physical==34", source)
        self.assertIn("elif physical==43", source)


if __name__ == "__main__":
    unittest.main()
