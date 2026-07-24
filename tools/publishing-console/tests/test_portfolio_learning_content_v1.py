from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"
OVERRIDES = ROOT / "bcube-publishing-sdk/books/learning-page-overrides-v1.json"
NORMALIZER = ROOT / "bcube-publishing-sdk/normalizers/build_learning_contract_v2.py"
REFINER = ROOT / "bcube-publishing-sdk/normalizers/refine_learning_contract_v2.py"
FINALISER = ROOT / "bcube-publishing-sdk/normalizers/finalise_learning_contract_v2.py"
CONTENT_INDEX = ROOT / "bcube-publishing-sdk/books/learning-content-v1/index.json"

GENERIC_PHRASES = (
    "look carefully at the pictures. follow the model",
    "look at the simple model for an idea",
    "choose one example that shows your learning",
    "look at the model example. use the pictures",
    "study the model and visual clues",
    "follow the model slowly",
    "art activity discussion",
    "to be completed",
)


def load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise AssertionError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain an object")
    return value


def deep_merge(target: dict[str, Any], update: dict[str, Any]) -> None:
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = value


class PortfolioLearningContentV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.normalizer = load_module("portfolio_content_normalizer", NORMALIZER)
        cls.refiner = load_module("portfolio_content_refiner", REFINER)
        cls.finaliser = load_module("portfolio_content_finaliser", FINALISER)
        cls.registry = load(BOOKS)
        cls.overrides = load(OVERRIDES).get("pages", {})

    def manifest_path(self, level: str, slug: str) -> Path:
        candidates = (
            ROOT / "production-prompts" / slug / level / "v4" / "release-manifest.json",
            ROOT / "production-prompts" / slug / level / "V4" / "release-manifest.json",
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        self.fail(f"No V4 manifest for {level}/{slug}")

    def resolved_contracts(self):
        for level, level_data in self.registry["levels"].items():
            for slug, book in level_data["books"].items():
                manifest_path = self.manifest_path(level, slug)
                manifest = load(manifest_path)
                for page in manifest.get("pages", []):
                    physical = page.get("physical")
                    if not isinstance(physical, int) or not 8 <= physical <= 43:
                        continue
                    source_path = manifest_path.parent / page["json"]
                    contract = self.normalizer.build_contract(
                        root=ROOT,
                        v4_path=source_path,
                        illustration_path="PENDING_ILLUSTRATION",
                        official_logo_path="PENDING_OFFICIAL_LOGO",
                        book_title_lines=list(book["title_lines"]),
                        level_name=str(level_data["display_level"]),
                        age=str(level_data["age"]),
                    )
                    override = self.overrides.get(contract["identity"]["page_id"])
                    override_applied = isinstance(override, dict)
                    if override_applied:
                        deep_merge(contract, override)
                    self.refiner.refine_contract(
                        contract,
                        curated_override_applied=override_applied,
                    )
                    self.finaliser.finalise_contract(
                        contract,
                        curated_override_applied=override_applied,
                    )
                    yield contract

    def test_policy_index_locks_1080_pages(self) -> None:
        index = load(CONTENT_INDEX)
        self.assertEqual("portfolio-learning-content-v1.0", index["version"])
        self.assertEqual(1080, index["expected_total_pages"])
        self.assertEqual("LOCKED", index["status"])
        self.assertIn("learning.student_instruction", index["locked_fields"])
        self.assertIn("deterministic_components", index["locked_fields"])

    def test_all_1080_pages_have_locked_page_specific_content(self) -> None:
        contracts = list(self.resolved_contracts())
        self.assertEqual(1080, len(contracts))
        instructions: set[str] = set()
        for contract in contracts:
            identifier = contract["identity"]["page_id"]
            learning = contract["learning"]
            activity = contract["activity"]
            guidance = contract["guidance"]
            instruction = str(learning["student_instruction"])
            combined = " ".join(
                str(value or "")
                for value in (
                    learning.get("objective"),
                    instruction,
                    learning.get("expected_response"),
                    guidance.get("parent_extension"),
                )
            ).casefold()
            self.assertEqual("LOCKED", contract["content_status"], identifier)
            self.assertEqual(
                "portfolio-learning-content-v1.0",
                contract["source_lineage"]["portfolio_content_version"],
                identifier,
            )
            self.assertTrue(learning.get("objective"), identifier)
            self.assertTrue(instruction.endswith((".", "?", "!")), identifier)
            self.assertTrue(learning.get("expected_response"), identifier)
            for phrase in GENERIC_PHRASES:
                self.assertNotIn(phrase, combined, identifier)
            self.assertTrue(guidance["teacher"]["model"], identifier)
            self.assertTrue(guidance["teacher"]["question"], identifier)
            self.assertTrue(guidance["parent_extension"], identifier)
            self.assertTrue(contract["deterministic_components"], identifier)
            self.assertEqual(
                len(contract["deterministic_components"]),
                contract["qa_requirements"]["component_count"],
                identifier,
            )
            self.assertEqual("LOCKED", contract["qa_requirements"]["content_status"], identifier)
            self.assertIn(activity["layout_variant"], {
                "observe-speak", "trace-copy", "match-connect", "colour-draw",
                "count-compare", "sort-classify", "sequence-story", "choice-circle",
                "maze-path", "build-explore", "reflect-assess",
            }, identifier)
            instructions.add(instruction)
        self.assertGreaterEqual(len(instructions), 650)

    def test_reference_pages_keep_approved_content(self) -> None:
        contracts = {value["identity"]["page_id"]: value for value in self.resolved_contracts()}
        name = contracts["CC-NURSERY-V4-P008"]
        self.assertEqual("trace-copy", name["activity"]["layout_variant"])
        self.assertEqual("My name is ________.", name["learning"]["model_text"])
        self.assertEqual(
            ["model_phrase", "trace_line", "copy_line"],
            [item["type"] for item in name["deterministic_components"]],
        )
        self.assertEqual("official-asset-separate", name["illustration"]["star_policy"])

        colours = contracts["AC-LKG-V4-P008"]
        self.assertEqual("colour-draw", colours["activity"]["layout_variant"])
        self.assertIn("red, yellow, and blue", colours["learning"]["student_instruction"])
        self.assertEqual(
            ["model_example", "creative_response_area"],
            [item["type"] for item in colours["deterministic_components"]],
        )
        self.assertEqual("official-asset-separate", colours["illustration"]["star_policy"])


if __name__ == "__main__":
    unittest.main()
