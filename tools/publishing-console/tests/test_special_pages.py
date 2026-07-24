from __future__ import annotations

import importlib.util
import json
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


def load_special_composer():
    spec = importlib.util.spec_from_file_location("bcube_special_composer", COMPOSER)
    if spec is None or spec.loader is None:
        raise AssertionError("Cannot load the special-page composer")
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
            "welcome": "Welcome!",
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
            welcome = next(
                item for item in evidence["components"]["module_groups"]["items"]
                if item.get("component") == "contents_entry" and item.get("physical") is None
                and item.get("page") == 5
            )
            self.assertEqual("Welcome!", welcome["title"])
            self.assertNotIn("illustration", evidence["components"])
            self.assertNotIn("official_star", evidence["components"])
            self.assertNotIn("teacher_panel", evidence["components"])
            self.assertNotIn("parent_panel", evidence["components"])

    def test_confidence_builders_contents_part_two_fits_long_module_heading(self) -> None:
        pipeline = load_front_matter_pipeline()
        with tempfile.TemporaryDirectory() as folder:
            data = common("contents", 5)
            data.update({
                "page_id": "CB-NURSERY-V4-P005",
                "physical_page": 5,
                "book_title": "Confidence Builders",
                "book_title_lines": ["Confidence", "Builders"],
                "page_title": "Contents — Part 2",
                "level": "Nursery",
                "tagline": "I Believe • I Can • I Will",
                "footer_keywords": "Self-belief • Courage • Expression • Kindness • Independence",
                "entries": pipeline.contents_entries("nursery", "confidence-builders", 5),
            })
            _, evidence, _ = self.render(data, Path(folder))
            groups = evidence["components"]["module_groups"]
            self.assertEqual(19, groups["entry_count"])
            long_heading = next(
                item for item in groups["items"]
                if item.get("module") == "Module 4 Independence And Responsibility"
                and item.get("component") == "module_heading"
            )
            self.assertEqual(1, len(long_heading["typography"]["lines"]))
            self.assertGreaterEqual(long_heading["typography"]["font_size"], 30)

    def test_all_sixty_registered_contents_pages_fit_the_locked_layout(self) -> None:
        pipeline = load_front_matter_pipeline()
        composer = load_special_composer()
        registry = json.loads(BOOKS.read_text(encoding="utf-8"))
        template = json.loads(
            (ROOT / "bcube-publishing-sdk/templates/special-page-v1.json").read_text(encoding="utf-8")
        )
        checked = 0
        for level_slug, level in registry["levels"].items():
            for book_slug, book in level["books"].items():
                for physical_page in (4, 5):
                    canvas = Image.new("RGB", (2480, 3508), "white")
                    result = composer.draw_contents(
                        ImageDraw.Draw(canvas),
                        {
                            "book_title": " ".join(book["title_lines"]),
                            "entries": pipeline.contents_entries(
                                level_slug, book_slug, physical_page
                            ),
                        },
                        template,
                    )
                    self.assertEqual(19, result["entry_count"])
                    checked += 1
        self.assertEqual(60, checked)

    def test_welcome_contents_entry_is_compact_and_matches_the_page_title(self) -> None:
        composer = load_special_composer()
        template = json.loads(
            (ROOT / "bcube-publishing-sdk/templates/special-page-v1.json").read_text(encoding="utf-8")
        )
        entries = [
            {
                "physical": physical,
                "title": "Welcome to My World & General Awareness" if physical == 6 else f"Page {page}",
                "page": page,
                "module": "FRONT_MATTER" if physical < 8 else "MODULE_ONE",
            }
            for physical, page in zip(range(6, 25), range(5, 24))
        ]
        result = composer.draw_contents(
            ImageDraw.Draw(Image.new("RGB", (2480, 3508), "white")),
            {"book_title": "My World & General Awareness", "entries": entries},
            template,
        )
        welcome = next(
            item for item in result["items"]
            if item.get("component") == "contents_entry" and item.get("page") == 5
        )
        self.assertEqual("Welcome!", welcome["title"])
        self.assertGreaterEqual(welcome["font_size"], template["contents"]["entry_min_px"])
        self.assertLessEqual(welcome["font_size"], template["contents"]["entry_max_px"])

    def test_welcome_trims_empty_canvas_and_meets_locked_occupancy(self) -> None:
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
                "message": "Let us mix colours, draw shapes, paint pictures, make crafts, and explore textures.",
                "illustration_path": str(illustration),
            })
            report, evidence, _ = self.render(data, temporary)
            self.assertTrue(report["visible_page_number"])
            illustration_evidence = evidence["components"]["illustration"]
            self.assertTrue(illustration_evidence["background_removed"])
            self.assertTrue(illustration_evidence["trimmed_to_visible_artwork"])
            self.assertGreaterEqual(
                illustration_evidence["visible_occupancy"],
                evidence["occupancy_gate"]["minimum"],
            )
            self.assertLess(illustration_evidence["source_crop"][0], illustration_evidence["source_crop"][2])
            self.assertNotIn("official_star", evidence["components"])
            self.assertNotIn("teacher_panel", evidence["components"])
            self.assertNotIn("parent_panel", evidence["components"])

    def test_meet_star_is_enlarged_and_uses_one_registered_asset(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            data = common("meet_star", 7)
            data.update({
                "page_number": 6,
                "message": "Hello! I am Star, your friendly guide through Art & Colour Fun.",
                "purpose": "Together, we will mix, draw, paint, craft, and explore textures. I will help you create and share your artwork.",
                "official_star_path": official_asset("official_star_candidates"),
            })
            report, evidence, _ = self.render(data, Path(folder))
            self.assertTrue(report["visible_page_number"])
            star = evidence["components"]["official_star"]
            self.assertTrue(star["trimmed_to_visible_artwork"])
            self.assertGreaterEqual(star["visible_occupancy"], evidence["occupancy_gate"]["minimum"])
            self.assertLess(star["rendered_bounds"][1], evidence["components"]["purpose"]["bounds"][1])
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
