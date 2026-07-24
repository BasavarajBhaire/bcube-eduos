#!/usr/bin/env python3
"""Refine generic Learning Page Contract V2 content before validation and rendering."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GENERIC_FRAGMENTS = (
    "art activity discussion",
    "include one teacher demonstration",
    "include one guided art activity",
    "include one independent activity",
    "include one speaking opportunity",
    "expected child response",
    "premium illustration composition",
    "teacher-guided",
    "print-ready",
    "one dominant learning scene",
    "one clear learning scene",
    "one dominant focus for",
    "demonstrate the art technique before children begin",
    "repeat the activity at home using safe art materials",
    "what can you show or tell about",
    "model once, invite one response, pause for processing",
    "use a familiar home routine or everyday object",
)

INSTRUCTION_TEMPLATES = {
    "observe": "Look closely. Point to what you notice and say its name.",
    "speak": "Look at the picture. Say your answer in a clear sentence.",
    "listen": "Listen carefully. Point to the picture that matches what you hear.",
    "trace": "Look at the model. Trace it carefully, then try it once by yourself.",
    "match": "Look at both sides. Match each item to the one that belongs with it.",
    "connect": "Join each item to the one that belongs with it.",
    "colour": "Name the colours. Colour the matching objects neatly.",
    "draw": "Look at the example. Draw your own idea in the space.",
    "count": "Count each group carefully. Mark or write the correct answer.",
    "compare": "Look at both groups. Show which has more, fewer, or the same.",
    "sort": "Look at each picture. Sort it into the correct group.",
    "sequence": "Look at the pictures. Put them in the correct order.",
    "circle": "Look at every choice. Circle the correct answer.",
    "complete": "Look at the clue. Complete the missing part.",
    "maze": "Start at the beginning. Follow the path carefully to the finish.",
    "explore": "Look, try, and notice what changes. Share what you discover.",
    "think": "Look closely. Think about the clue and choose the best answer.",
    "reflect": "Think about what you learned. Draw or tell your answer.",
    "assessment": "Complete each task independently and show what you know.",
}

TEACHER_TEMPLATES = {
    "observe": "Model looking carefully and pointing before naming. Invite one observation at a time and affirm accurate noticing.",
    "speak": "Model one short sentence, pause, and invite the child to respond using a word, phrase, or sentence.",
    "listen": "Give the listening cue once, pause for processing, and invite the child to point before answering.",
    "trace": "Demonstrate the starting point and direction once. Guide the first movement, then leave the independent response unfinished.",
    "match": "Name one item from each side and demonstrate one match without completing the remaining pairs.",
    "connect": "Demonstrate one careful joining line, then invite the child to complete the remaining connections.",
    "colour": "Name the target colours and demonstrate a small sample without colouring the child’s response area.",
    "draw": "Discuss one simple idea and show a small model while leaving the main drawing area for the child.",
    "count": "Touch each object once while counting aloud, then invite the child to count independently.",
    "compare": "Model one comparison using more, fewer, or the same, then ask the child to explain the next choice.",
    "sort": "Name the groups and sort one example. Invite the child to complete the remaining choices and explain one placement.",
    "sequence": "Talk through the first event, then invite the child to order the remaining pictures and retell the sequence.",
    "circle": "Explain the cue and model circling one example only when a model is present.",
    "complete": "Point out the repeating or visual clue and model how to find one missing part.",
    "maze": "Trace the route in the air first. Encourage slow pencil movement from start to finish.",
    "explore": "Introduce the safe materials, ask for a prediction, and observe the result together without giving the conclusion first.",
    "think": "Read the clue slowly and invite the child to explain the choice using a word, gesture, or short sentence.",
    "reflect": "Invite the child to recall the activity and accept a drawing, gesture, word, or short sentence.",
    "assessment": "Give one instruction at a time and record only what the child completes independently.",
}

QUESTION_TEMPLATES = {
    "observe": "What do you notice?",
    "speak": "What would you like to say about the picture?",
    "listen": "Which picture matches what you heard?",
    "trace": "Where will you start?",
    "match": "Which two belong together?",
    "connect": "What belongs with this one?",
    "colour": "Which colour will you use, and why?",
    "draw": "What will you add to your picture?",
    "count": "How many are there?",
    "compare": "Which group has more, fewer, or the same?",
    "sort": "Why does this picture belong in that group?",
    "sequence": "What happens first? What happens next?",
    "circle": "Which choice is correct?",
    "complete": "What clue helps you find the missing part?",
    "maze": "Where will you start and finish?",
    "explore": "What do you think will happen? What did you notice?",
    "think": "Why is that the best choice?",
    "reflect": "What did you learn or enjoy?",
    "assessment": "Can you show what you know?",
}

PARENT_TEMPLATES = {
    "observe": "Find one familiar example at home and talk about what you notice together.",
    "speak": "Use the same sentence pattern during a familiar home conversation.",
    "listen": "Play a short listening-and-pointing game using familiar household sounds.",
    "trace": "Trace the same shape or word once with a finger on a safe surface.",
    "match": "Match two pairs of familiar household objects and name why they belong together.",
    "connect": "Pair familiar items that belong together and explain each choice.",
    "colour": "Find safe objects in the target colours and name them together.",
    "draw": "Draw one familiar idea together using paper and crayons.",
    "count": "Count a small group of familiar household objects together.",
    "compare": "Compare two small groups using more, fewer, or the same.",
    "sort": "Sort a few safe household items into two simple groups.",
    "sequence": "Talk through the order of a familiar daily routine.",
    "circle": "Ask the child to choose between two familiar options and explain the choice.",
    "complete": "Make a simple repeating pattern with safe household objects.",
    "maze": "Use a finger to follow a simple path on a table or floor.",
    "explore": "Repeat the safe observation using common household materials.",
    "think": "Ask a similar why question during a familiar routine.",
    "reflect": "Ask the child to tell or draw one thing remembered from the page.",
    "assessment": "Notice the skill naturally during play without adding another scored task.",
}

SCENE_TEMPLATES = {
    "observe": "Large, familiar objects arranged in one clear observation scene with every target fully visible.",
    "speak": "One clear preschool interaction that gives the child an obvious idea to describe or discuss.",
    "listen": "A small set of large, distinct picture choices that can be identified after hearing a cue.",
    "trace": "One simple visual model above a completely clear deterministic tracing and copying area.",
    "match": "Two balanced groups of large picture objects with clear visual relationships and open space for joining lines.",
    "connect": "Two organised groups of large related objects with unobstructed space between them for connection lines.",
    "colour": "Large, simple colouring objects with thick rounded outlines and one small completed model example.",
    "draw": "One simple model scene beside or above a large unobstructed child drawing area.",
    "count": "Small groups of large, well-separated objects that can each be touched and counted once.",
    "compare": "Two clearly separated groups of familiar objects that make the comparison visually obvious.",
    "sort": "A small set of familiar objects shown above clear category areas, with no object already placed as the child’s answer.",
    "sequence": "Three or four clear picture moments from one familiar event, each visually distinct and easy to order.",
    "circle": "Three or four large picture choices with one clear correct response path.",
    "complete": "One simple pattern or partly completed picture with the missing part clearly defined.",
    "maze": "A small themed start-and-finish illustration positioned outside a large, clear deterministic maze area.",
    "explore": "One safe preschool investigation with the materials and observable change clearly visible.",
    "think": "One visual reasoning problem with a small number of large, clearly different choices.",
    "reflect": "One warm recap image connected to the learning, leaving the deterministic reflection area clear.",
    "assessment": "A calm, uncluttered review illustration that supports the assessed skill without revealing the answer.",
}

FOCAL_TEMPLATES = {
    "observe": "The exact objects the child must notice and name.",
    "speak": "The child’s oral response, supported by one obvious visual cue.",
    "listen": "The distinct picture choices used for the listening response.",
    "trace": "The visual model; all writing guides are constructed separately by the page composer.",
    "match": "The relationship between the left and right picture groups.",
    "connect": "The related pairs and the unobstructed joining space.",
    "colour": "The target colours or colouring objects; the child artwork area stays clear.",
    "draw": "The model idea and the unobstructed child drawing area.",
    "count": "The countable objects and their clear one-to-one separation.",
    "compare": "The visible difference or equality between the two groups.",
    "sort": "The objects and the category distinction, not completed placements.",
    "sequence": "The changing action from one picture moment to the next.",
    "circle": "The small set of answer choices.",
    "complete": "The visual clue and the single missing response.",
    "maze": "The themed start and finish; the route itself is built deterministically.",
    "explore": "The safe materials and the observable change.",
    "think": "The clue and the clearly differentiated choices.",
    "reflect": "The remembered learning event and the child’s own response.",
    "assessment": "The assessed concept without a completed answer.",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def is_generic(value: Any) -> bool:
    text = clean(value).casefold()
    if not text:
        return True
    return any(fragment in text for fragment in GENERIC_FRAGMENTS)


def shorten_instruction(value: str, activity: str, maximum: int = 180) -> tuple[str, bool]:
    text = clean(value)
    if is_generic(text) or len(text) > maximum:
        return INSTRUCTION_TEMPLATES[activity], True
    return text, False


def refine_contract(contract: dict[str, Any], *, curated_override_applied: bool) -> dict[str, Any]:
    activity = clean(contract["activity"].get("primary")).casefold()
    if activity not in INSTRUCTION_TEMPLATES:
        raise ValueError(f"No refinement rules exist for activity {activity!r}")
    changes: list[str] = []
    if not curated_override_applied:
        instruction, changed = shorten_instruction(
            clean(contract["learning"].get("student_instruction")),
            activity,
        )
        if changed:
            contract["learning"]["student_instruction"] = instruction
            changes.append("student_instruction")

        expected = clean(contract["learning"].get("expected_response"))
        if not expected or is_generic(expected):
            contract["learning"]["expected_response"] = (
                f"Child completes the {activity} response and shows or explains the answer in an age-appropriate way."
            )
            changes.append("expected_response")

        teacher = contract["guidance"]["teacher"]
        if is_generic(teacher.get("model")):
            teacher["model"] = TEACHER_TEMPLATES[activity]
            changes.append("teacher.model")
        if is_generic(teacher.get("question")):
            teacher["question"] = QUESTION_TEMPLATES[activity]
            changes.append("teacher.question")

        if is_generic(contract["guidance"].get("parent_extension")):
            contract["guidance"]["parent_extension"] = PARENT_TEMPLATES[activity]
            changes.append("parent_extension")

        illustration = contract["illustration"]
        if is_generic(illustration.get("scene")):
            illustration["scene"] = SCENE_TEMPLATES[activity]
            changes.append("illustration.scene")
        if is_generic(illustration.get("focal_point")):
            illustration["focal_point"] = FOCAL_TEMPLATES[activity]
            changes.append("illustration.focal_point")

    contract["source_lineage"]["portfolio_content_refiner"] = "learning-content-refiner-v1.0"
    contract["source_lineage"]["content_refinement_changes"] = changes
    contract["source_lineage"]["content_refinement_applied"] = bool(changes)
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--curated-override-applied", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = load(args.contract)
    refined = refine_contract(
        contract,
        curated_override_applied=args.curated_override_applied,
    )
    output = args.output or args.contract
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(refined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "REFINED",
                "page_id": refined["identity"]["page_id"],
                "changes": refined["source_lineage"]["content_refinement_changes"],
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
