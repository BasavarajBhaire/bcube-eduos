#!/usr/bin/env python3
"""Apply the locked portfolio learning-content policy before validation and rendering."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

CURATOR_PATH = Path(__file__).with_name("curate_learning_content_v1.py")

INSTRUCTION_TEMPLATES = {
    "observe": "Look closely. Point to what you notice and say its name.",
    "speak": "Look at the picture. Say your answer in one clear sentence.",
    "listen": "Listen carefully. Point to the picture that matches what you hear.",
    "trace": "Look at the model. Trace it carefully, then try it once by yourself.",
    "match": "Look at both sides. Match each item to the one that belongs with it.",
    "connect": "Join each item to the one that belongs with it.",
    "colour": "Name the colours. Use them carefully in your response.",
    "draw": "Look at the example. Draw your own idea in the space.",
    "count": "Count each group carefully. Mark or write the correct answer.",
    "compare": "Look at both groups. Show which has more, fewer, or the same.",
    "sort": "Look at each picture. Sort it into the correct group.",
    "sequence": "Look at the pictures. Put them in the correct order.",
    "circle": "Look at every choice. Circle the best answer.",
    "complete": "Look at the clue. Complete the missing part.",
    "maze": "Start at the beginning. Follow the path carefully to the finish.",
    "explore": "Predict, try safely, and share what you notice.",
    "think": "Look closely. Think about the clue and choose the best answer.",
    "reflect": "Think about what you learned. Draw or tell your answer.",
    "assessment": "Complete each task independently and show what you know.",
}
TEACHER_TEMPLATES = {
    activity: f"Model one {activity} response, then leave the remaining task for the child."
    for activity in INSTRUCTION_TEMPLATES
}
QUESTION_TEMPLATES = {
    activity: f"What do you notice or know about this {activity} task?"
    for activity in INSTRUCTION_TEMPLATES
}
PARENT_TEMPLATES = {
    activity: f"Practise the same {activity} skill once during a familiar home routine."
    for activity in INSTRUCTION_TEMPLATES
}
SCENE_TEMPLATES = {
    activity: f"One clear preschool support illustration for the {activity} task."
    for activity in INSTRUCTION_TEMPLATES
}
FOCAL_TEMPLATES = {
    activity: f"The exact visual evidence needed for the {activity} response."
    for activity in INSTRUCTION_TEMPLATES
}


def load_curator() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "bcube_portfolio_learning_content_v1",
        CURATOR_PATH,
    )
    if specification is None or specification.loader is None:
        raise ValueError(f"Cannot load portfolio content curator: {CURATOR_PATH}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def is_generic(value: Any) -> bool:
    text = clean(value).casefold()
    return not text or any(
        fragment in text
        for fragment in (
            "art activity discussion",
            "one dominant learning scene",
            "one clear preschool illustration for",
            "what can you show or tell about",
            "expected child response",
        )
    )


def is_non_actionable_instruction(value: Any) -> bool:
    text = clean(value)
    return len(text.split()) <= 5 or not text.endswith((".", "?", "!"))


def refine_contract(
    contract: dict[str, Any],
    *,
    curated_override_applied: bool,
) -> dict[str, Any]:
    curator = load_curator()
    curator.apply_locked_content(contract)
    contract.setdefault("source_lineage", {})
    contract["source_lineage"].update(
        {
            "portfolio_content_refiner": curator.VERSION,
            "content_refinement_changes": [
                "learning.objective",
                "learning.student_instruction",
                "learning.expected_response",
                "learning.model_text",
                "activity",
                "guidance.teacher",
                "guidance.parent_extension",
                "deterministic_components",
                "qa_requirements.content_status",
            ],
            "content_refinement_applied": True,
            "curated_override_preserved": bool(curated_override_applied),
        }
    )
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--curated-override-applied", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = refine_contract(
        load(args.contract),
        curated_override_applied=args.curated_override_applied,
    )
    output = args.output or args.contract
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "LOCKED",
                "page_id": contract["identity"]["page_id"],
                "content_version": contract["source_lineage"]["portfolio_content_refiner"],
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
        print(f"BCube learning-content refinement FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
