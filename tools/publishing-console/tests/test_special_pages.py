from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_special_inputs.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_special_page.py"
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"
FRONT_MATTER_PIPELINE = ROOT / "scripts/run_bcube_front_matter_pipeline.py"


def load_front_matter_pipeline():
    spec = importlib.util.spec_from_file_location("bcube_front_matter_pipeline", FRONT_MATTER_PIPELINE)
    if spec is None or spec.loader is None:
        raise AssertionError("Cannot load front-matter pipeline")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def official_asset(key: str) -> str:
    registry = json.loads(BOOKS.read_text(encoding="utf-8"))
    for candidate in registry["shared"][key]:
        path = ROOT / candidate
        if not path.is_file():
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            return candidate
        except OSError:
            continue
    raise AssertionError(f"No valid registered asset for {key}")


def common(page_type: str, physical: int) -> dict:
    return {
        "page_id": f"AC-LKG-V4-P{physical:03d}",
        "page_type": page_type,
        "physical_page": physical,
        "book_title": "Art & Colour Fun",
        "book_title_lines": ["Art & Colour", "Fun"],
        "page_title": {
            "contents": "Contents — Part 1",
            "welcome": "Welcome",
            "meet_star": "Meet Star",
        }[page_type],
        "level": "LKG",
        "tagline": "Explore • Mix • Create",
        "core_pillars": ["Creativity", "Communication", "Curiosity", "Confidence", "Collaboration"],
        "footer_keywords": "Colour • Drawing • Painting • Craft • Creativity",
        "official_logo_path": official_asset("official_logo_candidates"),
    }


class SpecialPageTests(unittest.TestCase):
    def test_contents_assigns_front_matter_module_to_welcome_and_meet_star(self) -> None:
        pipeline = load_front_matter_pipeline()
        entries = pipeline.contents_entries("nursery", "communication-champions", 4)
        self.assertEqual(19, len(entries))
        self.assertEqual(["FRONT_MATTER", "FRONT_MATTER"], [entry["module"] for entry in entries[:2]])

    def render(self, data: dict, directory: Path) -> tuple[dict, dict, Path]:
        data_path = directory / f"{data['page_type']}.json"
        report_path = directory / f"{data['page_type']}-report.json"
        evidence_path = directory / f"{data['page_type']}-evidence.json"
        output = directory / f"{data['page_type']}.png"
        data_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
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
        with Image.open(output) as rendered:
            self.assertEqual((2480, 3508), rendered.size)
            self.assertGreaterEqual(rendered.info.get("dpi", (0, 0))[0], 299)
        return (
            json.loads(report_path.read_text(encoding="utf-8")),
            json.loads(evidence_path.read_text(encoding="utf-8")),
            output,
        )

    def test_contents_is_module_navigation_without_lesson_or_illustration_components(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            data = common("contents", 4)
            data["entries"] = [
                {
                    "physical": physical,
                    "title": "Welcome" if physical == 6 else f"Learning Page {printed}",
                    "page": printed,
                    "module": "FRONT_MATTER" if physical < 8 else "COLOUR_SKILLS",
                }
                for physical, printed in zip(range(6, 25), range(5, 24))
            ]
            report, evidence, _ = self.render(data, Path(folder))
            self.assertFalse(report["visible_page_number"])
            self.assertEqual(19, evidence["components"]["module_groups"]["entry_count"])
            self.assertNotIn("illustration", evidence["components"])
            self.assertNotIn("official_star", evidence["components"])
            self.assertNotIn("teacher_panel", evidence["components"])
            self.assertNotIn("parent_panel", evidence["components"])

    def test_welcome_uses_hero_illustration_without_star_or_lesson_panels(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            illustration = temporary / "welcome.png"
            image = Image.new("RGB", (1200, 1000), "white")
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((100, 80, 1100, 920), radius=80, fill="#DFF2FF")
            image.save(illustration, "PNG", dpi=(300, 300))
            data = common("welcome", 6)
            data.update({
                "page_number": 5,
                "message": "Welcome to a joyful journey of colour, drawing, painting, and making.",
                "illustration_path": str(illustration),
            })
            report, evidence, _ = self.render(data, temporary)
            self.assertTrue(report["visible_page_number"])
            self.assertIn("illustration", evidence["components"])
            self.assertNotIn("official_star", evidence["components"])
            self.assertNotIn("teacher_panel", evidence["components"])
            self.assertNotIn("parent_panel", evidence["components"])

    def test_meet_star_uses_one_registered_star_without_uploaded_illustration(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            data = common("meet_star", 7)
            data.update({
                "page_number": 6,
                "message": "Meet Star, your friendly guide for this colourful learning journey.",
                "purpose": "Star encourages you to explore, try, create, and share your artwork.",
                "official_star_path": official_asset("official_star_candidates"),
            })
            report, evidence, _ = self.render(data, Path(folder))
            self.assertTrue(report["visible_page_number"])
            self.assertIn("official_star", evidence["components"])
            self.assertNotIn("illustration", evidence["components"])
            self.assertEqual(1, evidence["prohibited_component_counts"]["official_star"])
            self.assertNotIn("teacher_panel", evidence["components"])
            self.assertNotIn("parent_panel", evidence["components"])

    def test_special_validator_rejects_lesson_panels(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            data = common("contents", 4)
            data["entries"] = [
                {"physical": physical, "title": f"Page {printed}", "page": printed, "module": "MODULE_ONE"}
                for physical, printed in zip(range(6, 25), range(5, 24))
            ]
            data["teacher_prompt"] = "This must not appear on Contents."
            data_path = Path(folder) / "invalid.json"
            data_path.write_text(json.dumps(data), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--data", str(data_path)],
                cwd=ROOT, check=False, capture_output=True, text=True,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("prohibited components", completed.stderr)


if __name__ == "__main__":
    unittest.main()
