from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NORMALIZER = ROOT / "bcube-publishing-sdk/normalizers/build_learning_contract_v2.py"
PIPELINE = ROOT / "scripts/run_bcube_learning_pipeline.py"
VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_learning_contract_v2.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_character_v2.py"
BOOKS = ROOT / "bcube-publishing-sdk/books/cover-books.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def asset(key: str) -> Path:
    registry = json.loads(BOOKS.read_text(encoding="utf-8"))
    for candidate in registry["shared"][key]:
        path = ROOT / candidate
        if path.is_file():
            try:
                with Image.open(path) as image:
                    image.verify()
                return path
            except OSError:
                continue
    raise AssertionError(f"No valid registered asset for {key}")


def sample_illustration(path: Path) -> None:
    image = Image.new("RGB", (1400, 1100), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((120, 100, 1280, 1000), radius=80, fill="#DFF2FF")
    draw.ellipse((260, 180, 760, 680), fill="#FFD54F", outline="#5B3C88", width=16)
    draw.rectangle((820, 250, 1190, 880), fill="#B9E6B1", outline="#1768B3", width=14)
    image.save(path, "PNG", dpi=(300, 300))


class LearningPageContractV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.normalizer = load_module("learning_normalizer_v2", NORMALIZER)
        cls.pipeline = load_module("learning_pipeline_v2", PIPELINE)
        cls.validator = load_module("learning_validator_v2", VALIDATOR)
        cls.composer = load_module("learning_composer_character_v2", COMPOSER)
        cls.registry = json.loads(BOOKS.read_text(encoding="utf-8"))
        cls.logo = asset("official_logo_candidates")
        cls.star = asset("official_star_candidates")

    def build_contract(
        self,
        source: Path,
        illustration: Path,
        *,
        title_lines: list[str],
        level: str,
        age: str,
    ) -> dict:
        contract = self.normalizer.build_contract(
            root=ROOT,
            v4_path=source,
            illustration_path=str(illustration),
            official_logo_path=str(self.logo),
            book_title_lines=title_lines,
            level_name=level,
            age=age,
        )
        self.pipeline.apply_curated_override(contract)
        self.pipeline.normalise_star_policy(contract, self.star)
        return contract

    def render(self, contract: dict, folder: Path) -> tuple[dict, dict, Path]:
        contract_path = folder / "contract.json"
        report_path = folder / "report.json"
        evidence_path = folder / "evidence.json"
        output = folder / "page.png"
        contract_path.write_text(json.dumps(contract, ensure_ascii=False), encoding="utf-8")
        report = self.validator.validate(contract_path)
        report_path.write_text(json.dumps(report), encoding="utf-8")
        self.composer.compose(contract_path, output, evidence_path)
        return report, json.loads(evidence_path.read_text(encoding="utf-8")), output

    def test_my_name_recovers_rich_source_and_builds_trace_copy_page(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            illustration = temporary / "my-name.png"
            sample_illustration(illustration)
            source = (
                ROOT
                / "production-prompts/communication-champions/nursery/v4/pages/"
                "CC-NURSERY-V4-P008-my-name.json"
            )
            contract = self.build_contract(
                source,
                illustration,
                title_lines=["Communication", "Champions"],
                level="Nursery",
                age="3+",
            )
            self.assertEqual("trace-copy", contract["activity"]["layout_variant"])
            self.assertEqual("curated-page-override", contract["activity"]["resolution_source"])
            self.assertEqual(
                ["model_phrase", "trace_line", "copy_line"],
                [item["type"] for item in contract["deterministic_components"]],
            )
            self.assertEqual("official-asset-separate", contract["illustration"]["star_policy"])
            self.assertIn("What is your name?", contract["guidance"]["teacher"]["question"])
            report, evidence, output = self.render(contract, temporary)
            self.assertEqual("PASS", report["status"])
            self.assertEqual(3, evidence["components"]["worksheet"]["component_count"])
            self.assertIn("official_star", evidence["components"])
            self.assertEqual("REVIEW_CANDIDATE", evidence["qa"]["status"])
            with Image.open(output) as rendered:
                self.assertEqual((2480, 3508), rendered.size)

    def test_primary_colours_replaces_generic_source_with_curated_activity(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            illustration = temporary / "primary-colours.png"
            sample_illustration(illustration)
            source = (
                ROOT
                / "production-prompts/art-colour-fun/lkg/v4/pages/"
                "AC-LKG-V4-P008-primary-colours.json"
            )
            contract = self.build_contract(
                source,
                illustration,
                title_lines=["Art & Colour", "Fun"],
                level="LKG",
                age="4+",
            )
            combined = json.dumps(contract).casefold()
            self.assertNotIn("art activity discussion", combined)
            self.assertNotIn("one dominant learning scene", combined)
            self.assertNotIn("what can you show or tell about", combined)
            self.assertEqual("colour-draw", contract["activity"]["layout_variant"])
            self.assertEqual(
                ["model_example", "creative_response_area"],
                [item["type"] for item in contract["deterministic_components"]],
            )
            self.assertEqual("prohibited", contract["illustration"]["star_policy"])
            self.assertIn("red, yellow, and blue", contract["learning"]["student_instruction"])
            report, evidence, _ = self.render(contract, temporary)
            self.assertEqual("PASS", report["status"])
            self.assertNotIn("official_star", evidence["components"])
            self.assertEqual(
                ["model_example", "creative_response_area"],
                evidence["components"]["worksheet"]["component_types"],
            )

    def test_blank_illustration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            illustration = temporary / "blank.png"
            Image.new("RGB", (1200, 1000), "white").save(illustration, "PNG", dpi=(300, 300))
            source = (
                ROOT
                / "production-prompts/communication-champions/nursery/v4/pages/"
                "CC-NURSERY-V4-P008-my-name.json"
            )
            contract = self.build_contract(
                source,
                illustration,
                title_lines=["Communication", "Champions"],
                level="Nursery",
                age="3+",
            )
            contract_path = temporary / "contract.json"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "blank or near-white"):
                self.validator.validate(contract_path)

    def test_all_layout_variants_have_non_overlapping_registered_geometry(self) -> None:
        template = json.loads(
            (ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json").read_text(
                encoding="utf-8"
            )
        )
        base = self.composer.load_module()
        for layout_name, layout in template["layout_variants"].items():
            geometry = base.validate_geometry(template, layout)
            self.assertFalse(geometry["illustration_response_overlap"], layout_name)
            self.assertGreaterEqual(geometry["illustration_response_gap"], 30, layout_name)


if __name__ == "__main__":
    unittest.main()
