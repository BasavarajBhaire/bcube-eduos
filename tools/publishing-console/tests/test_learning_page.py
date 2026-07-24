from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_activity_inputs.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_activity_page.py"
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"


def official_logo() -> str:
    registry = json.loads(BOOKS.read_text(encoding="utf-8"))
    for candidate in registry["shared"]["official_logo_candidates"]:
        path = ROOT / candidate
        if path.is_file():
            try:
                with Image.open(path) as image:
                    image.verify()
                return candidate
            except OSError:
                pass
    raise AssertionError("No official logo is available")


class LearningPageTests(unittest.TestCase):
    def test_lesson_header_shows_book_identity_without_overlapping_default_star(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            illustration = temporary / "illustration.png"
            Image.new("RGB", (1200, 1000), "white").save(illustration, "PNG", dpi=(300, 300))
            data = {
                "page_id": "AC-LKG-V4-P008",
                "book_title": "Art & Colour Fun",
                "book_title_lines": ["Art & Colour", "Fun"],
                "level": "LKG",
                "age": "4+ Years",
                "page_number": 7,
                "activity_type": "colour",
                "title": "Primary Colours",
                "learning_objective": "Recognise red, yellow, and blue as primary colours.",
                "student_instruction": "Point to each primary colour and colour the matching objects.",
                "teacher_prompt": "Name each colour and invite the child to find a matching classroom object.",
                "parent_prompt": "Find one red, one yellow, and one blue object together at home.",
                "illustration_path": str(illustration),
                "official_logo_path": official_logo(),
            }
            data_path = temporary / "data.json"
            report_path = temporary / "report.json"
            evidence_path = temporary / "evidence.json"
            output = temporary / "page.png"
            data_path.write_text(json.dumps(data), encoding="utf-8")
            validation = subprocess.run(
                [sys.executable, str(VALIDATOR), "--data", str(data_path), "--output", str(report_path)],
                cwd=ROOT, check=False, capture_output=True, text=True,
            )
            self.assertEqual(0, validation.returncode, validation.stderr)
            composition = subprocess.run(
                [sys.executable, str(COMPOSER), "--data", str(data_path), "--output", str(output),
                 "--evidence-output", str(evidence_path)],
                cwd=ROOT, check=False, capture_output=True, text=True,
            )
            self.assertEqual(0, composition.returncode, composition.stderr)
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertIn("book_title", evidence["components"])
            self.assertEqual(["Art & Colour", "Fun"], evidence["components"]["book_title"]["coloured_segments"])
            self.assertEqual(["Art & Colour Fun"], evidence["components"]["book_title"]["lines"])
            self.assertIn("teacher_panel", evidence["components"])
            self.assertIn("parent_panel", evidence["components"])
            self.assertNotIn("star", evidence["components"])
            self.assertFalse(evidence["qa"]["panel_overlap"])
            with Image.open(output) as rendered:
                self.assertEqual((2480, 3508), rendered.size)


if __name__ == "__main__":
    unittest.main()
