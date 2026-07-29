#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BLUEPRINT = ROOT / "curriculum/early-literacy-adventures/lkg/curriculum-first-p008-p043-v1.json"
RUNTIME = ROOT / "runtime-contracts/lkg/early-literacy-adventures.json"
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"
PROMPTS = ROOT / "production-prompts/early-literacy-adventures/lkg/v4/phase2-illustration-prompts.json"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_early_literacy_curriculum_first.py"
WAVE1 = ROOT / "scripts/render_early_literacy_wave1.py"
WAVE2 = ROOT / "scripts/render_early_literacy_wave2.py"
WAVE3 = ROOT / "scripts/render_early_literacy_wave3.py"
WAVE4 = ROOT / "scripts/render_early_literacy_wave4.py"


class EarlyLiteracyCurriculumFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        cls.pages = cls.book["pages"]

    def test_complete_learning_and_closing_scope(self):
        expected = {f"EL-LKG-V4-P{number:03d}" for number in range(8, 44)}
        self.assertEqual(expected, set(self.pages))

    def test_no_parent_or_generic_panel(self):
        rules = self.book["global_rules"]
        self.assertFalse(rules["parent_panel"])
        self.assertFalse(rules["home_connection"])
        self.assertFalse(rules["generic_response_panel"])
        self.assertTrue(rules["isolated_object_names_visible"])

    def test_every_page_has_exact_mechanics_and_teacher_cue(self):
        for page_id, page in self.pages.items():
            self.assertTrue(page["mechanic"], page_id)
            self.assertTrue(page["render_kind"], page_id)
            self.assertTrue(page["renderer_controls"], page_id)
            self.assertTrue(page["teacher_cue"], page_id)
            self.assertGreaterEqual(len(page["validation_gates"]), 3, page_id)

    def test_read_match_keeps_proven_phase2_content(self):
        page = self.pages["EL-LKG-V4-P023"]
        controls = page["renderer_controls"]
        self.assertEqual(["cat", "sun", "bus", "cup"], controls["main_words"])
        self.assertEqual(["cup", "bus", "cat", "sun"], controls["main_picture_order"])
        self.assertTrue(controls["require_full_derangement"])

    def test_observation_repairs_add_depth_and_response_space(self):
        self.assertEqual(6, len(self.pages["EL-LKG-V4-P012"]["renderer_controls"]["cards"]))
        self.assertEqual(5, len(self.pages["EL-LKG-V4-P014"]["renderer_controls"]["rows"]))
        self.assertEqual(5, len(self.pages["EL-LKG-V4-P015"]["renderer_controls"]["rows"]))
        self.assertEqual(6, len(self.pages["EL-LKG-V4-P020"]["renderer_controls"]["correct_pairs"]))
        self.assertEqual(3, self.pages["EL-LKG-V4-P022"]["renderer_controls"]["number_writing_boxes_per_category"])
        self.assertEqual(6, len(self.pages["EL-LKG-V4-P032"]["renderer_controls"]["tasks"]))

    def test_replacement_sound_pages_do_not_reuse_picture_sets(self):
        same_sound = set(self.pages["EL-LKG-V4-P014"]["illustration_assets"])
        odd_sound = set(self.pages["EL-LKG-V4-P015"]["illustration_assets"])
        self.assertFalse(same_sound & odd_sound)

    def test_sentence_builder_has_explicit_crop_mapping(self):
        page = self.pages["EL-LKG-V4-P026"]
        self.assertEqual(set(page["illustration_assets"]), set(page["asset_crop_overrides"]))
        self.assertGreaterEqual(page["asset_crop_overrides"]["bus_scene"]["w"], 0.5)

    def test_composer_renders_child_readable_object_names(self):
        source = COMPOSER.read_text(encoding="utf-8")
        self.assertIn("def draw_asset_name", source)
        self.assertIn("readable_asset_name", source)

    def test_assessments_do_not_reveal_model_answers(self):
        for page_id in ("EL-LKG-V4-P038", "EL-LKG-V4-P039"):
            self.assertTrue(self.pages[page_id]["model_example"]["assessment_safe"])

    def test_runtime_loader_accepts_every_page(self):
        spec = importlib.util.spec_from_file_location("early_literacy_runtime_loader_test", LOADER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        for page_id, page in runtime["pages"].items():
            module.validate_page_contract(page_id, page)

    def test_illustration_prompt_pack_matches_runtime_assets(self):
        prompt_pack = json.loads(PROMPTS.read_text(encoding="utf-8"))
        runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        self.assertEqual(set(self.pages), set(prompt_pack["pages"]))
        for page_id, prompt_page in prompt_pack["pages"].items():
            runtime_page = runtime["pages"][page_id]
            self.assertEqual(runtime_page["illustration"]["assets"], prompt_page["asset_names"], page_id)
            self.assertEqual(runtime_page["illustration"]["asset_crops"], prompt_page["asset_crops"], page_id)
            if prompt_page["status"] == "READY_FOR_ILLUSTRATION":
                self.assertIn("Exact child action:", prompt_page["prompt"], page_id)
                self.assertIn("No visible words", prompt_page["prompt"], page_id)

    def test_first_wave_has_exact_renderer_dispatch(self):
        source = COMPOSER.read_text(encoding="utf-8")
        for page_id in (f"EL-LKG-V4-P{number:03d}" for number in range(8, 18)):
            render_kind = self.pages[page_id]["render_kind"]
            self.assertIn(render_kind, source, page_id)
        self.assertIn("Exact Early Literacy renderer not implemented yet", source)

    def test_wave1_runner_fails_closed(self):
        source = WAVE1.read_text(encoding="utf-8")
        self.assertIn("P008-P017", source)
        self.assertIn("Missing approved illustration", source)
        self.assertIn("no generic fallback", source)

    def test_second_wave_has_exact_renderer_dispatch(self):
        source = COMPOSER.read_text(encoding="utf-8")
        for page_id in (f"EL-LKG-V4-P{number:03d}" for number in range(18, 28)):
            render_kind = self.pages[page_id]["render_kind"]
            self.assertIn(render_kind, source, page_id)

    def test_wave2_runner_fails_closed(self):
        source = WAVE2.read_text(encoding="utf-8")
        self.assertIn("P018-P027", source)
        self.assertIn("Missing approved illustration", source)
        self.assertIn("no generic fallback", source)

    def test_third_wave_has_exact_renderer_dispatch(self):
        source = COMPOSER.read_text(encoding="utf-8")
        for page_id in (f"EL-LKG-V4-P{number:03d}" for number in range(28, 38)):
            render_kind = self.pages[page_id]["render_kind"]
            self.assertIn(render_kind, source, page_id)

    def test_wave3_runner_fails_closed(self):
        source = WAVE3.read_text(encoding="utf-8")
        self.assertIn("P028-P037", source)
        self.assertIn("Missing approved illustration", source)
        self.assertIn("no generic fallback", source)

    def test_fourth_wave_has_exact_renderer_dispatch(self):
        source = COMPOSER.read_text(encoding="utf-8")
        for page_id in (f"EL-LKG-V4-P{number:03d}" for number in range(38, 44)):
            render_kind = self.pages[page_id]["render_kind"]
            self.assertIn(render_kind, source, page_id)

    def test_wave4_runner_fails_closed(self):
        source = WAVE4.read_text(encoding="utf-8")
        self.assertIn("P038-P043", source)
        self.assertIn("Missing approved illustration", source)
        self.assertIn("no generic fallback", source)


if __name__ == "__main__":
    unittest.main()
