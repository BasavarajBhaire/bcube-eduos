import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eduos" / "src"))

from manifest_validator import validate_manifest  # noqa: E402
from page_composer import build_plan  # noqa: E402
from qa_engine import evaluate, WEIGHTS  # noqa: E402


class EduOSPhase1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "eduos" / "examples" / "communication-champions-cover.json"
        cls.manifest = json.loads(path.read_text(encoding="utf-8"))

    def test_manifest_is_valid(self):
        self.assertEqual(validate_manifest(self.manifest), [])

    def test_cover_has_no_page_number(self):
        self.assertFalse(self.manifest["page"]["show_page_number"])

    def test_composer_uses_a4_300dpi(self):
        plan = build_plan(self.manifest)
        self.assertEqual(plan["canvas"]["width"], 2480)
        self.assertEqual(plan["canvas"]["height"], 3508)
        self.assertEqual(plan["canvas"]["dpi"], 300)

    def test_composer_uses_exact_logo_asset(self):
        plan = build_plan(self.manifest)
        logo_layer = next(layer for layer in plan["layers"] if layer["kind"] == "logo")
        self.assertEqual(logo_layer["mode"], "exact_asset")

    def test_qa_requires_95_and_all_critical_checks(self):
        report = {
            "critical_checks": {
                "single_page": True,
                "correct_logo": True,
                "correct_identity": True,
                "exact_visible_text": True,
                "print_geometry": True,
                "no_invented_content": True,
            },
            "scores": dict(WEIGHTS),
        }
        passed, score, failures = evaluate(report)
        self.assertTrue(passed)
        self.assertEqual(score, 100)
        self.assertEqual(failures, [])

    def test_critical_failure_rejects_even_with_100_score(self):
        report = {
            "critical_checks": {
                "single_page": True,
                "correct_logo": False,
                "correct_identity": True,
                "exact_visible_text": True,
                "print_geometry": True,
                "no_invented_content": True,
            },
            "scores": dict(WEIGHTS),
        }
        passed, score, failures = evaluate(report)
        self.assertFalse(passed)
        self.assertEqual(score, 100)
        self.assertIn("critical:correct_logo", failures)


if __name__ == "__main__":
    unittest.main()
