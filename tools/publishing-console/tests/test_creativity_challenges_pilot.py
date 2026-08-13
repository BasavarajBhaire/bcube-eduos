from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BLUEPRINT = ROOT / "curriculum/creativity-challenges/lkg/curriculum-first-p008-p024-v1.json"
RENDERER = ROOT / "scripts/render_creativity_challenges_pilot.py"


class CreativityChallengesPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        cls.renderer = RENDERER.read_text(encoding="utf-8")

    def test_scope_is_exactly_p008_through_p032(self) -> None:
        expected = {f"CR-LKG-V4-P{number:03d}" for number in range(8, 33)}
        self.assertEqual(set(self.blueprint["pages"]), expected)

    def test_every_page_has_specific_child_and_teacher_guidance(self) -> None:
        for page_id, page in self.blueprint["pages"].items():
            with self.subTest(page_id=page_id):
                self.assertGreaterEqual(len(page["instruction"]), 35)
                self.assertGreaterEqual(len(page["teacher_cue"]), 45)
                self.assertNotIn("what did you notice", page["teacher_cue"].lower())
                self.assertNotIn("home", page["teacher_cue"].lower())
                self.assertNotIn("parent", page["teacher_cue"].lower())

    def test_each_page_uses_a_task_specific_renderer(self) -> None:
        for page_number in range(8, 33):
            with self.subTest(page_number=page_number):
                self.assertIn(f"def render_p{page_number:03d}", self.renderer)

    def test_pilot_has_models_and_open_child_response_areas(self) -> None:
        self.assertIn("COMPLETED", self.renderer)
        self.assertIn("EXAMPLE", self.renderer)
        self.assertIn("Finish the balloon", self.renderer)
        self.assertIn("Make your own repeating pattern", self.renderer)
        self.assertIn("Draw the toy and label two special parts", self.renderer)
        self.assertIn("Complete your dream house", self.renderer)
        self.assertIn("Make a repeating nature pattern", self.renderer)
        self.assertIn("Practise one mark", self.renderer)
        self.assertIn("Write 1, 2 and 3", self.renderer)
        self.assertIn("paper-plate puppet", self.renderer)
        self.assertIn("toy car needs to cross", self.renderer)
        self.assertIn("Draw your invention", self.renderer)
        self.assertIn("ASK: What is the problem?", self.renderer)
        self.assertIn("Choose three feelings", self.renderer)
        self.assertIn("four-beat movement pattern", self.renderer)
        self.assertNotIn("Parent", self.renderer)
        self.assertNotIn("Home Connection", self.renderer)


if __name__ == "__main__":
    unittest.main()
