from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NORMALIZER = ROOT / "bcube-publishing-sdk/normalizers/build_learning_contract_v2.py"
REFINER = ROOT / "bcube-publishing-sdk/normalizers/refine_learning_contract_v2.py"
FINALISER = ROOT / "bcube-publishing-sdk/normalizers/finalise_learning_contract_v2.py"
SOURCE = (
    ROOT
    / "production-prompts/early-literacy-adventures/lkg/v4/pages/"
    "EL-LKG-V4-P008-alphabet-review.json"
)


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise AssertionError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class LearningContractFinaliserV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.normalizer = load_module("learning_normalizer_finaliser_test", NORMALIZER)
        cls.refiner = load_module("learning_refiner_finaliser_test", REFINER)
        cls.finaliser = load_module("learning_finaliser_test", FINALISER)

    def test_alphabet_review_is_repaired_before_rendering(self) -> None:
        contract = self.normalizer.build_contract(
            root=ROOT,
            v4_path=SOURCE,
            illustration_path="PENDING_ILLUSTRATION",
            official_logo_path="PENDING_LOGO",
            book_title_lines=["Early Literacy", "Adventures"],
            level_name="LKG",
            age="4+",
        )
        self.refiner.refine_contract(contract, curated_override_applied=False)
        self.finaliser.finalise_contract(contract, curated_override_applied=False)
        combined = json.dumps(contract).casefold()
        self.assertNotIn("to be completed", combined)
        self.assertNotIn("a4 portrait", combined)
        self.assertNotIn("teacher guiding", combined)
        self.assertNotIn("what can you show or tell about", combined)
        self.assertEqual("reflect", contract["activity"]["primary"])
        self.assertEqual("reflect-assess", contract["activity"]["layout_variant"])
        self.assertEqual(
            [{"type": "response_box", "label": "Show what you know", "lines": 3}],
            contract["deterministic_components"],
        )
        self.assertIn("alphabet", contract["learning"]["objective"].casefold())
        self.assertTrue(contract["source_lineage"]["contract_finalisation_applied"])

    def test_curated_contract_is_not_reclassified(self) -> None:
        contract = {
            "identity": {"title": "My Review Picture"},
            "learning": {
                "objective": "Create one personal picture to show a remembered idea.",
                "student_instruction": "Draw one idea you remember.",
            },
            "activity": {
                "primary": "draw",
                "secondary": [],
                "response_modes": ["draw"],
                "layout_variant": "colour-draw",
                "resolution_source": "curated-page-override",
            },
            "guidance": {
                "teacher": {"model": "Show one example.", "question": "What do you remember?"},
                "parent_extension": "Talk about the picture at home.",
            },
            "illustration": {"scene": "One child drawing.", "focal_point": "The child drawing."},
            "deterministic_components": [{"type": "creative_response_area", "label": "My picture"}],
            "qa_requirements": {"component_count": 1},
            "source_lineage": {},
        }
        self.finaliser.finalise_contract(contract, curated_override_applied=True)
        self.assertEqual("draw", contract["activity"]["primary"])
        self.assertEqual("colour-draw", contract["activity"]["layout_variant"])
        self.assertFalse(contract["source_lineage"]["contract_finalisation_applied"])


if __name__ == "__main__":
    unittest.main()
