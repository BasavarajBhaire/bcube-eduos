from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_publisher_inputs.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_publisher_page.py"
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
    raise AssertionError("No official logo is available for the Publisher-page test")


def page_data() -> dict:
    return {
        "page_id": "AC-NURSERY-V4-P003",
        "page_type": "publisher",
        "physical_page": 3,
        "book_title": "Art & Colour Fun",
        "book_title_lines": ["Art & Colour", "Fun"],
        "page_title": "Publication & Copyright",
        "level": "Nursery",
        "publisher": {
            "name": "BCube Future Academy",
            "address": "407, DSMAX Sky Supreme, KST, Bangalore - 560060",
            "email": "info@bcubefutureacademy.in",
            "website": "bcubefutureacademy.in",
            "phone": "+91 79750 59945",
            "copyright_year": 2026,
            "production_status": "PILOT",
            "country_of_print": "India",
        },
        "publication_code": "BCUBE-NUR-AC-001",
        "document_id": "AC-NURSERY-PILOT-2026",
        "copyright_notice": "© 2026 BCube Future Academy. All rights reserved.",
        "official_logo_path": official_logo(),
    }


class PublisherPageTests(unittest.TestCase):
    def test_render_is_clean_administrative_page_without_illustration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            data_path = temporary / "data.json"
            output = temporary / "publisher.png"
            evidence_path = temporary / "evidence.json"
            report_path = temporary / "report.json"
            data_path.write_text(json.dumps(page_data()), encoding="utf-8")

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
            self.assertEqual("MINIMAL_HEADER", report["header_type"])
            self.assertFalse(report["illustration_required"])
            self.assertEqual("MINIMAL_HEADER", evidence["header_type"])
            self.assertIn("publisher_details", evidence["components"])
            self.assertIn("identifiers", evidence["components"])
            self.assertIn("copyright_notice", evidence["components"])
            for component in (
                "illustration_layer", "official_star", "learning_goal",
                "activity_banner", "teacher_panel", "parent_panel", "isbn",
            ):
                self.assertEqual(0, evidence["prohibited_component_counts"][component])
            with Image.open(output) as rendered:
                self.assertEqual((2480, 3508), rendered.size)
                self.assertGreaterEqual(rendered.info.get("dpi", (0, 0))[0], 299)

    def test_validator_rejects_illustration_or_lesson_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            invalid = page_data()
            invalid["illustration_path"] = "artwork.png"
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
