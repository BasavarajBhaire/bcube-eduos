#!/usr/bin/env python3
"""Build the curriculum-first Phase 2 audit for Communication Champions LKG."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "production-prompts/communication-champions/lkg/v4/pages"
OUTPUT = ROOT / "curriculum/communication-champions/lkg/phase2-page-audit-v1.json"


# The mechanic is intentionally page-specific.  It is the contract used to stop
# communication pages collapsing into a generic hero illustration and response box.
MECHANICS: dict[int, tuple[str, str, str]] = {
    8: ("listening-behaviour-choice", "four-behaviour-choice-cards", "choose one good-listening behaviour and say the model phrase"),
    9: ("listen-and-perform-one-step", "six-action-listening-grid", "listen, identify the named action, then perform it"),
    10: ("listen-and-perform-two-step", "three-two-step-action-strips", "follow both actions in the spoken order"),
    11: ("picture-to-full-sentence", "four-picture-sentence-prompts", "name each picture using a complete short sentence"),
    12: ("personal-introduction", "name-age-speaking-card", "say and record own name and age with adult support"),
    13: ("personal-preference-speaking", "four-preference-choice-groups", "choose personal favourites and complete the sentence frames"),
    14: ("people-and-role-match", "people-role-matching-columns", "match each school person to their work and say one sentence"),
    15: ("classroom-vocabulary", "named-classroom-object-grid", "name classroom objects and use one in a sentence"),
    16: ("action-word-match", "action-picture-word-match", "match each action picture to its word and say the action sentence"),
    17: ("describing-word-choice", "four-comparison-pairs", "choose a describing word for each clear visual pair"),
    18: ("opposite-word-match", "five-opposite-pairs", "draw lines between opposite picture-word pairs"),
    19: ("position-word-choice", "five-bear-position-scenes", "choose the correct position word and say the full sentence"),
    20: ("sentence-ordering", "three-colour-coded-sentence-strips", "arrange each word set into a meaningful sentence"),
    21: ("greeting-situation-match", "four-greeting-situations", "match and say the greeting appropriate to each situation"),
    22: ("polite-phrase-role-play", "three-polite-exchange-scenes", "choose and say please or thank you in context"),
    23: ("turn-taking-sequence", "three-turn-taking-moments", "order and practise ask, wait and take a turn"),
    24: ("help-request-role-play", "three-help-situations", "choose a situation and ask for help using the sentence frame"),
    25: ("join-play-role-play", "three-play-group-scenes", "choose a group, ask to join and listen to the reply"),
    26: ("idea-share-and-reply", "paired-planning-scene", "share one idea and respond kindly to a partner's idea"),
    27: ("social-problem-choice", "problem-scene-three-solutions", "choose a fair solution and say it to a partner"),
    28: ("who-what-where", "playground-scene-three-questions", "answer who, what and where from one controlled scene"),
    29: ("form-a-question", "four-question-starter-scenes", "use each picture and starter to ask a complete question"),
    30: ("yes-no-and-extend", "four-picture-question-cards", "answer yes or no and repeat the complete response"),
    31: ("answer-in-a-sentence", "three-picture-question-pairs", "answer each picture question using a complete short sentence"),
    32: ("guided-picture-talk", "rich-park-scene-prompt-strip", "observe, name details and predict what might happen next"),
    33: ("story-sequence-and-retell", "four-shuffled-story-cards", "number four events and retell them in order"),
    34: ("four-picture-retell", "four-event-story-strip", "retell who, where, what happened and how it ended"),
    35: ("choose-story-ending", "story-starter-ending-choices-draw", "choose a logical ending or draw another one"),
    36: ("character-description", "character-with-attribute-choices", "choose visual details and describe the character"),
    37: ("show-and-tell", "object-choice-speaking-card", "choose one familiar object and answer four speaking prompts"),
    38: ("personal-news-journal", "drawing-frame-three-oral-prompts", "draw one event and tell who, what and feeling"),
    39: ("small-group-speaking", "speaker-audience-checklist", "speak to a small group and use the four speaking behaviours"),
    40: ("listen-and-kindly-respond", "peer-sharing-response-choices", "listen to a peer and choose a kind relevant reply"),
    41: ("communication-reflection", "drawing-frame-four-skill-checks", "mark practised skills and complete one reflection"),
    42: ("certificate", "deterministic-certificate", "record completion; no child learning task"),
    43: ("achievement-celebration", "achievement-badge-six-checks", "review and celebrate six communication achievements"),
}


def extract_section(text: str, start: str, endings: tuple[str, ...]) -> str:
    match = re.search(re.escape(start) + r"(.*?)(?:" + "|".join(map(re.escape, endings)) + r")", text, re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def main() -> int:
    pages: dict[str, dict[str, object]] = {}
    for physical in range(8, 44):
        matches = sorted(SOURCE.glob(f"CC-LKG-V4-P{physical:03d}-*.json"))
        if len(matches) != 1:
            raise SystemExit(f"Expected one source for P{physical:03d}; found {len(matches)}")
        source_path = matches[0]
        source = json.loads(source_path.read_text(encoding="utf-8"))
        page_id = source["prompt_id"]
        curriculum = source["curriculum"]
        approved = source["preserved_source"]["approved_source_instruction"]
        mechanic, layout, child_path = MECHANICS[physical]
        page_type = source["page"]["type"]
        pages[page_id] = {
            "physical_page": physical,
            "printed_page": source["page"]["printed"],
            "title": source["page"]["title"],
            "page_type": page_type,
            "objective": curriculum["objective"],
            "source_instruction": curriculum["instruction"],
            "approved_page_direction": extract_section(
                approved,
                "PAGE-SPECIFIC ART DIRECTION:",
                ("INDIVIDUAL PAGE EXECUTION BLUEPRINT:", "OFFICIAL STAR MASCOT:"),
            ),
            "phase2": {
                "primary_mechanic": mechanic,
                "layout": layout,
                "child_response_path": child_path,
                "completed_example_required": page_type == "activity_page",
                "parent_or_home_panel": False,
                "generic_response_box": False,
                "teacher_cue": "one short, page-specific facilitation action",
                "illustration_policy": "content-aligned artwork only; text and response mechanics deterministic",
            },
            "audit": {
                "status": "REBUILD_REQUIRED",
                "reason": "The V4 source is structurally complete but has not been converted into a task-specific Phase 2 runtime page.",
                "release_gates": [
                    "learning goal, instruction, model and independent task use the same mechanic",
                    "completed example visibly demonstrates the child action without solving the independent task",
                    "every response has a clear place to point, circle, match, order, draw, mark or speak",
                    "no person, object or response space is cropped",
                    "text is comfortably readable at A4 print size",
                    "no parent or homework panel",
                ],
            },
            "source_file": source_path.relative_to(ROOT).as_posix(),
        }

    output = {
        "version": "communication-champions-lkg-phase2-audit-v1",
        "book": "Communication Champions",
        "level": "LKG (4+)",
        "scope": "CC-LKG-V4-P008 through CC-LKG-V4-P043",
        "learning_and_closing_page_count": len(pages),
        "current_runtime_page_count_before_rebuild": 1,
        "locked_book_rules": [
            "consistent BCube header and footer with task-specific learning area",
            "no repeated generic activity box",
            "no parent or home connection panel",
            "one compact page-specific teacher cue",
            "model the exact child action once, then leave independent responses unanswered",
            "use visible object or character names when they support vocabulary and reading",
            "use separated prompt and choice areas for selection tasks",
            "vary correct-answer positions and display order",
            "provide large purposeful response spaces",
            "fit artwork from visible bounds with safe padding; never crop key content",
        ],
        "pages": pages,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} audited pages to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
