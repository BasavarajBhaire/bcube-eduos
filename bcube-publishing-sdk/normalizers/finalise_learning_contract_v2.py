#!/usr/bin/env python3
"""Finalise systematic Learning Page Contract V2 defects after normalisation/refinement."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REFINER_PATH = ROOT / "bcube-publishing-sdk/normalizers/refine_learning_contract_v2.py"

GENERIC_OBJECTIVES = (
    "to be completed",
    "tbd",
    "learning objective",
    "develop skills through this activity",
)
SYSTEMATIC_SOURCE_FRAGMENTS = (
    "teacher guiding",
    "teacher-centered classroom",
    "teacher-centred classroom",
    "one short speaking, reflection, or independent practice response",
    "repeat learning at home using everyday situations",
    "let's observe together",
    "a4 portrait",
    "purposeful labelled activity zones",
    "rich educational storytelling",
)
REVIEW_TITLE_MARKERS = (
    "review",
    "recap",
    "reflection",
    "check my learning",
    "what i learned",
    "checkpoint",
    "revision",
)

OBJECTIVE_TEMPLATES = {
    "observe": "Observe and identify the key features connected to {topic}.",
    "speak": "Describe and discuss ideas connected to {topic} using clear language.",
    "listen": "Listen carefully and identify the correct information connected to {topic}.",
    "trace": "Develop controlled tracing and copying skills through {topic}.",
    "match": "Recognise relationships and match items correctly in {topic}.",
    "connect": "Recognise related items and connect them correctly in {topic}.",
    "colour": "Recognise and apply the target colours or visual features in {topic}.",
    "draw": "Represent an idea connected to {topic} through a simple drawing.",
    "count": "Count accurately and record a response connected to {topic}.",
    "compare": "Compare groups or features connected to {topic} using appropriate language.",
    "sort": "Sort and classify familiar items connected to {topic}.",
    "sequence": "Order the events or stages connected to {topic}.",
    "circle": "Identify and select the correct response connected to {topic}.",
    "complete": "Use a visual or logical clue to complete the missing part in {topic}.",
    "maze": "Follow a controlled path from start to finish while practising visual planning.",
    "explore": "Observe, predict, and explain a simple investigation connected to {topic}.",
    "think": "Use visual clues and reasoning to solve a problem connected to {topic}.",
    "reflect": "Review and show understanding of the key ideas in {topic}.",
    "assessment": "Show independent understanding of the key skills in {topic}.",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_refiner() -> ModuleType:
    specification = importlib.util.spec_from_file_location("bcube_learning_refiner_for_finaliser", REFINER_PATH)
    if specification is None or specification.loader is None:
        raise ValueError(f"Cannot load learning refiner: {REFINER_PATH}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def contains_any(value: Any, fragments: tuple[str, ...]) -> bool:
    text = clean(value).casefold()
    return any(fragment in text for fragment in fragments)


def topic_from_title(title: str) -> str:
    topic = clean(title)
    topic = re.sub(
        r"\b(review|recap|reflection|checkpoint|revision)\b",
        "",
        topic,
        flags=re.IGNORECASE,
    )
    topic = " ".join(topic.split()).strip(" -–—:;")
    return topic or clean(title) or "this learning"


def reclassify_review(contract: dict[str, Any], refiner: ModuleType, changes: list[str]) -> None:
    title = clean(contract["identity"].get("title"))
    if not contains_any(title, REVIEW_TITLE_MARKERS):
        return
    old_primary = clean(contract["activity"].get("primary"))
    contract["activity"]["primary"] = "reflect"
    contract["activity"]["secondary"] = [old_primary] if old_primary and old_primary != "reflect" else []
    contract["activity"]["response_modes"] = ["oral", "draw", "independent-response"]
    contract["activity"]["layout_variant"] = "reflect-assess"
    contract["activity"]["resolution_source"] = "page-role-finaliser"
    contract["deterministic_components"] = [
        {"type": "response_box", "label": "Show what you know", "lines": 3}
    ]
    contract["qa_requirements"]["component_count"] = 1
    contract["learning"]["student_instruction"] = refiner.INSTRUCTION_TEMPLATES["reflect"]
    contract["guidance"]["teacher"]["model"] = refiner.TEACHER_TEMPLATES["reflect"]
    contract["guidance"]["teacher"]["question"] = refiner.QUESTION_TEMPLATES["reflect"]
    contract["guidance"]["parent_extension"] = refiner.PARENT_TEMPLATES["reflect"]
    contract["illustration"]["scene"] = refiner.SCENE_TEMPLATES["reflect"]
    contract["illustration"]["focal_point"] = refiner.FOCAL_TEMPLATES["reflect"]
    changes.extend(
        [
            "activity.review-role",
            "deterministic_components",
            "student_instruction.review-role",
            "guidance.review-role",
            "illustration.review-role",
        ]
    )


def repair_objective(contract: dict[str, Any], changes: list[str]) -> None:
    objective = clean(contract["learning"].get("objective"))
    if objective and not contains_any(objective, GENERIC_OBJECTIVES):
        return
    activity = clean(contract["activity"].get("primary")).casefold()
    template = OBJECTIVE_TEMPLATES.get(activity)
    if not template:
        raise ValueError(f"No objective template exists for activity {activity!r}")
    topic = topic_from_title(clean(contract["identity"].get("title"))).lower()
    contract["learning"]["objective"] = template.format(topic=topic)
    changes.append("learning.objective")


def repair_systematic_source_text(
    contract: dict[str, Any],
    refiner: ModuleType,
    changes: list[str],
) -> None:
    activity = clean(contract["activity"].get("primary")).casefold()
    if activity not in refiner.INSTRUCTION_TEMPLATES:
        raise ValueError(f"No systematic repair templates exist for activity {activity!r}")
    if contains_any(contract["learning"].get("student_instruction"), SYSTEMATIC_SOURCE_FRAGMENTS):
        contract["learning"]["student_instruction"] = refiner.INSTRUCTION_TEMPLATES[activity]
        changes.append("student_instruction.systematic-source")
    teacher = contract["guidance"]["teacher"]
    if contains_any(teacher.get("model"), SYSTEMATIC_SOURCE_FRAGMENTS):
        teacher["model"] = refiner.TEACHER_TEMPLATES[activity]
        changes.append("teacher.model.systematic-source")
    if contains_any(teacher.get("question"), SYSTEMATIC_SOURCE_FRAGMENTS):
        teacher["question"] = refiner.QUESTION_TEMPLATES[activity]
        changes.append("teacher.question.systematic-source")
    if contains_any(contract["guidance"].get("parent_extension"), SYSTEMATIC_SOURCE_FRAGMENTS):
        contract["guidance"]["parent_extension"] = refiner.PARENT_TEMPLATES[activity]
        changes.append("parent_extension.systematic-source")
    illustration = contract["illustration"]
    if contains_any(illustration.get("scene"), SYSTEMATIC_SOURCE_FRAGMENTS):
        illustration["scene"] = refiner.SCENE_TEMPLATES[activity]
        changes.append("illustration.scene.systematic-source")
    if contains_any(illustration.get("focal_point"), SYSTEMATIC_SOURCE_FRAGMENTS):
        illustration["focal_point"] = refiner.FOCAL_TEMPLATES[activity]
        changes.append("illustration.focal_point.systematic-source")


def finalise_contract(contract: dict[str, Any], *, curated_override_applied: bool) -> dict[str, Any]:
    refiner = load_refiner()
    changes: list[str] = []
    if not curated_override_applied:
        reclassify_review(contract, refiner, changes)
        repair_systematic_source_text(contract, refiner, changes)
        repair_objective(contract, changes)
    contract["source_lineage"]["learning_contract_finaliser"] = "learning-contract-finaliser-v1.0"
    contract["source_lineage"]["contract_finalisation_changes"] = changes
    contract["source_lineage"]["contract_finalisation_applied"] = bool(changes)
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--curated-override-applied", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = load(args.contract)
    finalised = finalise_contract(
        contract,
        curated_override_applied=args.curated_override_applied,
    )
    output = args.output or args.contract
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(finalised, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "FINALISED",
                "page_id": finalised["identity"]["page_id"],
                "changes": finalised["source_lineage"]["contract_finalisation_changes"],
                "output": str(output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BCube learning-contract finalisation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
