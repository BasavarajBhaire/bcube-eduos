#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BLUEPRINT = ROOT / "curriculum/early-maths-adventures/lkg/curriculum-first-p009-p021-v1.json"
EARLY_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_early_maths_curriculum_first_v3.py"
LATE_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page_response_safe.py"
FULL_BOOK_RUNNER = ROOT / "scripts/render_early_maths_full_book_approved_assets_v2.py"


class EarlyMathsFullBookRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        cls.pages = cls.book["pages"]
        cls.early_source = EARLY_COMPOSER.read_text(encoding="utf-8")
        cls.late_source = LATE_COMPOSER.read_text(encoding="utf-8")
        cls.runner_source = FULL_BOOK_RUNNER.read_text(encoding="utf-8")

    def test_number_line_rows_start_at_zero(self):
        rows = self.pages["EM-LKG-V4-P018"]["renderer_controls"]["rows"]
        self.assertEqual([0, 0, 0], [row["start"] for row in rows])
        self.assertEqual([2, 4, 5], [row["landing"] for row in rows])

    def test_sparse_number_comparison_is_expanded(self):
        page = self.pages["EM-LKG-V4-P019"]
        self.assertEqual(6, len(page["renderer_controls"]["rows"]))
        self.assertEqual({"rows": 3, "columns": 2, "two_large_numerals_per_card": True}, page["layout"])
        self.assertIn("2 is less than 5", self.early_source)

    def test_second_math_story_visually_adds_the_third_ball(self):
        self.assertIn('story["asset"] == "story_balls"', self.early_source)
        self.assertIn("the third visible ball deterministically", self.early_source)

    def test_pattern_pages_have_child_response_boxes(self):
        self.assertIn("Draw the next item in the box", self.runner_source)
        self.assertIn('"Draw next:"', self.late_source)

    def test_directions_use_dots_not_a_completed_path(self):
        self.assertIn("for dot in range(10)", self.late_source)
        self.assertIn("route_endpoint_crops", self.late_source)
        self.assertNotIn("draw.line(route", self.late_source)

    def test_object_names_and_pattern_labels_are_child_readable(self):
        self.assertIn("def object_label", self.late_source)
        for label in (
            "apple - banana",
            "circle - triangle - triangle",
            "red cube - blue cube - green cube",
            "small star - big star",
        ):
            self.assertIn(label, self.late_source)

    def test_long_short_does_not_normalise_both_objects_to_same_width(self):
        self.assertIn('elif mechanic == "long-short"', self.late_source)
        self.assertIn("scaled_region(right_region, 0.58, bottom=False)", self.late_source)


if __name__ == "__main__":
    unittest.main()
