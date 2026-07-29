#!/usr/bin/env python3
"""Build the complete curriculum-first Communication Champions LKG runtime."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "curriculum/communication-champions/lkg/phase2-page-audit-v1.json"
PROMPTS = ROOT / "production-prompts/communication-champions/lkg/v4/phase2-illustration-prompts.json"
OUTPUT = ROOT / "runtime-contracts/lkg/communication-champions.json"


INSTRUCTIONS = {
    8: "Look at each picture. Circle every picture that shows good listening. Choose one and say: I am ready to listen.",
    9: "Listen to one instruction. Point to the matching picture, then do the action.",
    10: "Listen carefully. Do both actions in the correct order.",
    11: "Look at each picture. Say one complete sentence about it.",
    12: "Say your name and age. Ask an adult to help you write them.",
    13: "Choose any two favourite groups. Point to your choices and say both sentences.",
    14: "Draw a line from each school person to what they do. Say one sentence.",
    15: "Name each classroom object. Choose one and say: I can see a ___.",
    16: "Name each action. Draw a line to the matching action word. Say the sentence.",
    17: "Look at each pair. Circle the describing word that matches the first picture.",
    18: "Name each picture. Draw a line to its opposite.",
    19: "Look at the bear. Circle the correct position word. Say the full sentence.",
    20: "Put the word cards in order. Read each complete sentence.",
    21: "Look at each situation. Circle and say the greeting that fits.",
    22: "Look at each situation. Choose and say the polite words.",
    23: "Write 1, 2 and 3 to show how to take turns. Practise the words with a partner.",
    24: "Choose one picture. Ask for help using the sentence starter.",
    25: "Choose one group. Ask to join, then listen to the reply.",
    26: "Share one idea. Listen to your partner and give a kind reply.",
    27: "Look at the problem. Circle one fair solution and say it.",
    28: "Look at the playground. Answer the who, what and where questions.",
    29: "Look at each picture. Use the starter to ask a complete question.",
    30: "Listen to each question. Circle Yes or No, then say the full answer.",
    31: "Look at each picture. Listen to the question. Answer in one complete sentence.",
    32: "Look carefully at the park. Name what you see, describe an action and predict what happens next.",
    33: "Write 1, 2, 3 and 4 to order the pictures. Retell the story.",
    34: "Look at the four pictures. Retell who, where, what happened and how it ended.",
    35: "Look at the story beginning. Circle a sensible ending or draw another ending.",
    36: "Look at the character. Choose words that describe how the character looks and feels.",
    37: "Choose one object. Show it and answer the four speaking questions.",
    38: "Draw one piece of news. Tell who was there, what happened and how you felt.",
    39: "Choose one topic. Speak clearly to the group and use the four speaking behaviours.",
    40: "Listen to your partner. Circle and say one kind reply that matches what you heard.",
    41: "Draw one communication moment. Tick the skills you used and finish the reflection.",
    42: "Celebrate completing Communication Champions.",
    43: "Tick the communication skills you can use. Say the champion sentence.",
}


MODELS: dict[int, dict[str, Any]] = {
    8: {"picture": "body_still", "answer": "I am ready to listen.", "show_circle": True},
    9: {"instruction": "Clap.", "picture": "clap", "show_match": True},
    10: {"actions": ["Clap", "Sit"], "show_order": True},
    11: {"picture": "dog", "answer": "It is a dog."},
    12: {"answer": "My name is Sam. I am four years old."},
    13: {"choice": "red", "answer": "My favourite colour is red."},
    14: {"person": "teacher", "action": "teaching_action", "answer": "The teacher teaches us."},
    15: {"picture": "book", "answer": "I can see a book."},
    16: {"picture": "jump", "word": "jump", "answer": "The child is jumping."},
    17: {"pair": "big_small", "answer": "The first ball is big.", "show_circle": True},
    18: {"answer": "happy ↔ sad", "show_line": True},
    19: {"picture": "bear_on_box", "answer": "The bear is on the box.", "show_circle": True},
    20: {"answer": "The dog is running.", "show_order": True},
    21: {"situation": "morning", "answer": "Good morning."},
    22: {"situation": "asking for a crayon", "answer": "Please may I have the crayon?"},
    23: {"steps": ["Ask", "Wait", "Take a turn"], "numbers": [1, 2, 3]},
    24: {"situation": "open a bag", "answer": "Please help me open my bag."},
    25: {"answer": "Can I play with you?", "reply": "Yes, you can join us."},
    26: {"answer": "My idea is a tall tower.", "reply": "I like your idea."},
    27: {"answer": "Let us share the book.", "show_circle": True},
    28: {"question": "Where is the kite?", "answer": "The kite is in the sky."},
    29: {"starter": "What is", "answer": "What is the child making?"},
    30: {"question": "Is the sun yellow?", "answer": "Yes, it is.", "show_circle": True},
    31: {"question": "What do you see?", "answer": "I see a tree."},
    32: {"question": "What can you see?", "answer": "I can see children playing."},
    33: {"events": ["seed", "water", "sprout", "flower"], "numbers": [1, 2, 3, 4]},
    34: {"answer": "Mia was at the park. Her hat blew away. She found it by a tree."},
    35: {"beginning": "A child finds a lost puppy.", "ending": "The puppy finds its owner."},
    36: {"answer": "The character is happy."},
    37: {"object": "ball", "answer": "This is my ball. It is red."},
    38: {"answer": "I played with my friend. I felt happy."},
    39: {"answer": "My favourite toy is my red ball."},
    40: {"reply": "Can you tell me more?"},
    41: {"skill": "I listened", "reflection": "Today I was proud when I listened."},
    42: {"not_required": True},
    43: {"answer": "I am a communication champion!"},
}


TEACHER_CUES = {
    8: "Read one listening clue. Let the child compare the pictures before choosing.",
    9: "Say one action only; wait for the child to point and perform it.",
    10: "Say both actions once, pause, and repeat only when needed.",
    11: "Accept a short complete sentence and recast gently when a word is missing.",
    12: "Model your own introduction, then support the child's personal response.",
    13: "Let the child choose genuinely; do not suggest a favourite.",
    14: "Ask what each person does before the child draws a matching line.",
    15: "Point to one object at a time and invite the child to name it before speaking.",
    16: "Act out one word, then ask the child to find and say the matching action.",
    17: "Compare the two pictures aloud without naming the answer word.",
    18: "Name one picture and ask the child to find the picture that means the opposite.",
    19: "Ask where the bear is and encourage the full sentence, not one word only.",
    20: "Read the shuffled words slowly, then let the child decide the sentence order.",
    21: "Describe the situation first; let the child choose and say the greeting.",
    22: "Role-play each exchange with the child using a real classroom item.",
    23: "Practise ask, wait and take a turn with one shared object.",
    24: "Invite one clear help request; respond promptly and kindly.",
    25: "Take the partner role and give the friendly reply after the child asks.",
    26: "Give each child one turn to share an idea and one turn to respond.",
    27: "Ask which solution is fair and why; accept more than one fair choice.",
    28: "Ask the three questions in order and allow time to scan the scene.",
    29: "Say the starter once and let the child form the rest of the question.",
    30: "After Yes or No, prompt the child to repeat the complete answer.",
    31: "Model the first answer, then ask the remaining questions without supplying words.",
    32: "Follow the three prompts from naming to action to prediction.",
    33: "Ask what happens first; do not number any independent picture for the child.",
    34: "Point to each picture in order and use only the four retelling prompts.",
    35: "Ask what could happen next and accept any ending that fits the beginning.",
    36: "Ask for one appearance word and one feeling word.",
    37: "Let the child hold or point to one chosen object while speaking.",
    38: "Listen first; write the child's words only when support is needed.",
    39: "Use a group of three listeners and keep the speaking turn brief and positive.",
    40: "Ask the listener to repeat one detail before choosing a kind reply.",
    41: "Discuss the drawing briefly, then let the child choose the skills used.",
    42: "Complete the child's name and date, then celebrate specific communication growth.",
    43: "Review each achievement and celebrate effort without treating the checks as a test.",
}


def controls(physical: int, names: list[str]) -> dict[str, Any]:
    common = {"asset_order": names, "activity_count": len(names)}
    specific: dict[int, dict[str, Any]] = {
        8: {
            "choices": names,
            "good": names[:4],
            "distractor": names[4] if len(names) > 4 else "",
            "response": "circle",
            "display_labels": {
                "eyes_looking": "Look at the speaker",
                "ears_listening": "Listen carefully",
                "body_still": "Keep your body still",
                "waiting_turn": "Wait for your turn",
                "interrupting_distractor": "Interrupting",
            },
        },
        9: {"actions": names, "response": "point-and-perform"},
        10: {"strips": names, "response": "perform-two-actions"},
        11: {
            "sentence_frames": ["It is a ___ .", "The ball is ___ .", "The girl is ___ .", "The boy is ___ ."],
            "display_labels": {"dog": "dog", "red_ball": "ball", "girl_running": "girl", "boy_reading": "boy"},
        },
        12: {"fields": ["My name is", "I am", "years old"], "adult_supported": True},
        13: {
            "sentence_frames": [
                "My favourite colour is ___ .",
                "My favourite food is ___ .",
                "My favourite toy is ___ .",
                "My favourite activity is ___ .",
            ]
        },
        14: {"left": names[:5], "right": names[5:], "right_display": ["driving_action", "playing_action", "teaching_action", "helping_action", "leading_school_action"], "response": "match-and-say"},
        15: {"objects": names, "frame": "I can see a ___."},
        16: {"pictures": names, "words": ["read", "eat", "jump", "write", "run", "clap"], "response": "match-and-say"},
        17: {"pairs": names, "choices": [["big", "small"], ["tall", "short"], ["hot", "cold"], ["happy", "sad"]]},
        18: {
            "left": ["open_box", "full_basket", "up_arrow_object", "fast_rabbit", "clean_shoe"],
            "right": ["dirty_shoe", "slow_tortoise", "closed_box", "empty_basket", "down_arrow_object"],
            "correct_pairs": [["open_box", "closed_box"], ["full_basket", "empty_basket"], ["up_arrow_object", "down_arrow_object"], ["fast_rabbit", "slow_tortoise"], ["clean_shoe", "dirty_shoe"]],
            "response": "match-and-say",
            "display_labels": {
                "open_box": "open",
                "closed_box": "closed",
                "full_basket": "full",
                "empty_basket": "empty",
                "up_arrow_object": "up",
                "down_arrow_object": "down",
                "fast_rabbit": "fast",
                "slow_tortoise": "slow",
                "clean_shoe": "clean",
                "dirty_shoe": "dirty",
            },
        },
        19: {"scenes": names, "choices": [["in", "on"], ["on", "under"], ["under", "behind"], ["beside", "in"], ["behind", "beside"]]},
        20: {
            "sentences": [["sleeping.", "The", "cat", "is"], ["ball.", "The", "boy", "has", "a"], ["reads", "a", "book.", "The", "girl"]],
            "answers": ["The cat is sleeping.", "The boy has a ball.", "The girl reads a book."],
        },
        21: {"scenes": names, "choices": ["Good morning", "Hello", "How are you?", "Goodbye"]},
        22: {
            "scenes": names,
            "responses": ["Please may I have the crayon?", "Thank you.", "Here you are."],
            "display_labels": {"ask_crayon": "Ask for a crayon", "receive_help": "Receive help", "give_item": "Give an item"},
        },
        23: {"display_order": ["take_turn", "ask_for_turn", "wait_for_turn"], "correct_order": names, "writing_boxes": 3},
        24: {
            "scenes": names,
            "frame": "Please help me with ___.",
            "display_labels": {"open_bag_help": "Open a bag", "reach_book_help": "Reach a book", "tie_shoelace_help": "Tie a shoelace"},
        },
        25: {
            "scenes": names,
            "ask": "Can I play with you?",
            "reply": "Yes, you can join us.",
            "display_labels": {"join_building": "Build together", "join_drawing": "Draw together", "join_ball_game": "Play ball together"},
        },
        26: {"frames": ["My idea is ___.", "I like your idea."], "display_labels": {"tower_planning_pair": "Share a tower idea"}},
        27: {
            "problem": names[0],
            "solutions": names[1:],
            "response": "circle-and-say",
            "display_labels": {
                "same_toy_problem": "Both children want the same toy",
                "take_turns_solution": "Take turns",
                "timer_solution": "Use a timer",
                "other_toy_solution": "Choose another toy",
            },
        },
        28: {"scene": names[0], "questions": ["Who is on the swing?", "What is the boy holding?", "Where is the ball?"]},
        29: {"scenes": names, "starters": ["Who is", "What is", "Where is", "Why is"]},
        30: {"cards": names, "questions": ["Is the cat sleeping?", "Is the ball red?", "Can the fish fly?", "Is the girl reading?"], "choices": ["Yes", "No"]},
        31: {"cards": names, "questions": ["What do you see?", "What is she doing?", "Where is the book?"], "starters": ["I see ___.", "She is ___.", "It is ___ the table."]},
        32: {"scene": names[0], "questions": ["What can you see?", "What is happening?", "What might happen next?"]},
        33: {
            "display_order": ["flower", "seed", "sprout", "water"],
            "correct_order": names,
            "writing_boxes": 4,
            "display_labels": {"flower": "flower grows", "seed": "plant seed", "sprout": "sprout appears", "water": "water seed"},
        },
        34: {
            "events": names,
            "prompts": ["Who?", "Where?", "What happened?", "How did it end?"],
            "display_labels": {"play_with_toy": "playing with teddy", "toy_missing": "teddy is missing", "search_for_toy": "looking under the chair", "toy_found": "teddy is found"},
        },
        35: {"starters": names[:2], "endings": names[2:], "drawing_box": True},
        36: {
            "character": names[0],
            "choice_pairs": [["brown hair", "black hair"], ["pink dress", "green dress"], ["pigtails", "short hair"], ["waving", "sleeping"], ["happy", "worried"]],
            "display_labels": {"story_character": "Look closely at the character"},
        },
        37: {
            "model": names[0],
            "choices": names[1:],
            "questions": ["What is it?", "What colour is it?", "What can it do?", "Why do you like it?"],
            "display_labels": {"ball": "ball", "toy_car": "toy car", "book": "book", "teddy": "teddy bear"},
        },
        38: {"icons": names, "questions": ["Who was there?", "What happened?", "How did you feel?"], "drawing_frame": True},
        39: {
            "scene": names[0],
            "topics": ["My favourite toy", "A fun day", "Something I made"],
            "checklist": ["Stand tall", "Look up", "Speak clearly", "Listen to questions"],
        },
        40: {
            "scene": names[0],
            "responses": ["That is interesting.", "I like your idea.", "Can you tell me more?"],
            "response": "circle",
        },
        41: {"skills": ["I listened", "I asked", "I shared", "I told a story"], "drawing_frame": True, "reflection": "Today I was proud when ___."},
        42: {"certificate_statement": "for listening carefully, speaking clearly, asking questions, joining conversations and sharing stories"},
        43: {"checks": ["I listen", "I speak in sentences", "I ask questions", "I take turns", "I share ideas", "I tell stories"]},
    }
    common.update(specific[physical])
    return common


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
    pages: dict[str, Any] = {}
    for page_id, source in audit["pages"].items():
        physical = int(source["physical_page"])
        prompt_page = prompts["pages"][page_id]
        names = list(prompt_page["asset_names"])
        page_type = "certificate" if physical == 42 else "celebration" if physical == 43 else "learning_page"
        pages[page_id] = {
            "identity": {"page_id": page_id, "book_slug": "communication-champions", "level": "lkg", "physical_page": physical, "printed_page": source["printed_page"], "title": source["title"], "page_type": page_type},
            "learning": {"objective": source["objective"], "instruction": INSTRUCTIONS[physical], "expected_response": source["phase2"]["child_response_path"], "model_text": MODELS[physical], "child_thinking": "I look, listen, think, speak and respond for this exact communication task."},
            "activity": {"archetype": source["phase2"]["layout"], "mechanic": source["phase2"]["primary_mechanic"], "render_kind": f"communication-{source['phase2']['primary_mechanic']}", "response_mode": "page-specific", "mechanics": controls(physical, names)},
            "illustration": {"source_asset": f"{page_id}.png", "assets": names, "asset_crops": prompt_page["asset_crops"], "asset_meanings": prompt_page["asset_descriptions"], "requires_generated_art": True, "artwork_only": True, "crop_safe": True, "must_match_prompt": True},
            "layout": {"template": source["phase2"]["layout"], "parent_panel": False, "home_connection": False, "generic_response_panel": False, "completed_example": physical != 42, "independent_answers_unmarked": True, "object_names_visible": physical in {14, 15, 16, 18}},
            "guidance": {"teacher_cue": TEACHER_CUES[physical]},
            "validation": {"status": "READY", "allow_fallback": False, "illustration_contract_aligned": True, "curriculum_first": True, "teaching_gates": source["audit"]["release_gates"], "blocked_reasons": []},
        }
    contract = {"contract_version": "bcube-book-runtime-contract-v2-curriculum-first", "book": {"title": "Communication Champions", "slug": "communication-champions", "prefix": "CC"}, "level": "LKG", "age": "4+", "allow_fallback": False, "curriculum_first_scope": list(pages), "pages": pages}
    OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} Communication Champions pages to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
