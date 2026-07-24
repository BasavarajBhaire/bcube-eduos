#!/usr/bin/env python3
"""Build BCube Learning Page Contract V2 from finalized V4 page packages."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_SPEC = ROOT / "bcube-publishing-sdk/contracts/learning-page-contract-v2.json"

PLACEHOLDER_PHRASES = (
    "one dominant learning scene",
    "one dominant focus for",
    "introduce the page purpose clearly",
    "use this page for orientation only",
    "use the page for its stated front-matter purpose",
    "art activity discussion",
    "what can you show or tell about",
)
DEFAULT_TEACHER_PROMPT = (
    "model once, invite one response, pause for processing, scaffold through gesture or choice, "
    "and affirm effort"
)
DEFAULT_PARENT_PROMPT = (
    "use a familiar home routine or everyday object to extend the learning without adding a scored task"
)

ACTIVITY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("maze", ("maze", "path to the finish")),
    ("trace", ("trace", "pre-writing", "copy line", "dotted line")),
    ("colour", ("colour", "color", "paint", "crayon")),
    ("match", ("match", "pair")),
    ("sort", ("sort", "classify", "group into")),
    ("sequence", ("sequence", "put in order", "first next", "before and after")),
    ("count", ("count", "number", "how many", "more or fewer")),
    ("compare", ("compare", "same and different", "greater", "smaller")),
    ("circle", ("circle", "choose the correct")),
    ("connect", ("connect", "join", "link")),
    ("complete", ("complete", "finish", "fill in", "missing part")),
    ("draw", ("draw", "sketch")),
    ("listen", ("listen", "sound")),
    ("speak", ("speak", "say", "tell", "talk", "show and tell", "present")),
    ("explore", ("explore", "discover", "experiment", "investigate", "test")),
    ("think", ("think", "reason", "solve", "logic", "why")),
    ("reflect", ("reflect", "how did", "what did you learn")),
    ("observe", ("observe", "look", "find", "identify", "recognise", "recognize", "notice")),
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

CHILD_INSTRUCTION_TEMPLATES = {
    "observe": "Look closely. Point to what you notice and say its name.",
    "speak": "Look at the picture. Say your answer in a clear sentence.",
    "listen": "Listen carefully. Point to the picture that matches what you hear.",
    "trace": "Trace the model carefully. Then try it once by yourself.",
    "match": "Look at both sides. Match each item to its partner.",
    "connect": "Join each item to the one that belongs with it.",
    "colour": "Name the colours. Colour the matching objects neatly.",
    "draw": "Look at the example. Draw your own idea in the space.",
    "count": "Count each group. Mark or write the correct answer.",
    "compare": "Look at both groups. Show which has more, fewer, or the same.",
    "sort": "Sort the pictures into the correct groups.",
    "sequence": "Put the pictures in the correct order.",
    "circle": "Look at each choice. Circle the correct answer.",
    "complete": "Look at the pattern or picture. Complete the missing part.",
    "maze": "Start at the beginning. Follow the path to the finish.",
    "explore": "Look, try, and notice what changes. Share what you discover.",
    "think": "Look closely. Think about the clue and choose the best answer.",
    "reflect": "Think about what you learned. Draw or tell your answer.",
    "assessment": "Complete each task independently and show what you know.",
}

GENERIC_SCENE_PREFIXES = (
    "one dominant learning scene",
    "one clear learning scene",
    "one dominant focus",
)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def unique_strings(values: list[Any]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = clean(value)
        key = text.casefold()
        if text and key not in seen:
            seen.add(key)
            output.append(text)
    return output


def contains_placeholder(value: Any) -> bool:
    text = clean(value).casefold()
    return any(phrase in text for phrase in PLACEHOLDER_PHRASES)


def nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def source_page_data(root: Path, v4: dict[str, Any]) -> tuple[dict[str, Any], str]:
    preserved = nested(v4, "preserved_source", "page_data")
    if isinstance(preserved, dict):
        return preserved, "preserved_source.page_data"
    relative = clean(nested(v4, "source_lineage", "relative_file"))
    if relative:
        path = (root / relative).resolve()
        if root.resolve() not in path.parents or not path.is_file():
            raise ValueError(f"Invalid source lineage file: {relative}")
        source = load_object(path)
        page_data = source.get("page_data")
        if isinstance(page_data, dict):
            return page_data, relative
    return {}, "v4-only"


def source_instruction(v4: dict[str, Any], page_data: dict[str, Any]) -> str:
    candidates = [
        nested(page_data, "individual_specification", "exact_child_action"),
        nested(page_data, "activity", "instruction"),
        nested(v4, "preserved_source", "approved_source_instruction"),
        nested(v4, "curriculum", "instruction"),
    ]
    for value in candidates:
        text = clean(value)
        if text and not contains_placeholder(text):
            technical = re.search(r"\bPAGE\s+\d+\s*:\s*(.+)", text, flags=re.IGNORECASE)
            return clean(technical.group(1)) if technical else text
    return ""


def explicit_activity(v4: dict[str, Any], page_data: dict[str, Any]) -> str:
    for value in (
        nested(v4, "curriculum", "activity_type"),
        nested(page_data, "activity", "type"),
        nested(page_data, "individual_specification", "activity_type"),
    ):
        candidate = clean(value).casefold().replace("_", "-")
        if candidate in LAYOUT_BY_ACTIVITY:
            return candidate
    page_type = clean(nested(v4, "page", "type")).casefold()
    if page_type == "assessment":
        return "assessment"
    return ""


def resolve_activity(v4: dict[str, Any], page_data: dict[str, Any]) -> tuple[str, str]:
    explicit = explicit_activity(v4, page_data)
    if explicit:
        return explicit, "explicit"
    text = " ".join(
        unique_strings(
            [
                nested(v4, "page", "title"),
                source_instruction(v4, page_data),
                nested(v4, "curriculum", "objective"),
                nested(v4, "preserved_source", "approved_source_instruction"),
                nested(page_data, "individual_specification", "response_space"),
                nested(page_data, "illustration", "focal_point"),
            ]
        )
    ).casefold()
    for activity, keywords in ACTIVITY_RULES:
        if any(keyword in text for keyword in keywords):
            return activity, "deterministic-source-analysis"
    if clean(nested(v4, "page", "type")).casefold() in {"review", "reflection"}:
        return "reflect", "page-type"
    raise ValueError(
        f"{clean(v4.get('prompt_id')) or 'learning page'} has no explicit or safely resolvable activity type"
    )


def refine_instruction(v4: dict[str, Any], page_data: dict[str, Any], activity: str) -> tuple[str, str]:
    instruction = source_instruction(v4, page_data)
    if instruction:
        if instruction.casefold().startswith("identify and match the three primary colours"):
            return (
                "Name red, yellow, and blue. Match each colour, then make your own colour picture.",
                "curated-primary-colours",
            )
        return instruction, "approved-source"
    return CHILD_INSTRUCTION_TEMPLATES[activity], "activity-template"


def teacher_guidance(v4: dict[str, Any], page_data: dict[str, Any], activity: str, title: str) -> dict[str, str]:
    facilitation = clean(
        nested(page_data, "teacher_prompt", "facilitation")
        or nested(v4, "curriculum", "teacher_facilitation")
    )
    questions = nested(page_data, "teacher_prompt", "questions")
    if not isinstance(questions, list):
        questions = nested(v4, "curriculum", "teacher_questions")
    question_values = unique_strings(questions if isinstance(questions, list) else [])
    question = question_values[0] if question_values else ""
    if contains_placeholder(question):
        question = ""
    if not facilitation or DEFAULT_TEACHER_PROMPT in facilitation.casefold() or contains_placeholder(facilitation):
        facilitation = {
            "observe": f"Model looking closely at the {title.lower()} picture. Invite the child to point before naming.",
            "speak": f"Model one short sentence about {title.lower()}, then invite the child to speak.",
            "listen": "Say the listening cue once, pause, and invite the child to point to the matching picture.",
            "trace": "Write or demonstrate the model once. Guide the first trace, then allow one independent attempt.",
            "match": "Name one item from each side and demonstrate one match without completing the page.",
            "connect": "Demonstrate one careful joining line, then let the child connect the remaining pairs.",
            "colour": "Name the target colours and demonstrate a small sample without colouring the child's response area.",
            "draw": "Show one simple example, discuss the idea, and leave the main drawing space for the child.",
            "count": "Touch each object once while counting aloud, then invite the child to count independently.",
            "compare": "Model comparing one pair using more, fewer, or the same.",
            "sort": "Name the groups and sort one example, then invite the child to complete the remaining choices.",
            "sequence": "Talk through the first event and invite the child to place the remaining pictures in order.",
            "circle": "Read or explain the cue and model circling one example only when the page contains a model.",
            "complete": "Point out the repeating clue and model how to find the missing part.",
            "maze": "Trace the route in the air first. Encourage slow movement from start to finish.",
            "explore": "Demonstrate the safe materials, ask for a prediction, and observe the result together.",
            "think": "Read the clue slowly and invite the child to explain the choice using a word or gesture.",
            "reflect": "Invite the child to recall the activity and accept a drawing, gesture, word, or short sentence.",
            "assessment": "Give one instruction at a time and record only what the child completes independently.",
        }[activity]
    if not question:
        question = {
            "trace": "What does your model say or show?",
            "match": "Which two belong together?",
            "connect": "What belongs with this one?",
            "colour": "Which colours will you use?",
            "draw": "What will you add to your picture?",
            "count": "How many are there?",
            "compare": "Which group has more, fewer, or the same?",
            "sort": "Why does this picture belong in that group?",
            "sequence": "What happens first? What happens next?",
            "maze": "Where will you start and finish?",
            "explore": "What do you think will happen?",
            "assessment": "Can you show what you know?",
        }.get(activity, f"What do you notice about {title.lower()}?")
    return {"model": facilitation, "question": question}


def parent_guidance(v4: dict[str, Any], page_data: dict[str, Any], activity: str, title: str) -> str:
    conversation = clean(
        nested(page_data, "parent_prompt", "conversation")
        or nested(v4, "curriculum", "parent_conversation")
    )
    home = clean(
        nested(page_data, "parent_prompt", "home_activity")
        or nested(v4, "curriculum", "parent_home_activity")
    )
    candidates = unique_strings([conversation, home])
    candidates = [
        value
        for value in candidates
        if DEFAULT_PARENT_PROMPT not in value.casefold() and not contains_placeholder(value)
    ]
    if candidates:
        return " ".join(candidates)
    verb = {
        "observe": "Find one familiar example at home and talk about what you notice.",
        "speak": "Use the same sentence during a familiar home conversation.",
        "listen": "Play a short listening-and-pointing game using familiar household sounds.",
        "trace": "Trace the shape or word once with a finger on a safe surface.",
        "match": "Match two pairs of familiar household objects.",
        "connect": "Pair familiar items that belong together and explain each choice.",
        "colour": "Find safe objects in the target colours and name them together.",
        "draw": "Draw one familiar idea together using paper and crayons.",
        "count": "Count a small group of familiar household objects.",
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
    }[activity]
    return f"For {title.lower()}, {verb[0].lower() + verb[1:]}"


def illustration_spec(v4: dict[str, Any], page_data: dict[str, Any], title: str, objective: str) -> dict[str, Any]:
    illustration = page_data.get("illustration") if isinstance(page_data.get("illustration"), dict) else {}
    curriculum = v4.get("curriculum") if isinstance(v4.get("curriculum"), dict) else {}
    scene = clean(illustration.get("scene") or curriculum.get("scene"))
    focal = clean(
        illustration.get("focal_point")
        or curriculum.get("focal_point")
        or nested(page_data, "individual_specification", "response_space")
    )
    if not scene or scene.casefold().startswith(GENERIC_SCENE_PREFIXES):
        scene = f"One clear preschool illustration for {title} that directly supports: {objective}"
    if not focal or focal.casefold().startswith(GENERIC_SCENE_PREFIXES):
        focal = f"The exact child action for {title}, with the response area kept clear."
    negatives = illustration.get("negative_constraints")
    if not isinstance(negatives, list):
        negatives = []
    page_prohibition = clean(nested(page_data, "individual_specification", "page_specific_prohibition"))
    required_objects = illustration.get("required_objects")
    if not isinstance(required_objects, list):
        required_objects = []
    if not required_objects:
        required_objects = infer_required_objects(scene)
    star_required = any(
        "star" in clean(value).casefold()
        for value in (
            scene,
            nested(page_data, "character_refs"),
            nested(v4, "design_lock", "approved_star"),
        )
    )
    star_policy = "official-asset-separate" if star_required else "not-required"
    return {
        "scene": scene,
        "focal_point": focal,
        "required_objects": unique_strings(required_objects),
        "forbidden_objects": unique_strings([*negatives, page_prohibition]),
        "protected_response_zones": ["deterministic response area below or beside the illustration"],
        "star_policy": star_policy,
        "artwork_only": True,
        "no_visible_text": True,
        "no_logo": True,
        "no_page_layout": True,
    }


def infer_required_objects(scene: str) -> list[str]:
    lowered = scene.casefold()
    candidates = (
        "child",
        "children",
        "mirror",
        "name card",
        "ball",
        "blocks",
        "book",
        "plant",
        "animal",
        "teacher",
        "table",
        "paintbrush",
        "crayons",
        "colour cards",
        "picture cards",
    )
    return [value for value in candidates if value in lowered]


def parse_visible_text(page_data: dict[str, Any]) -> str:
    return clean(nested(page_data, "individual_specification", "visible_text"))


def parse_response_space(page_data: dict[str, Any]) -> str:
    return clean(nested(page_data, "individual_specification", "response_space"))


def component(component_type: str, **kwargs: Any) -> dict[str, Any]:
    value: dict[str, Any] = {"type": component_type}
    value.update({key: item for key, item in kwargs.items() if item not in (None, "", [])})
    return value


def deterministic_components(
    activity: str,
    instruction: str,
    page_data: dict[str, Any],
    expected_response: str,
) -> list[dict[str, Any]]:
    visible_text = parse_visible_text(page_data)
    response_space = parse_response_space(page_data).casefold()
    text = f"{instruction} {visible_text} {response_space}".casefold()
    if activity == "trace":
        items: list[dict[str, Any]] = []
        model = ""
        if visible_text:
            model = visible_text.split(".")[0].strip()
        if model:
            items.append(component("model_phrase", text=model))
        items.append(component("trace_line", count=1, label="Trace"))
        if any(keyword in text for keyword in ("copy", "write", "blank copy line")):
            items.append(component("copy_line", count=1, label="Try it"))
        return items
    if activity in {"match", "connect"}:
        return [component("matching_anchors", count=infer_count(text, 4), label="Match")]
    if activity in {"colour", "draw"}:
        items = []
        if "example" in text or "demonstration" in text:
            items.append(component("model_example", label="Look"))
        items.append(component("creative_response_area", label="My work"))
        return items
    if activity in {"count", "compare"}:
        return [component("number_response_boxes", count=infer_count(text, 4), label="Answer")]
    if activity == "sort":
        return [component("sort_bins", count=infer_count(text, 2), labels=["Group 1", "Group 2"])]
    if activity == "sequence":
        return [component("sequence_slots", count=infer_count(text, 4), label="Order")]
    if activity in {"circle", "complete", "think"}:
        return [component("choice_targets", count=infer_count(text, 4), label="Choose")]
    if activity == "maze":
        return [component("maze_path", rows=7, columns=9, start="START", finish="FINISH")]
    if activity == "explore":
        return [component("prediction_observation", labels=["I think", "I noticed"])]
    if activity in {"reflect", "assessment"}:
        return [component("response_box", label="My response", lines=3)]
    if activity in {"observe", "speak", "listen"}:
        return [component("speech_response", label="Say or tell", prompt=expected_response)]
    raise ValueError(f"No deterministic component builder for activity {activity!r}")


def infer_count(text: str, default: int) -> int:
    word_numbers = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
    }
    for word, value in word_numbers.items():
        if re.search(rf"\b{word}\b", text):
            return value
    values = [int(value) for value in re.findall(r"\b([1-6])\b", text)]
    return values[0] if values else default


def build_contract(
    *,
    root: Path,
    v4_path: Path,
    illustration_path: str,
    official_logo_path: str,
    book_title_lines: list[str],
    level_name: str,
    age: str,
) -> dict[str, Any]:
    v4 = load_object(v4_path)
    page = v4.get("page")
    curriculum = v4.get("curriculum")
    book = v4.get("book")
    if not isinstance(page, dict) or not isinstance(curriculum, dict) or not isinstance(book, dict):
        raise ValueError(f"{v4_path} lacks page, curriculum, or book data")
    page_data, source_page_origin = source_page_data(root, v4)
    activity, activity_source = resolve_activity(v4, page_data)
    instruction, instruction_source = refine_instruction(v4, page_data, activity)
    title = clean(page.get("title"))
    objective = clean(curriculum.get("objective") or page_data.get("learning_objective"))
    expected_response = clean(curriculum.get("evidence") or nested(page_data, "activity", "evidence"))
    if not expected_response:
        expected_response = f"Child completes the {activity} response and explains or shows the answer."
    teacher = teacher_guidance(v4, page_data, activity, title)
    parent = parent_guidance(v4, page_data, activity, title)
    illustration = illustration_spec(v4, page_data, title, objective)
    components = deterministic_components(activity, instruction, page_data, expected_response)
    printed = page.get("printed")
    printed_visible = bool(page.get("printed_visible") and isinstance(printed, int))
    contract = {
        "contract_version": "learning-page-contract-v2.0",
        "identity": {
            "page_id": clean(v4.get("prompt_id")),
            "book_slug": clean(book.get("slug")),
            "book_title": clean(book.get("name")),
            "book_title_lines": list(book_title_lines),
            "level": level_name,
            "age": age,
            "physical_page": int(page.get("physical")),
            "page_number": int(printed) if printed_visible else 0,
            "page_number_visible": printed_visible,
            "title": title,
            "page_role": "learning",
        },
        "learning": {
            "objective": objective,
            "student_instruction": instruction,
            "expected_response": expected_response,
            "model_text": parse_visible_text(page_data),
        },
        "activity": {
            "primary": activity,
            "secondary": resolve_secondary_activities(instruction, activity),
            "response_modes": resolve_response_modes(activity, instruction),
            "layout_variant": LAYOUT_BY_ACTIVITY[activity],
            "resolution_source": activity_source,
        },
        "guidance": {
            "teacher": teacher,
            "parent_extension": parent,
        },
        "illustration": illustration,
        "deterministic_components": components,
        "prohibitions": unique_strings(
            [
                *illustration["forbidden_objects"],
                "No generated text, letters, numbers, logo, page border, worksheet mechanics, or page layout inside the illustration.",
                "No default or generated Star; use the official Star asset separately only when the contract requires it.",
                "No unrelated second activity or decorative empty response area.",
            ]
        ),
        "source_lineage": {
            "v4_file": v4_path.resolve().relative_to(root.resolve()).as_posix(),
            "v4_prompt_id": clean(v4.get("prompt_id")),
            "source_page_origin": source_page_origin,
            "instruction_source": instruction_source,
            "activity_source": activity_source,
            "source_prompt_id": clean(nested(v4, "source_lineage", "prompt_id")),
        },
        "assets": {
            "illustration_path": illustration_path,
            "official_logo_path": official_logo_path,
        },
        "qa_requirements": {
            "component_count": len(components),
            "requires_response_area": True,
            "requires_nonblank_illustration": True,
            "requires_human_semantic_review": True,
        },
    }
    validate_contract_shape(contract)
    return contract


def resolve_secondary_activities(instruction: str, primary: str) -> list[str]:
    text = instruction.casefold()
    activities: list[str] = []
    for activity, keywords in ACTIVITY_RULES:
        if activity == primary:
            continue
        if any(keyword in text for keyword in keywords):
            activities.append(activity)
    return activities[:3]


def resolve_response_modes(activity: str, instruction: str) -> list[str]:
    modes = {
        "observe": ["point", "oral"],
        "speak": ["oral"],
        "listen": ["point", "oral"],
        "trace": ["trace", "write"],
        "match": ["connect"],
        "connect": ["connect"],
        "colour": ["colour", "oral"],
        "draw": ["draw", "oral"],
        "count": ["point", "number"],
        "compare": ["point", "oral"],
        "sort": ["place", "oral"],
        "sequence": ["order", "oral"],
        "circle": ["circle"],
        "complete": ["mark", "draw"],
        "maze": ["pencil-path"],
        "explore": ["observe", "oral", "draw"],
        "think": ["choose", "oral"],
        "reflect": ["draw", "oral"],
        "assessment": ["independent-response"],
    }[activity]
    if "say" in instruction.casefold() and "oral" not in modes:
        modes.append("oral")
    return modes


def validate_contract_shape(contract: dict[str, Any]) -> None:
    spec = load_object(CONTRACT_SPEC)
    missing = [name for name in spec["required_sections"] if name not in contract]
    if missing:
        raise ValueError(f"Learning contract is missing sections: {missing}")
    activity = contract["activity"]["primary"]
    if activity not in spec["supported_primary_activities"]:
        raise ValueError(f"Unsupported primary activity: {activity}")
    layout = contract["activity"]["layout_variant"]
    layout_spec = spec["layout_variants"].get(layout)
    if not isinstance(layout_spec, dict):
        raise ValueError(f"Unsupported layout variant: {layout}")
    component_types = [item.get("type") for item in contract["deterministic_components"]]
    missing_components = [
        value for value in layout_spec["required_component_types"] if value not in component_types
    ]
    if missing_components:
        raise ValueError(f"{layout} is missing deterministic components: {missing_components}")
    illegal = [value for value in component_types if value not in layout_spec["allowed_component_types"]]
    if illegal:
        raise ValueError(f"{layout} contains unsupported components: {illegal}")
    text_fields = [
        contract["identity"]["title"],
        contract["learning"]["objective"],
        contract["learning"]["student_instruction"],
        contract["guidance"]["teacher"]["model"],
        contract["guidance"]["teacher"]["question"],
        contract["guidance"]["parent_extension"],
        contract["illustration"]["scene"],
        contract["illustration"]["focal_point"],
    ]
    bad = [value for value in text_fields if contains_placeholder(value)]
    if bad:
        raise ValueError(f"Learning contract still contains placeholder content: {bad}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-page-json", type=Path, required=True)
    parser.add_argument("--illustration-path", required=True)
    parser.add_argument("--official-logo-path", required=True)
    parser.add_argument("--book-title-lines-json", required=True)
    parser.add_argument("--level", required=True)
    parser.add_argument("--age", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    title_lines = json.loads(args.book_title_lines_json)
    if not isinstance(title_lines, list) or not title_lines:
        raise ValueError("--book-title-lines-json must contain a non-empty JSON list")
    contract = build_contract(
        root=ROOT,
        v4_path=args.source_page_json.resolve(),
        illustration_path=args.illustration_path,
        official_logo_path=args.official_logo_path,
        book_title_lines=[clean(value) for value in title_lines],
        level_name=args.level,
        age=args.age,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "NORMALISED", "page_id": contract["identity"]["page_id"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BCube learning-page normalisation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
