from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_about_inputs.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_about_page.py"
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"


def official_logo() -> str:
    registry = json.loads(BOOKS.read_text(encoding="utf-8"))
    for candidate in registry["shared"]["official_logo_candidates"]:
        path = ROOT / candidate
        if not path.is_file():
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            return candidate
        except OSError:
            continue
    raise AssertionError("No official logo is available for the About-page test")


def page_data(illustration: Path) -> dict:
    return {
        "page_id": "AC-NURSERY-V4-P002",
        "page_type": "about",
        "physical_page": 2,
        "book_title": "Art & Colour Fun",
        "book_title_lines": ["Art & Colour", "Fun"],
        "page_title": "About This Book",
        "level": "Nursery",
        "learning_objective": (
            "Introduce families and teachers to the purpose and learning journey of Art & Colour Fun."
        ),
        "overview": (
            "Read the short overview and use the book through guided play, conversation, and child response."
        ),
        "learning_outcomes": [
            "Explore Colours", "Hold Art Tools", "Make Simple Art",
            "Choose Colours", "Create Freely", "Enjoy Making",
        ],
        "core_pillars": [
            "Creativity", "Communication", "Curiosity", "Confidence", "Collaboration",
        ],
        "footer_keywords": "Colour • Art • Expression • Imagination • Joy",
        "illustration_path": str(illustration),
        "official_logo_path": official_logo(),
    }


class AboutPageTests(unittest.TestCase):
    def test_render_uses_book_header_and_excludes_lesson_components(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            illustration = temporary / "illustration.png"
            image = Image.new("RGB", (1200, 1000), "white")
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((120, 100, 1080, 900), radius=80, fill="#F8D7E8")
            image.save(illustration, "PNG", dpi=(300, 300))
            data_path = temporary / "data.json"
            output = temporary / "about.png"
            evidence_path = temporary / "evidence.json"
            report_path = temporary / "report.json"
            data_path.write_text(json.dumps(page_data(illustration)), encoding="utf-8")

            validation = subprocess.run(
                [sys.executable, str(VALIDATOR), "--data", str(data_path), "--output", str(report_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, validation.returncode, validation.stderr)
            composition = subprocess.run(
                [sys.executable, str(COMPOSER), "--data", str(data_path), "--output", str(output),
                 "--evidence-output", str(evidence_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, composition.returncode, composition.stderr)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual("PASS", report["status"])
            self.assertEqual("BOOK_HEADER", report["header_type"])
            self.assertFalse(report["visible_page_number"])
            self.assertEqual("BOOK_HEADER", evidence["header_type"])
            self.assertIn("book_title", evidence["components"])
            self.assertIn("page_title", evidence["components"])
            self.assertIn("learning_outcomes", evidence["components"])
            self.assertNotIn("teacher_panel", evidence["components"])
            self.assertNotIn("parent_panel", evidence["components"])
            self.assertNotIn("official_star", evidence["components"])
            self.assertEqual(0, evidence["prohibited_component_counts"]["visible_page_number"])
            with Image.open(output) as rendered:
                self.assertEqual((2480, 3508), rendered.size)
                self.assertGreaterEqual(rendered.info.get("dpi", (0, 0))[0], 299)

    def test_validator_rejects_teacher_or_parent_panel_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            illustration = temporary / "illustration.png"
            Image.new("RGB", (800, 800), "white").save(illustration)
            invalid = page_data(illustration)
            invalid["teacher_prompt"] = "This activity-only field must be rejected."
            data_path = temporary / "invalid.json"
            data_path.write_text(json.dumps(invalid), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--data", str(data_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("prohibited components", completed.stderr)


if __name__ == "__main__":
    unittest.main()
