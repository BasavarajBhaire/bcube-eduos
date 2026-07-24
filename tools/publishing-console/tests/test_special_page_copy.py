from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"
COPY_REGISTRY = ROOT / "bcube-publishing-sdk/books/special-page-copy-v1.json"
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
        cls.copy_registry = json.loads(COPY_REGISTRY.read_text(encoding="utf-8"))

    def production_copy(self, value: dict[str, str]) -> dict[str, str]:
        return {
            **value,
            "content_source": "locked_special_page_copy_registry",
            "content_policy_version": "special-pages-v1.2",
        }

    def test_confidence_social_skills_uses_refined_locked_copy(self) -> None:
        welcome = self.pipeline.welcome_copy("lkg", "confidence-social-skills")
        star = self.pipeline.meet_star_copy(
            "Confidence & Social Skills", "lkg", "confidence-social-skills"
        )
        self.assertEqual("Welcome!", welcome["page_title"])
        self.assertEqual(
            "Let us speak with confidence, make friends, share, take turns, and grow together.",
            welcome["message"],
        )
        self.assertEqual("Meet Star", star["page_title"])
        self.assertEqual(
            "Hello! I am Star, your friendly guide through Confidence & Social Skills.",
            star["message"],
        )
        self.assertEqual(
            "Together, we will speak with confidence, make kind choices, understand our feelings, "
            "and solve small problems.",
            star["purpose"],
        )

    def test_curiosity_explorers_uses_the_approved_meet_star_tone(self) -> None:
        star = self.pipeline.meet_star_copy(
            "Curiosity Explorers", "nursery", "curiosity-explorers"
        )
        self.assertEqual(
            "Together, we will ask questions, look closely, explore, and discover. "
            "I will help you try, think, and celebrate every step.",
            star["purpose"],
        )

    def test_all_thirty_books_have_unique_curated_non_placeholder_copy(self) -> None:
        checked = 0
        welcome_messages: set[str] = set()
        star_purposes: set[str] = set()
        registered_pairs = {
            (level_slug, book_slug)
            for level_slug, level in self.registry["levels"].items()
            for book_slug in level["books"]
        }
        copy_pairs = {
            (level_slug, book_slug)
            for level_slug, books in self.copy_registry["levels"].items()
            for book_slug in books
        }
        self.assertEqual(registered_pairs, copy_pairs)
        self.assertEqual("special-pages-v1.2", self.copy_registry["copy_version"])
        for level_slug, level in self.registry["levels"].items():
            for book_slug, book in level["books"].items():
                title = " ".join(book["title_lines"])
                welcome = self.pipeline.welcome_copy(level_slug, book_slug)
                star = self.pipeline.meet_star_copy(title, level_slug, book_slug)
                combined = " ".join((*welcome.values(), *star.values())).casefold()
                self.assertEqual("Welcome!", welcome["page_title"])
                self.assertEqual("Meet Star", star["page_title"])
                self.assertIn(title.casefold(), star["message"].casefold())
                self.assertLessEqual(len(welcome["message"]), 130)
                self.assertLessEqual(len(star["purpose"]), 150)
                for placeholder in PLACEHOLDER_TEXT:
                    self.assertNotIn(placeholder, combined)
                welcome_messages.add(welcome["message"])
                star_purposes.add(star["purpose"])
                checked += 1
        self.assertEqual(30, checked)
        self.assertEqual(30, len(welcome_messages))
        self.assertEqual(30, len(star_purposes))

    def test_validator_rejects_legacy_welcome_placeholder(self) -> None:
        with self.assertRaisesRegex(ValueError, "placeholder copy"):
            self.validator.validate_locked_copy(
                {
                    "page_title": "Welcome!",
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
        welcome = self.production_copy(
            self.pipeline.welcome_copy("lkg", "confidence-social-skills")
        )
        star = self.production_copy(
            self.pipeline.meet_star_copy(
                "Confidence & Social Skills", "lkg", "confidence-social-skills"
            )
        )
        self.validator.validate_locked_copy(welcome, "welcome")
        self.validator.validate_locked_copy(star, "meet_star")

    def test_validator_rejects_repeated_welcome_title_in_locked_contract(self) -> None:
        data = self.production_copy(
            self.pipeline.welcome_copy("lkg", "confidence-social-skills")
        )
        data["page_title"] = "Welcome to Confidence & Social Skills"
        with self.assertRaisesRegex(ValueError, "exactly 'Welcome!'"):
            self.validator.validate_locked_copy(data, "welcome")


if __name__ == "__main__":
    unittest.main()
