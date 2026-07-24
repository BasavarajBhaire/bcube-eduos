from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/special-page-v1.json"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_special_page.py"
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"


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


class MeetStarFinalLockTests(unittest.TestCase):
    def test_template_locks_clear_gaps_and_compact_purpose_panel(self) -> None:
        template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        spec = template["meet_star"]
        self.assertEqual("page-type-contract-v1.3", template["template_version"])
        self.assertGreaterEqual(spec["star"][1] - spec["message"][3], 45)
        self.assertGreaterEqual(spec["purpose"][1] - spec["star"][3], 45)
        self.assertLessEqual(spec["purpose"][3] - spec["purpose"][1], 450)
        self.assertEqual(48, spec["purpose_text_max_px"])
        self.assertGreaterEqual(spec["purpose_text_min_px"], 32)

    def test_render_uses_larger_purpose_copy_and_measured_spacing(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            data_path = temporary / "meet-star.json"
            output = temporary / "meet-star.png"
            evidence_path = temporary / "meet-star-evidence.json"
            data = {
                "page_id": "AC-NURSERY-V4-P007",
                "page_type": "meet_star",
                "physical_page": 7,
                "page_number": 6,
                "book_title": "Art & Colour Fun",
                "book_title_lines": ["Art & Colour", "Fun"],
                "page_title": "Meet Star",
                "level": "Nursery",
                "tagline": "Colour • Create • Enjoy",
                "message": "Hello! I am Star, your friendly guide through Art & Colour Fun.",
                "purpose": (
                    "Together, we will explore colours, make art, and try new ideas. "
                    "I will help you create and celebrate every step."
                ),
                "core_pillars": [
                    "Creativity", "Communication", "Curiosity", "Confidence", "Collaboration"
                ],
                "footer_keywords": "Colour • Art • Expression • Imagination • Joy",
                "official_logo_path": official_asset("official_logo_candidates"),
                "official_star_path": official_asset("official_star_candidates"),
            }
            data_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(COMPOSER),
                    "--data",
                    str(data_path),
                    "--output",
                    str(output),
                    "--evidence-output",
                    str(evidence_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            purpose = evidence["components"]["purpose"]
            gaps = evidence["components"]["layout_gaps"]
            self.assertGreaterEqual(purpose["font_size"], 44)
            self.assertLessEqual(len(purpose["lines"]), 4)
            self.assertGreaterEqual(gaps["message_to_star"], gaps["minimum_message_to_star"])
            self.assertGreaterEqual(gaps["star_to_purpose"], gaps["minimum_star_to_purpose"])
            with Image.open(output) as rendered:
                self.assertEqual((2480, 3508), rendered.size)
                self.assertGreaterEqual(rendered.info.get("dpi", (0, 0))[0], 299)


if __name__ == "__main__":
    unittest.main()
