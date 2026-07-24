from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"
FRONT_MATTER_PIPELINE = ROOT / "scripts/run_bcube_front_matter_pipeline.py"
SPECIAL_VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_special_inputs.py"
PLACEHOLDER_TEXT = (
    "use the page for its stated front-matter purpose",
    "no additional worksheet task",
    "introduce the page purpose clearly",
    "use this page for orientation only",
    "one dominant learning scene",
    "one dominant focus for",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpecialPageCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pipeline = load_module("bcube_front_matter_copy", FRONT_MATTER_PIPELINE)
        cls.validator = load_module("bcube_special_copy_validator", SPECIAL_VALIDATOR)
        cls.registry = json.loads(BOOKS.read_text(encoding="utf-8"))

    def test_confidence_social_skills_uses_meaningful_locked_copy(self) -> None:
        book = self.registry["levels"]["lkg"]["books"]["confidence-social-skills"]
        title = "Confidence & Social Skills"
        welcome = self.pipeline.welcome_copy(title, book)
        star = self.pipeline.meet_star_copy(title, book)
        self.assertEqual("Welcome to Confidence & Social Skills", welcome["page_title"])
        self.assertEqual(
            "Let us learn to speak confidently, make friends, take turns, manage feelings, "
            "solve conflicts, and celebrate progress.",
            welcome["message"],
        )
        self.assertEqual("Meet Star", star["page_title"])
        self.assertIn("Hello! I am Star", star["message"])
        self.assertIn("speak confidently, make friends, take turns, and manage feelings", star["purpose"])

    def test_all_thirty_books_generate_book_specific_non_placeholder_copy(self) -> None:
        checked = 0
        welcome_messages: set[str] = set()
        star_purposes: set[str] = set()
        for level in self.registry["levels"].values():
            for book in level["books"].values():
                title = " ".join(book["title_lines"])
                first_skill = str(book["skills"][0]).lower()
                welcome = self.pipeline.welcome_copy(title, book)
                star = self.pipeline.meet_star_copy(title, book)
                combined = " ".join((*welcome.values(), *star.values())).casefold()
                self.assertEqual(f"Welcome to {title}", welcome["page_title"])
                self.assertIn(first_skill, welcome["message"].casefold())
                self.assertIn(first_skill, star["purpose"].casefold())
                self.assertIn(title.casefold(), star["message"].casefold())
                for placeholder in PLACEHOLDER_TEXT:
                    self.assertNotIn(placeholder, combined)
                welcome_messages.add(welcome["message"])
                star_purposes.add(star["purpose"])
                checked += 1
        self.assertEqual(30, checked)
        self.assertGreaterEqual(len(welcome_messages), 27)
        self.assertGreaterEqual(len(star_purposes), 27)

    def test_validator_rejects_legacy_welcome_placeholder(self) -> None:
        with self.assertRaisesRegex(ValueError, "placeholder copy"):
            self.validator.validate_locked_copy(
                {
                    "page_title": "Welcome to Confidence & Social Skills",
                    "message": "Use the page for its stated front-matter purpose. No additional worksheet task.",
                },
                "welcome",
            )

    def test_validator_rejects_legacy_meet_star_placeholder(self) -> None:
        with self.assertRaisesRegex(ValueError, "placeholder copy"):
            self.validator.validate_locked_copy(
                {
                    "page_title": "Meet Star",
                    "message": "Hello! I am Star.",
                    "purpose": "Use this page for orientation only.",
                },
                "meet_star",
            )

    def test_validator_accepts_locked_generated_copy(self) -> None:
        book = self.registry["levels"]["lkg"]["books"]["confidence-social-skills"]
        title = "Confidence & Social Skills"
        welcome = self.pipeline.welcome_copy(title, book)
        star = self.pipeline.meet_star_copy(title, book)
        self.validator.validate_locked_copy(welcome, "welcome")
        self.validator.validate_locked_copy(star, "meet_star")


if __name__ == "__main__":
    unittest.main()
