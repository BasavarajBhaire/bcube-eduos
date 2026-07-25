#!/usr/bin/env python3
"""Lock page-specific educational content for every BCube Learning Page Contract V2 page."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

VERSION = "portfolio-learning-content-v1.0"
GENERIC_PHRASES = (
    "look carefully at the pictures. follow the model",
    "look at the simple model for an idea",
    "choose one example that shows your learning",
    "look at the model example. use the pictures",
    "study the model and visual clues",
    "follow the model slowly",
    "complete the task and show or say",
)
LAYOUT_BY_ACTIVITY = {
    "observe": "observe-speak",
    "speak": "observe-speak",
    "listen": "observe-speak",
    "trace": "trace-copy",
    "match": "match-connect",
    "connect": "match-connect",
    "colour": "colour-draw",
    "draw": "colour-draw",
    "count": "count-compare",
    "compare": "count-compare",
    "sort": "sort-classify",
    "sequence": "sequence-story",
    "circle": "choice-circle",
    "complete": "choice-circle",
    "think": "choice-circle",
    "maze": "maze-path",
    "explore": "build-explore",
    "reflect": "reflect-assess",
    "assessment": "reflect-assess",
}

GENERIC_OBJECTIVES = (
    "to be completed",
    "tbd",
    "learning objective",
    "develop skills through this activity",
)
OBJECTIVE_TEMPLATES = {
    "observe": "Observe and identify the key features connected to {topic}.",
    "speak": "Describe and discuss ideas connected to {topic} using clear language.",
    "listen": "Listen carefully and identify information connected to {topic}.",
    "trace": "Develop controlled tracing and copying skills through {topic}.",
    "match": "Recognise relationships and match items correctly in {topic}.",
    "connect": "Recognise related items and connect them correctly in {topic}.",
    "colour": "Recognise and apply the target colours or visual features in {topic}.",
    "draw": "Represent an idea connected to {topic} through a simple creative response.",
    "count": "Count accurately and record a response connected to {topic}.",
    "compare": "Compare groups or features connected to {topic} using appropriate language.",
    "sort": "Sort and classify familiar items connected to {topic}.",
    "sequence": "Order the events or stages connected to {topic}.",
    "circle": "Identify and select an appropriate response connected to {topic}.",
    "complete": "Use a visual or logical clue to complete the missing part in {topic}.",
    "think": "Use visual clues and reasoning to solve a problem connected to {topic}.",
    "maze": "Follow a controlled path from start to finish while practising visual planning.",
    "explore": "Observe, predict, and explain a simple investigation connected to {topic}.",
    "reflect": "Review and show understanding of the key ideas in {topic}.",
    "assessment": "Show independent understanding of the key skills in {topic}.",
}

RESPONSE_MODES = {
    "observe": ["point", "oral"],
    "speak": ["oral"],
    "listen": ["point", "oral"],
    "trace": ["trace", "write"],
    "match": ["connect"],
    "connect": ["connect"],
    "colour": ["colour", "draw", "oral"],
    "draw": ["draw", "oral"],
    "count": ["point", "number"],
    "compare": ["point", "oral"],
    "sort": ["place", "oral"],
    "sequence": ["order", "oral"],
    "circle": ["circle", "oral"],
    "complete": ["mark", "draw"],
    "think": ["choose", "oral"],
    "maze": ["pencil-path"],
    "explore": ["predict", "observe", "oral", "draw"],
    "reflect": ["draw", "oral"],
    "assessment": ["independent-response"],
}


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def combined(*values: Any) -> str:
    return " ".join(clean(value).casefold() for value in values)


def title_phrase(contract: dict[str, Any]) -> str:
    return clean(contract["identity"]["title"]).rstrip(".!?")


def page_id(contract: dict[str, Any]) -> str:
    return clean(contract["identity"]["page_id"])


def resolve_primary(contract: dict[str, Any]) -> str:
    title = title_phrase(contract)
    objective = clean(contract["learning"].get("objective"))
    current = clean(contract["activity"].get("primary")).casefold()
    text = combined(title, objective)

    if "maze" in text or "path to" in text:
        return "maze"
    if any(key in text for key in ("trace", "pre-writing", "copy your", "write your name")):
        return "trace"
    if "match" in text or "same sound" in text:
        return "match"
    if any(key in text for key in ("sort", "classif")):
        return "sort"
    if any(key in text for key in ("sequence", "story order", "daily routine", "follow the steps", "before & after")):
        return "sequence"
    if any(key in text for key in ("sink or float", "magnet", "predict", "experiment", "test ", "ramp", "bridge challenge", "investigate")):
        return "explore"
    if any(key in text for key in ("count", "numbers ", "number ", "how many", "addition", "subtract", "total", "quantity")):
        if any(key in text for key in ("more", "fewer", "same", "compare", "equal")):
            return "compare"
        return "count"
    if any(key in text for key in ("compare", "same and different", "more or less", "big and small", "long and short", "heavy and light")):
        return "compare"
    if any(key in text for key in ("pattern", "missing", "complete", "finish", "picture coding")):
        return "complete"
    if any(key in text for key in ("safe choice", "healthy choice", "kind choice", "responsible choice", "my choice")):
        return "circle"
    if any(key in text for key in ("review", "reflect", "celebrat", "journal", "certificate", "gallery", "my progress")):
        return "reflect"
    if any(key in text for key in ("listen", "sound")):
        return "listen"
    if any(key in text for key in ("speak", "talk", "tell", "question", "sentence", "story", "conversation", "show and tell", "name and age", "my name")):
        return "trace" if "my name" in text else "speak"
    if any(key in text for key in ("colour", "color", "paint", "crayon")):
        return "colour"
    if any(key in text for key in ("draw", "art", "poster", "collage", "craft", "create", "design", "printing", "clay")):
        return "draw"
    return current if current in LAYOUT_BY_ACTIVITY else "observe"


def locked_objective_for(contract: dict[str, Any], primary: str) -> str:
    objective = clean(contract["learning"].get("objective"))
    if objective and not any(fragment in objective.casefold() for fragment in GENERIC_OBJECTIVES):
        return objective
    topic = title_phrase(contract).casefold()
    return OBJECTIVE_TEMPLATES[primary].format(topic=topic)


def instruction_for(contract: dict[str, Any], primary: str) -> str:
    title = title_phrase(contract)
    lowered = title.casefold()
    identifier = page_id(contract)

    if identifier == "CC-NURSERY-V4-P008":
        return "Say, ‘My name is ___.’ Trace your name. Then write it once."
    if identifier == "AC-LKG-V4-P008":
        return "Name red, yellow, and blue. Use the three colours to create your own picture."
    if "my name and age" in lowered:
        return "Say your name and age in one clear sentence. Trace or copy the details on the lines."
    if "show and tell" in lowered:
        return "Choose one familiar object. Say its name and tell two clear details about it."
    if primary == "trace":
        if "name" in lowered:
            return f"Say the model for {lowered}. Trace it once, then make one careful copy."
        return f"Look at the {lowered} model. Trace slowly from the starting point, then try once independently."
    if primary == "match":
        return f"Look carefully at the {lowered} pictures. Match each item with the partner that belongs with it."
    if primary == "sequence":
        return f"Look at all four {lowered} picture moments. Put them in order, then tell what happens first, next, and last."
    if primary == "sort":
        return f"Look at the {lowered} pictures. Place each item in the correct group and say the sorting rule."
    if primary == "explore":
        if "sink or float" in lowered:
            return "Predict which objects will sink or float. Test them with an adult, then mark what happened."
        if "magnet" in lowered:
            return "Predict which objects the magnet will attract. Test them with an adult, then mark the results."
        return f"Look at the {lowered} question. Make a prediction, test or observe safely with an adult, then record what happened."
    if primary == "maze":
        return f"Find the start and finish in the {lowered} maze. Follow one clear path without crossing the borders."
    if primary == "count":
        return f"Count the {lowered} objects carefully. Touch each one once, then mark or write the correct number."
    if primary == "compare":
        return f"Compare the {lowered} pictures or groups. Show which is more, fewer, the same, bigger, smaller, longer, or shorter."
    if primary == "complete":
        return f"Study the {lowered} clue. Complete the missing part or next step, then explain the pattern you used."
    if primary in {"circle", "think"}:
        return f"Look at each {lowered} situation or clue. Choose the best answer and say why."
    if primary in {"reflect", "assessment"}:
        return f"Think about {lowered}. Choose one example, draw or tell what you learned, and celebrate your effort."
    if primary == "listen":
        return f"Listen carefully to the {lowered} cue. Point to the matching picture and say one short answer."
    if primary == "speak":
        if "story" in lowered:
            return f"Look at the {lowered} pictures. Tell the story using a clear beginning, middle, and ending."
        if "question" in lowered:
            return f"Look at the {lowered} picture clue. Ask or answer one clear question in a complete sentence."
        return f"Look at the {lowered} scene. Take turns speaking and listening, then say one clear sentence."
    if primary == "colour":
        return f"Name the colours shown for {lowered}. Use them carefully to colour or create your own response."
    if primary == "draw":
        return f"Look at the simple {lowered} model for an idea. Create your own response in the large work area."
    return f"Look closely at the {lowered} pictures. Point to the important details and say what you notice."


def expected_response_for(contract: dict[str, Any], primary: str) -> str:
    title = title_phrase(contract).casefold()
    identifier = page_id(contract)
    if identifier == "CC-NURSERY-V4-P008":
        return "Child says own name, traces the adult-written model, and makes one supported copy attempt."
    if identifier == "AC-LKG-V4-P008":
        return "Child names red, yellow, and blue and uses the three colours in one simple original picture."
    templates = {
        "trace": f"Child traces the {title} model with controlled movement and makes one supported independent attempt.",
        "match": f"Child connects each {title} item to the correct partner and explains at least one match.",
        "sequence": f"Child places the four {title} pictures in a meaningful order and orally describes the sequence.",
        "sort": f"Child places each {title} item in the correct group and states or demonstrates the sorting rule.",
        "explore": f"Child makes a prediction about {title}, observes a safe test, and records or tells the result.",
        "maze": f"Child follows a continuous path from start to finish in the {title} maze.",
        "count": f"Child counts the {title} objects accurately and records or selects the corresponding number.",
        "compare": f"Child compares the {title} pictures or groups and uses an appropriate comparison word.",
        "complete": f"Child completes the missing {title} part or next step using the visible rule.",
        "circle": f"Child selects the best {title} choice and gives a short reason through speech, gesture, or supported dictation.",
        "think": f"Child chooses or constructs a reasonable answer for {title} and explains the choice using words or gestures.",
        "reflect": f"Child shares one specific memory, preference, skill, or achievement connected to {title}.",
        "assessment": f"Child completes the {title} response independently at an age-appropriate level.",
        "listen": f"Child listens to the {title} cue, points to the correct picture, and gives one short response.",
        "speak": f"Child gives one clear age-appropriate oral response about {title} and listens to another speaker.",
        "colour": f"Child identifies the target colours for {title} and uses them purposefully in the response area.",
        "draw": f"Child creates one original, age-appropriate response inspired by the {title} model.",
        "observe": f"Child identifies at least one important {title} feature and says, points to, circles, or draws what was noticed.",
    }
    return templates[primary]


def teacher_guidance_for(contract: dict[str, Any], primary: str) -> dict[str, str]:
    title = title_phrase(contract).casefold()
    identifier = page_id(contract)
    if identifier == "CC-NURSERY-V4-P008":
        return {
            "model": "Write the child’s name on the trace guide. Model the sentence once and guide the first movement.",
            "question": "What is your name?",
        }
    if identifier == "AC-LKG-V4-P008":
        return {
            "model": "Name red, yellow, and blue. Show one small example and leave the main space for the child.",
            "question": "Which colour will you use first?",
        }
    models = {
        "trace": f"Demonstrate one slow {title} trace. Guide only the first movement, then allow an independent attempt.",
        "match": f"Name one {title} item from each side and model one match without completing the remaining pairs.",
        "sequence": f"Discuss the first {title} event only. Ask the child to reason through the remaining order.",
        "sort": f"State the {title} sorting rule and place one example. Leave the remaining items for the child.",
        "explore": f"Introduce the safe {title} materials, ask for a prediction, and observe the result together.",
        "maze": f"Find the start and finish together. Trace the {title} route in the air before the child uses a pencil.",
        "count": f"Touch one {title} group item-by-item while counting aloud, then invite independent counting.",
        "compare": f"Model one {title} comparison using the correct comparison word, then pause for the child.",
        "complete": f"Point out one repeating or visual clue in {title}. Do not insert the missing answer.",
        "circle": f"Describe one {title} situation neutrally. Invite the child to choose and explain without signalling the answer.",
        "think": f"Read the {title} clue slowly. Ask the child to point to evidence before explaining the choice.",
        "reflect": f"Invite one specific {title} memory or example. Accept drawing, gesture, speech, or supported dictation.",
        "assessment": f"Give the {title} directions one at a time and record only what the child completes independently.",
        "listen": f"Give the {title} listening cue once, pause for processing, and invite pointing before speaking.",
        "speak": f"Model one short sentence about {title}. Prompt turn-taking and give enough time for the child to respond.",
        "colour": f"Name the target {title} colours and demonstrate a very small sample outside the child’s work area.",
        "draw": f"Discuss the {title} idea and show one simple model. Keep the main creative area entirely for the child.",
        "observe": f"Model looking closely at one {title} detail. Invite pointing before naming or describing.",
    }
    questions = {
        "trace": f"Where will you start the {title} trace?",
        "match": f"Which two {title} pictures belong together?",
        "sequence": f"What happens first in {title}? What happens next?",
        "sort": f"Why does this {title} item belong in that group?",
        "explore": f"What do you think will happen in {title}?",
        "maze": f"Which way will you go first in the {title} maze?",
        "count": f"How many {title} objects are there?",
        "compare": f"What is different or the same in {title}?",
        "complete": f"What clue helps you complete {title}?",
        "circle": f"Why is this the best {title} choice?",
        "think": f"What clue helped you solve {title}?",
        "reflect": f"What are you proud of or what did you learn in {title}?",
        "assessment": f"Can you show what you know about {title}?",
        "listen": f"What did you hear or notice in {title}?",
        "speak": f"What would you like to say about {title}?",
        "colour": f"Which colour will you use first for {title}?",
        "draw": f"What will you add to your {title} work?",
        "observe": f"What do you notice first about {title}?",
    }
    return {"model": models[primary], "question": questions[primary]}


def parent_extension_for(contract: dict[str, Any], primary: str) -> str:
    title = title_phrase(contract).casefold()
    identifier = page_id(contract)
    if identifier == "CC-NURSERY-V4-P008":
        return "Say family names together and clap the syllables."
    if identifier == "AC-LKG-V4-P008":
        return "Find one red, one yellow, and one blue object at home."
    values = {
        "trace": f"Trace a {title} shape or movement once with a finger on a safe surface.",
        "match": f"Find two or three familiar household pairs related to {title} and match them together.",
        "sequence": f"Talk through the order of a familiar routine connected to {title}.",
        "sort": f"Sort a few safe household items using the same {title} rule.",
        "explore": f"Repeat one safe {title} observation with common materials and adult supervision.",
        "maze": "Use a finger to follow a simple path from one familiar object to another.",
        "count": f"Count a small group of familiar objects and connect the quantity to {title}.",
        "compare": f"Compare two familiar objects or groups using the same {title} words.",
        "complete": f"Make a simple {title} pattern or missing-part game with safe household objects.",
        "circle": f"Notice one real-life {title} choice and ask the child to explain what is best.",
        "think": f"Ask one similar {title} why-or-how question during play.",
        "reflect": f"Ask the child to share one thing remembered or enjoyed about {title}.",
        "assessment": f"Notice the {title} skill naturally during play without adding another scored task.",
        "listen": f"Play a short listening-and-pointing game linked to {title}.",
        "speak": f"Use the {title} sentence or conversation skill during a familiar home routine.",
        "colour": f"Find safe household objects in the colours used for {title} and name them together.",
        "draw": f"Create one small {title} idea together with paper, crayons, or reusable materials.",
        "observe": f"Find one familiar example of {title} at home and talk about what you notice.",
    }
    return values[primary]


def infer_count(text: str, default: int) -> int:
    lowered = text.casefold()
    for word, value in (("one", 1), ("two", 2), ("three", 3), ("four", 4), ("five", 5), ("six", 6)):
        if re.search(rf"\b{word}\b", lowered):
            return value
    values = [int(value) for value in re.findall(r"\b([1-6])\b", lowered)]
    return values[0] if values else default


def model_text_for(contract: dict[str, Any], primary: str) -> str:
    title = title_phrase(contract).casefold()
    identifier = page_id(contract)
    if identifier == "CC-NURSERY-V4-P008":
        return "My name is ________."
    if identifier == "AC-LKG-V4-P008":
        return "Red • Yellow • Blue"
    if "my name and age" in title:
        return "My name is ________. I am ____ years old."
    if primary == "speak":
        if "full sentence" in title:
            return "I can see ________."
        if "question" in title:
            return "What is ________?"
        if "show and tell" in title:
            return "This is my ________. It is ________."
    if primary in {"reflect", "assessment"}:
        return "I learned ________."
    return ""


def deterministic_components_for(
    contract: dict[str, Any],
    primary: str,
    model_text: str,
    expected_response: str,
) -> list[dict[str, Any]]:
    title = title_phrase(contract)
    lowered = title.casefold()
    text = combined(title, contract["learning"].get("objective"), contract["learning"].get("student_instruction"))
    if primary == "trace":
        items: list[dict[str, Any]] = []
        if model_text:
            items.append({"type": "model_phrase", "text": model_text})
        items.append({"type": "trace_line", "count": 1, "label": "Trace my name" if "name" in lowered else f"Trace {lowered}"})
        if any(key in text for key in ("write", "copy", "name")):
            items.append({"type": "copy_line", "count": 1, "label": "Write my name" if "name" in lowered else "Try it"})
        return items
    if primary == "match":
        return [{"type": "matching_anchors", "count": max(3, min(4, infer_count(text, 4))), "label": f"Match {title}"}]
    if primary == "sequence":
        return [{"type": "sequence_slots", "count": 4, "label": f"Order {title}"}]
    if primary == "sort":
        count = 3 if any(key in text for key in ("three", "colour", "color", "shape")) else 2
        return [{"type": "sort_bins", "count": count, "labels": [f"Group {index + 1}" for index in range(count)]}]
    if primary == "explore":
        return [{"type": "prediction_observation", "labels": ["I think", "I noticed"]}]
    if primary == "maze":
        return [{"type": "maze_path", "rows": 7, "columns": 9, "start": "START", "finish": "FINISH"}]
    if primary in {"count", "compare"}:
        return [{"type": "number_response_boxes", "count": max(2, min(5, infer_count(text, 4))), "label": "My answer"}]
    if primary in {"complete", "circle", "think"}:
        return [{"type": "choice_targets", "count": max(2, min(4, infer_count(text, 4))), "label": "Choose or complete"}]
    if primary in {"reflect", "assessment"}:
        return [{"type": "response_box", "label": f"My {lowered} reflection", "lines": 3}]
    if primary in {"listen", "speak", "observe"}:
        return [{"type": "speech_response", "label": "Say or tell", "prompt": expected_response}]
    if primary in {"colour", "draw"}:
        items = []
        if model_text or any(key in text for key in ("model", "example", "look at")):
            items.append({"type": "model_example", "label": model_text or "Look at the model"})
        items.append({"type": "creative_response_area", "label": f"My {lowered} work"})
        return items
    raise ValueError(f"No content component mapping for {primary!r}")


def secondary_activities(instruction: str, primary: str) -> list[str]:
    lowered = instruction.casefold()
    candidates = (
        ("speak", ("say", "tell", "explain")),
        ("draw", ("draw", "create")),
        ("colour", ("colour", "color", "paint")),
        ("trace", ("trace",)),
        ("listen", ("listen",)),
    )
    values = [
        activity
        for activity, keywords in candidates
        if activity != primary and any(keyword in lowered for keyword in keywords)
    ]
    return values[:3]


def validate_locked_content(contract: dict[str, Any]) -> None:
    learning = contract["learning"]
    activity = contract["activity"]
    guidance = contract["guidance"]
    instruction = clean(learning.get("student_instruction"))
    if not instruction or any(phrase in instruction.casefold() for phrase in GENERIC_PHRASES):
        raise ValueError(f"{page_id(contract)} has generic or missing locked instruction: {instruction!r}")
    if not clean(learning.get("objective")) or not clean(learning.get("expected_response")):
        raise ValueError(f"{page_id(contract)} has incomplete locked learning content")
    if activity.get("layout_variant") != LAYOUT_BY_ACTIVITY.get(activity.get("primary")):
        raise ValueError(f"{page_id(contract)} has activity/layout mismatch")
    if not contract.get("deterministic_components"):
        raise ValueError(f"{page_id(contract)} has no deterministic worksheet components")
    teacher = guidance.get("teacher")
    if not isinstance(teacher, dict) or not clean(teacher.get("model")) or not clean(teacher.get("question")):
        raise ValueError(f"{page_id(contract)} has incomplete Teacher Tip content")
    if not clean(guidance.get("parent_extension")):
        raise ValueError(f"{page_id(contract)} has no Home Connection content")


def apply_locked_content(contract: dict[str, Any]) -> dict[str, Any]:
    primary = resolve_primary(contract)
    contract["learning"]["objective"] = locked_objective_for(contract, primary)
    instruction = instruction_for(contract, primary)
    expected = expected_response_for(contract, primary)
    model_text = model_text_for(contract, primary)
    components = deterministic_components_for(contract, primary, model_text, expected)

    contract["learning"]["student_instruction"] = instruction
    contract["learning"]["expected_response"] = expected
    contract["learning"]["model_text"] = model_text
    contract["activity"] = {
        "primary": primary,
        "secondary": secondary_activities(instruction, primary),
        "response_modes": list(RESPONSE_MODES[primary]),
        "layout_variant": LAYOUT_BY_ACTIVITY[primary],
        "resolution_source": VERSION,
    }
    contract["guidance"] = {
        "teacher": teacher_guidance_for(contract, primary),
        "parent_extension": parent_extension_for(contract, primary),
    }
    contract["deterministic_components"] = components
    contract.setdefault("qa_requirements", {})
    contract["qa_requirements"].update(
        {
            "component_count": len(components),
            "requires_response_area": True,
            "requires_page_specific_guidance": True,
            "content_status": "LOCKED",
        }
    )
    contract.setdefault("source_lineage", {})
    contract["source_lineage"].update(
        {
            "portfolio_content_version": VERSION,
            "portfolio_content_status": "LOCKED",
        }
    )
    contract["content_status"] = "LOCKED"
    validate_locked_content(contract)
    return contract


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = apply_locked_content(load(args.contract))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "LOCKED", "page_id": page_id(contract), "version": VERSION}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BCube learning-content curation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
