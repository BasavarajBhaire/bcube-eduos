#!/usr/bin/env python3
"""Build content-aligned illustration prompts for Communication Champions LKG."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "curriculum/communication-champions/lkg/phase2-page-audit-v1.json"
OUTPUT = ROOT / "production-prompts/communication-champions/lkg/v4/phase2-illustration-prompts.json"
PROMPT_DIR = ROOT / "production-prompts/communication-champions/lkg/v4/phase2-illustration-prompts/pages"


ASSETS: dict[int, dict[str, str]] = {
    8: {"eyes_looking": "child's eyes looking towards a speaker", "ears_listening": "child cupping one ear while listening", "body_still": "child sitting with calm still hands", "waiting_turn": "child waiting with one hand lowered", "interrupting_distractor": "mild incorrect example of a child interrupting"},
    9: {"clap": "child clapping", "stand": "child standing", "sit": "child sitting", "point": "child pointing", "touch_head": "child touching own head", "show_pencil": "child holding up one pencil"},
    10: {"clap_then_sit": "two clearly separated moments: clap, then sit", "pick_pencil_then_point_book": "two clearly separated moments: pick up a pencil, then point to a book", "stand_then_touch_head": "two clearly separated moments: stand, then touch head"},
    11: {"dog": "one friendly dog", "red_ball": "one red ball", "girl_running": "girl running", "boy_reading": "boy reading an open book"},
    12: {"introduction_child": "one confident LKG child facing forward and introducing themself with a friendly gesture"},
    13: {"colour_choices": "four large colour swatches without words", "food_choices": "four familiar foods", "toy_choices": "four familiar toys", "activity_choices": "four familiar child activities"},
    14: {"teacher": "school teacher", "principal": "school principal", "helper": "school helper", "driver": "school bus driver", "friend": "class friend", "teaching_action": "adult teaching children", "leading_school_action": "principal welcoming children", "helping_action": "helper arranging materials", "driving_action": "driver beside a school bus", "playing_action": "two friends sharing a game"},
    15: {"book": "one book", "pencil": "one pencil", "eraser": "one eraser", "school_bag": "one school bag", "chair": "one chair", "board": "one classroom board", "crayons": "small box of crayons"},
    16: {"jump": "child jumping", "run": "child running", "clap": "child clapping", "read": "child reading", "write": "child writing", "eat": "child eating"},
    17: {"big_small": "one big ball and one small matching ball", "tall_short": "one tall tree and one short matching tree", "hot_cold": "steaming warm drink and cold drink with ice", "happy_sad": "same child shown happy and sad"},
    18: {"open_box": "one open box", "closed_box": "one matching closed box", "full_basket": "one basket filled with apples", "empty_basket": "one matching empty basket", "up_arrow_object": "one toy rocket pointing up", "down_arrow_object": "one matching toy rocket pointing down", "fast_rabbit": "one rabbit running fast", "slow_tortoise": "one tortoise walking slowly", "clean_shoe": "one clean shoe", "dirty_shoe": "one matching muddy shoe"},
    19: {"bear_in_box": "toy bear inside a box", "bear_on_box": "toy bear on top of a box", "bear_under_box": "toy bear under a raised box", "bear_beside_box": "toy bear beside a box", "bear_behind_box": "toy bear partly behind a box but still recognisable"},
    20: {"cat_sleeping": "cat sleeping", "boy_has_ball": "boy holding a ball", "girl_reads_book": "girl reading a book"},
    21: {"morning_greeting": "child greeting an adult in the morning", "friend_greeting": "two friends meeting", "how_are_you": "one child kindly checking how a friend feels", "goodbye": "two children waving goodbye"},
    22: {"ask_crayon": "child politely asking another child for a crayon", "receive_help": "child receiving help", "give_item": "child giving an item to a friend"},
    23: {"ask_for_turn": "child asking to join a block game", "wait_for_turn": "child waiting calmly while friend plays", "take_turn": "child taking a turn with the blocks"},
    24: {"open_bag_help": "child needing help opening a school bag", "reach_book_help": "child needing help reaching a book", "tie_shoelace_help": "child needing help tying a shoelace"},
    25: {"join_building": "two children building and one child asking to join", "join_drawing": "two children drawing and one child asking to join", "join_ball_game": "two children playing ball and one child asking to join"},
    26: {"tower_planning_pair": "two children looking at blocks and respectfully sharing ideas for a tower"},
    27: {"same_toy_problem": "two children both reaching for the same toy without aggression", "take_turns_solution": "children taking turns with the toy", "timer_solution": "children using a simple sand timer", "other_toy_solution": "one child choosing another appealing toy"},
    28: {"playground_scene": "controlled playground scene with a girl on a swing, boy holding a kite and a ball under a bench"},
    29: {"who_scene": "adult helping a child", "what_scene": "child making a paper boat", "where_scene": "teddy hidden beside a bed", "why_scene": "child holding an umbrella in rain"},
    30: {"sleeping_cat": "cat clearly sleeping", "red_ball": "one red ball", "flying_fish": "fish in water, clearly not flying", "reading_girl": "girl reading a book"},
    31: {"see_bus": "one bus in a simple setting", "girl_drawing": "girl drawing", "book_on_table": "book clearly on top of a table"},
    32: {"park_scene": "rich but controlled park scene with eight to ten clear people, actions and familiar objects"},
    33: {"seed": "child placing a seed in soil", "water": "child watering the planted seed", "sprout": "small green sprout emerging", "flower": "grown flowering plant"},
    34: {"play_with_toy": "child playing with a favourite toy", "toy_missing": "child noticing the toy is missing", "search_for_toy": "child looking under a chair for the toy", "toy_found": "child happily finding the toy under the chair"},
    35: {"starter_one": "child sees a small lost puppy near a park gate", "starter_two": "child approaches the puppy carefully with an adult nearby", "ending_owner": "puppy reunited with its owner", "ending_safe_help": "child and adult take the puppy to a safe help desk"},
    36: {"story_character": "one friendly child story character with clear clothing, action and facial expression"},
    37: {"show_tell_child": "child confidently holding one familiar object for show and tell", "ball": "one ball", "toy_car": "one toy car", "book": "one picture book", "teddy": "one teddy bear"},
    38: {"who_icon": "simple icon of two familiar people", "event_icon": "simple icon of an event or action", "feeling_icon": "simple happy-neutral-sad feeling faces"},
    39: {"small_group_speaker": "one child speaking to three attentive classmates with natural eye contact and respectful posture"},
    40: {"peer_sharing_pair": "one child sharing an idea while another child listens attentively and prepares to respond"},
    41: {"listened_icon": "child listening", "asked_icon": "child asking a question", "shared_icon": "child sharing an idea", "story_icon": "child telling a short story"},
    42: {"achievement_badge": "premium communication achievement badge without words", "trophy": "friendly gold trophy", "confetti": "compact crop-safe celebratory confetti cluster"},
    43: {"champion_child": "confident LKG child celebrating communication skills with small listening, speaking and storytelling symbols"},
}


def crop_grid(names: list[str]) -> dict[str, dict[str, float]]:
    count = len(names)
    if count == 1:
        return {names[0]: {"x": 0.06, "y": 0.05, "w": 0.88, "h": 0.90, "padding": 0.012}}
    cols = 2 if count <= 12 else 3
    rows = math.ceil(count / cols)
    gap_x, gap_y = 0.055, 0.04
    left, top, right, bottom = 0.055, 0.035, 0.055, 0.035
    width = (1 - left - right - gap_x * (cols - 1)) / cols
    height = (1 - top - bottom - gap_y * (rows - 1)) / rows
    crops: dict[str, dict[str, float]] = {}
    for index, name in enumerate(names):
        row, col = divmod(index, cols)
        crops[name] = {
            "x": round(left + col * (width + gap_x), 6),
            "y": round(top + row * (height + gap_y), 6),
            "w": round(width, 6),
            "h": round(height, 6),
            "padding": 0.008,
        }
    return crops


def layout_sentence(count: int) -> str:
    if count == 1:
        return "Create one large coherent illustration centred on the canvas with generous pure-white safe margins."
    cols = 2 if count <= 12 else 3
    rows = math.ceil(count / cols)
    return f"Arrange the assets in a strict {cols}-column by {rows}-row extraction grid in the numbered order below."


def make_prompt(page_id: str, page: dict[str, Any], assets: dict[str, str]) -> str:
    exact = "\n".join(f"{i}. {name}: {description}." for i, (name, description) in enumerate(assets.items(), 1))
    return f"""BCube Content-Aligned Illustration Asset Prompt — {page_id}

BOOK AND LEVEL
Book: Communication Champions
Level: LKG (4+)
Exact page title: {page['title']}
Learning objective: {page['objective']}
Exact child response path: {page['phase2']['child_response_path']}.

ILLUSTRATION ROLE — LOCKED
Create only the raw illustration artwork required by the exact communication activity. Do not create the workbook page. The publishing engine will add every word, object name, question, sentence starter, model example, separator, response control, writing line, teacher cue, logo and page number.

EXACT OUTPUT
Create exactly {len(assets)} named visual asset(s), each appearing once:
{exact}

LAYOUT LOCK
{layout_sentence(len(assets))}
Keep wide pure-white gaps. No asset may touch, overlap or cross a cell boundary. Keep every person, hand, face, object and relationship fully visible with generous safe padding.

COMMUNICATION EVIDENCE
Expressions, gaze, gesture, posture and turn-taking must make the speaking or listening action obvious. Use only the people, objects and relationships required for this page. Children must look LKG age, approximately 4–5 years.

STYLE
Premium commercial preschool-publishing quality; large recognisable forms; thick clean rounded outlines; natural expressive faces; correct anatomy and hands; bright controlled colours; subtle dimensional shading; pure white background.

TEXT AND WORKSHEET LOCK
No visible words, letters, numerals, handwriting, labels, captions, speech bubbles, instructions, answer marks, circles, ticks, matching lines, arrows, cards with writing space, page title, logo, publisher mark, page number, watermark, QR code or BCube Star mascot.

FAIL CONDITIONS
Reject missing, duplicated, cropped, combined or misordered assets; generic classroom groups; teacher-led scenes unless explicitly required; decorative filler; completed answers; worksheet UI; dark backgrounds; or artwork that supports only the title but not the exact child response path.
"""


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    pages: dict[str, Any] = {}
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    index_lines = [
        "# Communication Champions — LKG Phase 2 Illustration Prompts",
        "",
        "Generate one page asset sheet from each prompt. Keep the exact output filename shown below.",
        "The renderer will add all text, model examples, response mechanics, teacher cues and branding.",
        "",
    ]
    for page_id, page in audit["pages"].items():
        physical = int(page["physical_page"])
        assets = ASSETS[physical]
        prompt = make_prompt(page_id, page, assets)
        prompt_path = PROMPT_DIR / f"{page_id}.txt"
        prompt_path.write_text(prompt, encoding="utf-8")
        pages[page_id] = {
            "title": page["title"],
            "output_filename": f"{page_id}.png",
            "asset_names": list(assets),
            "asset_descriptions": assets,
            "asset_crops": crop_grid(list(assets)),
            "prompt_file": prompt_path.relative_to(ROOT).as_posix(),
            "prompt": prompt,
            "status": "READY_FOR_ILLUSTRATION",
        }
        index_lines.append(f"- `{page_id}.txt` → `{page_id}.png` — {page['title']}")
    document = {
        "version": "communication-champions-phase2-illustration-prompts-v1",
        "book": "Communication Champions",
        "level": "LKG (4+)",
        "source_audit": AUDIT.relative_to(ROOT).as_posix(),
        "policy": "Content-aligned artwork only; deterministic text and mechanics; no generic fallback.",
        "pages": pages,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (PROMPT_DIR.parent / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} illustration prompts to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
