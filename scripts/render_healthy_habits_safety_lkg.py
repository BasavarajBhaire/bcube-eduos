#!/usr/bin/env python3
"""Render Healthy Habits & Safety LKG content pages P008-P043.

The canonical V4 prompt packages remain the source for identity, titles,
objectives, facilitation, home links and physical/printed numbering. This
renderer supplies page-specific, response-safe workbook mechanics and
premium illustration sheets. Front matter P001-P007 and back cover
P044 are intentionally outside the default and production scope.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "production-prompts/healthy-habits-safety/lkg/v4/pages"
TEXT_ENGINE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
PREMIUM_ROOT = ROOT / "assets/illustrations/healthy-habits-safety/lkg"
MY_WORLD_PREMIUM_ROOT = ROOT / "assets/illustrations/my-world-general-awareness/lkg"
STEM_PREMIUM_ROOT = ROOT / "assets/illustrations/stem-explorers/lkg"
WIDTH, HEIGHT = 2480, 3508
PAGES = tuple(range(8, 44))

NAVY = "#123F72"
PURPLE = "#7E57C2"
SOFT_PURPLE = "#A077E8"
BLUE = "#E8F4FF"
GOLD = "#FFF4C6"
GREEN = "#EAF8E8"
INK = "#31353A"
ORANGE = "#F29B38"
RED = "#F05A47"
TEAL = "#45A7A0"
PINK = "#F8E7F1"

ACTIVE_PAGE: int | None = None
ACTIVE_CANVAS: Image.Image | None = None
SHEET_CACHE: dict[Path, Image.Image] = {}


def sort_page(instruction, groups, counts, items, model):
    return {"layout": "sort", "instruction": instruction, "groups": groups,
            "counts": counts, "items": items, "model": model}


def match_page(instruction, sources, choices, model):
    return {"layout": "match", "instruction": instruction, "sources": sources,
            "choices": choices, "model": model}


def sequence_page(instruction, items, model):
    return {"layout": "sequence", "instruction": instruction,
            "items": items, "model": model}


def pairs_page(instruction, pairs, model):
    return {"layout": "pairs", "instruction": instruction,
            "pairs": pairs, "model": model}


ACTIVITIES = {
    8: sort_page(
        "Name each picture. Write its number under BODY PARTS or HEALTHY HABITS.",
        ["BODY PARTS", "HEALTHY HABITS"], [4, 4],
        ["eyes", "ears", "hands", "legs", "eat healthy food", "drink water", "exercise", "sleep well"],
        ("arms", "BODY PART", "Arms are body parts.")),
    9: match_page(
        "Match each sense organ with what it helps us notice. Write the matching letter.",
        ["ears", "nose", "tongue", "skin"],
        ["hear a bell", "smell a flower", "taste a lemon", "feel a soft toy"],
        ("eyes", "SEE", "Eyes help us see.")),
    10: sequence_page(
        "Look at the brushing steps. Write 1 to 4 to show the correct order.",
        ["rinse the mouth", "put toothpaste on brush", "brush the tongue", "brush every tooth"],
        ("wash hands first", "FIRST", "Clean hands help us begin.")),
    11: sequence_page(
        "Look at the handwashing steps. Write 1 to 6 to show the correct order.",
        ["rub palms", "dry hands", "wet hands", "rinse hands", "use soap", "clean between fingers"],
        ("roll up sleeves", "GET READY", "Roll up sleeves before washing.")),
    12: sort_page(
        "Name each item. Write its number under BATH ITEMS or NOT FOR BATH.",
        ["BATH ITEMS", "NOT FOR BATH"], [4, 4],
        ["soap", "towel", "shampoo", "bucket", "spoon", "pencil", "toy car", "shoe"],
        ("sponge", "BATH ITEM", "A sponge can help us wash.")),
    13: sort_page(
        "Name each food. Write its number under HEALTHY or EAT LESS OFTEN.",
        ["HEALTHY", "EAT LESS OFTEN"], [4, 4],
        ["apple", "carrot", "milk", "rice and dal", "chips", "sweets", "fizzy drink", "burger"],
        ("banana", "HEALTHY", "A banana is a healthy food.")),
    14: sort_page(
        "Look at each picture. Write its number under DRINK WATER or ASK AN ADULT.",
        ["DRINK WATER", "ASK AN ADULT"], [4, 4],
        ["after play", "with a meal", "on a hot day", "after waking", "unknown bottle", "water smells odd", "outdoor tap", "uncovered cup"],
        ("clean water bottle", "DRINK WATER", "Choose clean drinking water.")),
    15: match_page(
        "Match each exercise with how it helps the body. Write the matching letter.",
        ["running", "stretching", "jumping", "balancing"],
        ["strong heart", "flexible body", "strong legs", "steady body"],
        ("marching", "WARM UP", "Marching gently warms the body.")),
    16: sequence_page(
        "Look at the bedtime routine. Write 1 to 6 to show a healthy order.",
        ["read a story", "turn off the screen", "go to sleep", "brush teeth", "put toys away", "wear pyjamas"],
        ("dim the light", "BEDTIME", "A quiet room helps us get ready.")),
    17: sort_page(
        "Name each picture. Write its number under CLEAN or NEEDS WASHING.",
        ["CLEAN", "NEEDS WASHING"], [4, 4],
        ["fresh uniform", "clean socks", "folded shirt", "fresh pyjamas", "muddy shorts", "sweaty shirt", "stained dress", "wet socks"],
        ("clean cap", "CLEAN", "Clean clothes feel fresh.")),
    18: match_page(
        "Match each clinic picture with what it does. Write the matching letter.",
        ["doctor", "nurse", "thermometer", "stethoscope"],
        ["checks the body", "helps with care", "checks temperature", "listens to the heart"],
        ("bandage", "COVERS A CUT", "A bandage protects a small cut.")),
    19: sort_page(
        "Review the healthy habits. Write each picture number in the matching group.",
        ["CLEAN BODY", "HEALTHY FOOD", "ACTIVE BODY"], [3, 3, 2],
        ["brush teeth", "wash hands", "take a bath", "apple", "drink water", "vegetables", "run", "stretch"],
        ("sleep", "REST", "Rest helps the body grow.")),
    20: pairs_page(
        "Look at each pair. Circle the SAFE action.",
        [("tell an adult about a spill", "run on a wet floor"),
         ("use a step stool with an adult", "climb a tall shelf"),
         ("leave toys on the floor", "put toys away"),
         ("taste unknown tablets", "ask an adult for medicine")],
        ("hold the handrail", "SAFE", "Holding the handrail is safe.")),
    21: sort_page(
        "Name each kitchen picture. Write its number under ADULT ONLY or SAFE TO HELP.",
        ["ADULT ONLY", "SAFE TO HELP"], [4, 4],
        ["hot pan", "sharp knife", "lit stove", "hot kettle", "wash vegetables", "set the table", "mix a cold salad", "carry napkins"],
        ("open the oven", "ADULT ONLY", "An adult opens a hot oven.")),
    22: pairs_page(
        "Look at each pair. Circle the SAFE bathroom habit.",
        [("walk on a dry floor", "run on a wet floor"),
         ("climb into a wet tub", "use a bath mat"),
         ("jump into very hot water", "an adult checks the water"),
         ("keep electrical items outside", "use a device near the sink")],
        ("wipe up splashes", "SAFE", "A dry floor helps prevent slips.")),
    23: pairs_page(
        "Look at each pair. Circle the SAFE road action.",
        [("cross at a zebra crossing with an adult", "cross between parked cars"),
         ("cross on a red light", "wait for the green walk signal"),
         ("walk on the footpath", "walk in the road"),
         ("ride without a helmet", "wear a bicycle helmet")],
        ("stop at the kerb", "SAFE", "Stop and look before crossing.")),
    24: pairs_page(
        "Look at each pair. Circle the action that keeps the child SAFE.",
        [("stay with a trusted adult", "go away with an unfamiliar person"),
         ("keep an unsafe secret", "say NO and tell a trusted adult"),
         ("ask before accepting a gift", "take sweets from an unfamiliar person"),
         ("share the home address", "use the family safety password")],
        ("call my trusted adult", "SAFE", "A trusted adult can help.")),
    25: pairs_page(
        "My body belongs to me. Circle the choice that is SAFE and RESPECTFUL.",
        [("say NO to an unwanted hug", "stay silent when uncomfortable"),
         ("keep a touch secret", "tell a trusted adult"),
         ("doctor check with caregiver present", "go alone with an unfamiliar adult"),
         ("touch without asking", "ask before a hug or high-five")],
        ("say STOP", "MY CHOICE", "I can say STOP and move away.")),
    26: sequence_page(
        "Look at the fire-safety steps. Write 1 to 4 to show the safe order.",
        ["meet outside", "notice smoke", "leave by a safe exit", "tell an adult"],
        ("do not hide", "MOVE AWAY", "Move away from smoke and fire.")),
    27: match_page(
        "Match each emergency helper with the job. Write the matching letter.",
        ["firefighter", "police officer", "doctor", "ambulance"],
        ["puts out fires", "helps a lost child", "treats an injury", "takes a patient to hospital"],
        ("nurse", "CARES", "A nurse helps care for patients.")),
    28: pairs_page(
        "Look at each pair. Circle the SAFE playground action.",
        [("wait for a turn on the slide", "push on the slide"),
         ("stand near a moving swing", "sit and hold the swing"),
         ("jump from the top", "use the climbing frame carefully"),
         ("tell an adult about broken equipment", "play on broken equipment")],
        ("wear shoes", "SAFE", "Shoes protect our feet at play.")),
    29: pairs_page(
        "Look at each pair. Circle the SAFE screen-time choice.",
        [("use a screen with an adult nearby", "use a screen alone for a long time"),
         ("share a password", "keep personal information private"),
         ("sit at a screen all day", "take a movement break"),
         ("tell an adult about a strange message", "reply to an unknown person")],
        ("ask before going online", "SAFE", "An adult helps us use screens safely.")),
    30: match_page(
        "Match each feeling with a healthy response. Write the matching letter.",
        ["happy", "sad", "angry", "worried"],
        ["smile and share", "talk to a trusted adult", "breathe slowly", "ask for help"],
        ("excited", "MOVE GENTLY", "I can move safely when excited.")),
    31: pairs_page(
        "Look at each pair. Circle the KIND action.",
        [("invite someone to play", "leave someone out"),
         ("laugh at a mistake", "help a friend try again"),
         ("use gentle words", "shout hurtful words"),
         ("walk past a fallen book", "pick up a fallen book")],
        ("say thank you", "KIND", "Kind words help others feel good.")),
    32: sort_page(
        "Look at each picture. Write its number under CARING or NOT CARING.",
        ["CARING", "NOT CARING"], [4, 4],
        ["share crayons", "help tidy up", "comfort a friend", "take turns", "grab a toy", "laugh at a fall", "refuse to help", "push into a queue"],
        ("invite a friend", "CARING", "Inviting a friend shows care.")),
    33: sequence_page(
        "Look at the daily routine. Write 1 to 8 to show a healthy order.",
        ["play outside", "wake up", "eat dinner", "brush in the morning", "go to sleep", "eat breakfast", "brush at bedtime", "go to school"],
        ("prepare the school bag", "GET READY", "Getting ready makes mornings calm.")),
    34: sort_page(
        "Look at each picture. Write its number under KEEP CLEAN or MAKE DIRTY.",
        ["KEEP CLEAN", "MAKE DIRTY"], [4, 4],
        ["use a dustbin", "sweep the floor", "reuse a bottle", "pick up litter", "drop litter", "spill food", "leave rubbish", "scribble on a wall"],
        ("close the bin lid", "KEEP CLEAN", "A closed bin keeps the area tidy.")),
    35: sort_page(
        "Look at each picture. Write its number under STOPS GERMS or SPREADS GERMS.",
        ["STOPS GERMS", "SPREADS GERMS"], [4, 4],
        ["wash hands", "cover a cough", "use a tissue", "clean a table", "cough openly", "share a used tissue", "touch food with dirty hands", "leave a spill"],
        ("use soap", "STOPS GERMS", "Soap helps wash germs away.")),
    36: pairs_page(
        "Look at each pair. Circle the HEALTHY choice.",
        [("drink water", "drink fizzy drink"),
         ("watch a screen all day", "play outside"),
         ("eat many sweets", "eat fruit"),
         ("sleep on time", "stay awake very late")],
        ("wash hands before eating", "HEALTHY", "Clean hands are a healthy choice.")),
    37: sort_page(
        "Review the safety rules. Write each picture number in the matching group.",
        ["HOME", "ROAD", "PERSONAL", "FIRE"], [2, 2, 2, 2],
        ["put toys away", "ask an adult for medicine", "use a zebra crossing", "wear a helmet", "say no", "tell a trusted adult", "leave smoke", "meet outside"],
        ("wipe up a spill", "HOME", "A dry floor makes home safer.")),
    38: {"layout": "journal", "instruction": "Draw one healthy habit you practised this week. Then tell an adult about it.",
         "model": ("drink water", "MY HABIT", "I drank clean water this week.")},
    39: {"layout": "promise", "instruction": "Tick the habits you promise to practise. Complete the sentence with an adult.",
         "model": ("wash hands", "I PROMISE", "I promise to wash my hands.")},
    40: {"layout": "presentation", "instruction": "Choose a favourite healthy habit. Draw it, then tell the class why it helps.",
         "model": ("exercise", "MY FAVOURITE", "Exercise helps my body grow strong.")},
    41: {"layout": "certificate", "instruction": "Celebrate the learner's healthy and safe choices."},
    42: {"layout": "badges", "instruction": "Colour the four badges. Tick the healthy-and-safe skill you are most proud of.",
         "model": ("brush teeth", "HYGIENE", "Brushing teeth earns a hygiene badge.")},
    43: {"layout": "celebration", "instruction": "Celebrate what you can do to stay healthy and safe."},
}


def hh_asset(page: int, index: int) -> tuple[Path, int, int, int]:
    return (PREMIUM_ROOT / f"HH-LKG-V4-P{page:03d}-assets.png", 3, 3, index)


def mw_asset(page: int, columns: int, rows: int, index: int) -> tuple[Path, int, int, int]:
    return (MY_WORLD_PREMIUM_ROOT / f"MW-LKG-V4-P{page:03d}-assets.png", columns, rows, index)


def stem_asset(page: int, columns: int, rows: int, index: int) -> tuple[Path, int, int, int]:
    return (STEM_PREMIUM_ROOT / f"ST-LKG-V4-P{page:03d}.png", columns, rows, index)


def activity_labels(definition: dict) -> list[str]:
    """Return the labels that need a premium illustration, in sheet order."""
    labels = [definition["model"][0]] if "model" in definition else []
    layout = definition["layout"]
    if layout in {"sort", "sequence"}:
        labels.extend(definition["items"])
    elif layout == "match":
        labels.extend(definition["sources"] + definition["choices"])
    elif layout == "pairs":
        labels.extend(item for pair in definition["pairs"] for item in pair)
    return labels


ILLUSTRATION_MAP: dict[tuple[int, str], tuple[Path, int, int, int]] = {}

# Pages P009-P031 use their own page-specific 3x3 premium illustration sh×m9ÖÚ$z{-®éÜj×¢6öÇ3ÓB–bÆVâ†—FV×2’–âƒ‚Â’VÇ6R2–bÆVâ†—FV×2“ÓÓbVÇ6R ¢&÷w3ÖÖF‚æ6V–Â†ÆVâ†—FV×2’ö6öÇ2“²vÓ#C²ÆVgCÓs²&–v‡CÓ#3²F÷Ó²&÷GFöÓÓ3“ ¢7sÒ‡&–v‡BÖÆVgBÖv¢†6öÇ2Ó’’òö6öÇ3²6ƒÒ†&÷GFöÒ×F÷Öv¢‡&÷w2Ó’’ò÷&÷w0¢f÷"’ÆÆ&VÂ–âVçVÖW&FR†—FV×2“ ¢&÷rÆ6öÃÖF—fÖöB†’Æ6öÇ2“²ƒÖÆVgB¶6öÂ¢†7r¶v“²“×F÷·&÷r¢†6‚¶v¢6&B†G&rÇFW‡BÅ·ƒÇ“Çƒ¶7rÇ“¶6…ÒÆÆ&VÂ¢G&rç&÷VæFVE÷&V7FævÆR…·ƒ¶7rÓ"Ç“³‚Çƒ¶7rÓ#BÇ“³%ÒÇ&F—W3ÓBÆf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÕU%ÄRÇv–GFƒÓB¢f—GFVB‡FW‡BÆG&rÂ&÷&FW""Å·ƒ¶7rÓ#Ç“³"Çƒ¶7rÓbÇ“³3eÒÇ6—¦SÓrÆÖ–æ–×VÓÓBÆ6öÆ÷W#Ò"3cCsC„""Æ&öÆCÕG'VR  ¦FVb&VæFW%÷—'2†G&rÇFW‡BÆFVf–æ—F–öâ“ ¢—'3ÖFVf–æ—F–öå²'—'2%Ó²F÷Ó“C²&÷GFöÓÓ3“²vÓƒ²†VF–æsÓS@¢–ç7G'V7F–öãÖFVf–æ—F–öå²&–ç7G'V7F–öâ%ÒçWW"‚¢–b$´”äB"–â–ç7G'V7F–öã ¢&÷u÷&ö×CÒ$4•$4ÄRD„R´”äB4„ô”4Râ ¢VÆ–b%$U5T5DeTÂ"–â–ç7G'V7F–öã ¢&÷u÷&ö×CÒ$4•$4ÄRD„R4dRäB$U5T5DeTÂ4„ô”4Râ ¢VÆ–b$„TÅD…’"–â–ç7G'V7F–öã ¢&÷u÷&ö×CÒ$4•$4ÄRD„R„TÅD…’4„ô”4Râ ¢VÇ6S ¢&÷u÷&ö×CÒ$4•$4ÄRD„R4dR4„ô”4Râ ¢&÷uöƒÒ†&÷GFöÒ×F÷Öv¢†ÆVâ‡—'2’Ó’’òöÆVâ‡—'2¢f÷"’Â†ÆVgEöÆ&VÂÇ&–v‡EöÆ&VÂ’–âVçVÖW&FR‡—'2“ ¢“×F÷¶’¢‡&÷uö‚¶v¢æVÂ†G&rÅ³sÇ“Ã#3Ç“·&÷uö…ÒÆf–ÆÃÒ"4dddDc‚"¢7F—f—G•ö†VF–ær†G&rÇFW‡BÆb'¶’³Ò·&÷u÷&ö×GÒ"Å³#RÇ“³‚Ã##sÇ“¶†VF–æuÒ¢Ö–CÓ#C ¢6&B†G&rÇFW‡BÅ³#RÇ“¶†VF–ærÃ“‚Ç“·&÷uö‚ÓUÒÆÆVgEöÆ&VÂ¢6&B†G&rÇFW‡BÅ³#ƒ"Ç“¶†VF–ærÃ##sRÇ“·&÷uö‚ÓUÒÇ&–v‡EöÆ&VÂ¢G&ræÆ–æR…¶Ö–BÇ“¶†VF–ær³"ÆÖ–BÇ“·&÷uö‚Ó#UÒÆf–ÆÃÒ"4C„3„cR"Çv–GFƒÓB  ¦FVb&VæFW%ö¦÷W&æÂ†G&rÇFW‡B“ ¢7F—f—G•ö†VF–ær†G&rÇFW‡BÂ#4„ôõ4R„TÅD…’„$•BDòE$r"Å³sÃ“CÃ#3ÃÒ¢&ö×G3Õ²&6ÆVâ&öG’"Â&†VÇF‡’fööB"Â&7F—fR&öG’"Â&vööB6ÆVW%Ð¢vÓ#²7sÒƒ#CÖv£2’òó@¢f÷"’ÆÆ&VÂ–âVçVÖW&FR‡&ö×G2“ ¢ƒÓs¶’¢†7r¶v“²6&B†G&rÇFW‡BÅ·ƒÃÇƒ¶7rÃCƒÒÆÆ&VÂÆ&FvSÖ’³¢7F—f—G•ö†VF–ær†G&rÇFW‡BÂ#"E$r”õU"„TÅD…’„$•B"Å³sÃSÃ#3ÃSsÒ¢æVÂ†G&rÅ³sÃSƒÃ#3Ã#ccÒÆf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÕDTÂÇv–GFƒÓBÇ&F—W3Ó#‚¢f—GFVB‡FW‡BÆG&rÂ$×’†VÇF‡’†&—BF†—2vVV²v2õõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõòâ"Å³#3Ã#sÃ##SÃ#ƒ#ÒÇ6—¦SÓ32ÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÆG&rÂ$—B†VÇVBÖRõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõòâ"Å³#3Ã#ƒCÃ##SÃ#“ƒÒÇ6—¦SÓ32ÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"  ¦FVb&VæFW%÷&öÖ—6R†G&rÇFW‡B“ ¢†&—G3Õ²&''W6‚FVWF‚"Â'v6‚†æG2"Â&G&–æ²vFW""Â&VB†VÇF‡’fööB"Â&W†W&6—6R"Â'6ÆVWöâF–ÖR"Â&föÆÆ÷r6fWG’'VÆW2"Â'FVÆÂG'W7FVBGVÇB%Ð¢7F—f—G•ö†VF–ær†G&rÇFW‡BÂ%D”4²D„R„$•E2”õR$ôÔ•4RDò$5D•4R"Å³sÃ“CÃ#3ÃÒ¢6öÇ3Ó#²&÷w3ÓC²vÓ##²ÆVgCÓs²F÷ÓS²&÷GFöÓÓ#ccP¢7sÒƒ#CÖv’òó#²6ƒÒ†&÷GFöÒ×F÷Öv£2’òó@¢f÷"’ÆÆ&VÂ–âVçVÖW&FR††&—G2“ ¢&÷rÆ6öÃÖF—fÖöB†’Æ6öÇ2“²ƒÖÆVgB¶6öÂ¢†7r¶v“²“×F÷·&÷r¢†6‚¶v¢æVÂ†G&rÅ·ƒÇ“Çƒ¶7rÇ“¶6…ÒÆf–ÆÃÒ'v†—FR"¢G&rç&÷VæFVE÷&V7FævÆR…·ƒ³#BÇ“¶6‚òó"ÓC"Çƒ³‚Ç“¶6‚òó"³C%ÒÇ&F—W3Ó"Æf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÕU%ÄRÇv–GFƒÓB¢G&u÷7–Ö&öÂ†G&rÇFW‡BÆÆ&VÂÅ·ƒ³#RÇ“³#Çƒ³3“Ç“¶6‚Ó#Ò¢f—GFVB‡FW‡BÆG&rÆÆ&VÂÅ·ƒ³CÇ“³#"Çƒ¶7rÓ#BÇ“¶6‚Ó#%ÒÇ6—¦SÓ3ÆÖ–æ–×VÓÓ#Æ&öÆCÕG'VRÆÆ–æW3Ó"ÆÆ–vãÒ&ÆVgB"¢æVÂ†G&rÅ³sÃ#sÃ#3Ã3SÒÆf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÆG&rÂ$×’†VÇF‡’&öÖ—6R—3¢"Å³#3Ã#sSÃƒSÃ#ƒ3ÒÇ6—¦SÓ3"ÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢G&ræÆ–æR…³ƒSÃ#ƒ3RÃ###Ã#ƒ3UÒÆf–ÆÃÔäe’Çv–GFƒÓ2¢G&ræÆ–æR…³#3Ã#“CRÃ###Ã#“CUÒÆf–ÆÃÔäe’Çv–GFƒÓ2  ¦FVb&VæFW%÷&W6VçFF–öâ†G&rÇFW‡B“ ¢7F—f—G•ö†VF–ær†G&rÇFW‡BÂ#4„ôõ4RôäRddõU$•DR„$•B"Å³sÃ“CÃ#3ÃÒ¢Æ&VÇ3Õ²&‡–v–VæR"Â&†VÇF‡’fööB"Â&W†W&6—6R"Â'6fWG’%Ð¢vÓ#C²7sÒƒ#CÖv£2’òó@¢f÷"’ÆÆ&VÂ–âVçVÖW&FR†Æ&VÇ2“ ¢ƒÓs¶’¢†7r¶v“²6&B†G&rÇFW‡BÅ·ƒÃÇƒ¶7rÃCƒÒÆÆ&VÂÆ&FvSÖ’³¢7F—f—G•ö†VF–ær†G&rÇFW‡BÂ#"E$rõ"Äât„B”õRt”ÄÂ4„$R"Å³sÃSÃ#3ÃSsÒ¢æVÂ†G&rÅ³sÃSƒRÃ#3Ã#C“UÒÆf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÕDTÂÇv–GFƒÓBÇ&F—W3Ó#‚¢æVÂ†G&rÅ³sÃ#SCÃ#3Ã3cÒÆf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÆG&rÂ$×’ff÷W&—FR†VÇF‡’†&—B—2õõõõõõõõõõõõõõõõõõõõõõõõõõõõõòâ"Å³#3Ã#S“Ã##CÃ#sÒÇ6—¦SÓ3BÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÆG&rÂ$—B†VÇ2ÖR&V6W6Rõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõòâ"Å³#3Ã#scÃ##CÃ#ƒƒÒÇ6—¦SÓ3BÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÆG&rÂ$’v–ÆÂ6†÷r÷"6“¢õõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõòâ"Å³#3Ã#“Ã##CÃ3#ÒÇ6—¦SÓ3BÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"  ¦FVb&VæFW%ö6W'F–f–6FR†6çf2ÆG&rÇFW‡BÇ7F"Ç6÷W&6R“ ¢æVÂ†G&rÅ³##ÃƒsÃ##cÃ33ÒÆf–ÆÃÒ"4dddDc‚"Æ÷WFÆ–æSÒ"4Cdc$2"Çv–GFƒÓ‚Ç&F—W3ÓCB¢f—GFVB‡FW‡BÆG&rÂ$4U%D”d”4DRôb4ôÕÄUD”ôâ"Å³3SÃ“cÃ#3ÃÒÇ6—¦SÓc2ÆÖ–æ–×VÓÓCBÆ6öÆ÷W#ÕU%ÄRÆ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ%F†—26W'F–f–6FR—2&÷VFÇ’&W6VçFVBFò"Å³C#ÃƒÃ#cÃ#“ÒÇ6—¦SÓ3’ÆÖ–æ–×VÓÓ#’Æ6öÆ÷W#Ô”ä²¢G&ræÆ–æR…³CSÃC3Ã#3ÃC3ÒÆf–ÆÃÔäe’Çv–GFƒÓB¢f—GFVB‡FW‡BÆG&rÂ$ÆV&æW"w2æÖR"Å³sSÃCCRÃs3ÃSÒÇ6—¦SÓ#RÆÖ–æ–×VÓÓ#Æ6öÆ÷W#Ò"3cCsC„""¢7FUö76WB†6çf2Ç7F"Å³“ÃScÃSƒÃ###Ò¢f—GFVB‡FW‡BÆG&rÂ&f÷"6ö×ÆWF–ær†VÇF‡’†&—G2b6fWG’ÒÄ´r"Å³C#Ã##cÃ#cÃ#CÒÇ6—¦SÓC2ÆÖ–æ–×VÓÓ3Æ&öÆCÕG'VRÆÆ–æW3Ó"¢f—GFVB‡FW‡BÆG&rÂ&æB6†÷v–ær†VÇF‡’Â6&–æræB6fR6†ö–6W2â"Å³CsÃ#C#Ã#Ã#SCÒÇ6—¦SÓ3bÆÖ–æ–×VÓÓ#rÆ6öÆ÷W#ÕDTÂÆ&öÆCÕG'VRÆÆ–æW3Ó"¢G&ræÆ–æR…³3“Ã#sƒÃ“ƒÃ#sƒÒÆf–ÆÃÔäe’Çv–GFƒÓ2“²G&ræÆ–æR…³SÃ#sƒÃ#“Ã#sƒÒÆf–ÆÃÔäe’Çv–GFƒÓ2¢f—GFVB‡FW‡BÆG&rÂ%FV6†W"6–væGW&R"Å³C3Ã#s“Ã“CÃ#ƒSÒÇ6—¦SÓ#2ÆÖ–æ–×VÓÓ‚Æ6öÆ÷W#Ò"3cCsC„""¢f—GFVB‡FW‡BÆG&rÂ$FFR"Å³SCÃ#s“Ã#SÃ#ƒSÒÇ6—¦SÓ#2ÆÖ–æ–×VÓÓ‚Æ6öÆ÷W#Ò"3cCsC„""  ¦FVbG&uö&FvR†G&rÇFW‡BÆ&÷‚ÆÆ&VÂÆ6öÆ÷W"“ ¢ƒÇ“ÇƒÇ“Ö&÷ƒ²7‚Æ7“Ò‡ƒ·ƒ’òó"Â‡“·“’òó#²#ÖÖ–â‡ƒ×ƒÇ“×“’¢ã30¢G&ræVÆÆ—6R…¶7‚×"Æ7’×"Æ7‚·"Æ7’·%ÒÆf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÖ6öÆ÷W"Çv–GFƒÓ‚¢G&u÷7–Ö&öÂ†G&rÇFW‡BÆÆ&VÂÅ¶7‚×"¢ãsÆ7’×"¢ãsÆ7‚·"¢ãsÆ7’·"¢ãCUÒ¢f—GFVB‡FW‡BÆG&rÆÆ&VÂÅ·ƒ³#Ç“Óƒ"ÇƒÓ#Ç“Ó…ÒÇ6—¦SÓ#‚ÆÖ–æ–×VÓÓ’Æ&öÆCÕG'VRÆÆ–æW3Ó¢G&rç&÷VæFVE÷&V7FævÆR…·ƒÓ“RÇ“³#ÇƒÓ#RÇ“³“ÒÇ&F—W3Ó"Æf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÕU%ÄRÇv–GFƒÓB  ¦FVb&VæFW%ö&FvW2†G&rÇFW‡B“ ¢7F—f—G•ö†VF–ær†G&rÇFW‡BÂ$4ôÄõU"T4‚$DtRâD”4²ôäR”õR$RÔõ5B$õTBôbâ"Å³sÃ“CÃ#3ÃÒ¢Æ&VÇ3Õ²‚$…”t”TäR"Â"3DT4c"’Â‚$åUE$•D”ôâ"Â"3cd#“T"’Â‚$ÔõdTÔTåB"Äõ$ätR’Â‚%4dUE’"Å$TB•Ð¢vÓ#c²ÆVgCÓs²F÷Ó#S²&÷GFöÓÓ#s#²7sÒƒ#CÖv’òó#²6ƒÒ†&÷GFöÒ×F÷Öv’òó ¢f÷"’Â†Æ&VÂÆ6öÆ÷W"’–âVçVÖW&FR†Æ&VÇ2“ ¢&÷rÆ6öÃÖF—fÖöB†’Ã"“²ƒÖÆVgB¶6öÂ¢†7r¶v“²“×F÷·&÷r¢†6‚¶v¢æVÂ†G&rÅ·ƒÇ“Çƒ¶7rÇ“¶6…ÒÆf–ÆÃÒ"4dddDc‚"¢G&uö&FvR†G&rÇFW‡BÅ·ƒ³3Ç“³3Çƒ¶7rÓ3Ç“¶6‚Ó3ÒÆÆ&VÂÆ6öÆ÷W"¢æVÂ†G&rÅ³sÃ#ssÃ#3Ã3sÒÆf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÆG&rÂ$’Ò&÷VB&V6W6R’6âõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõòâ"Å³#CÃ#ƒ#Ã##CÃ3ÒÇ6—¦SÓ3BÆÖ–æ–×VÓÓ#2Æ&öÆCÕG'VRÆÆ–æW3Ó"ÆÆ–vãÒ&ÆVgB"  ¦FVb&VæFW%ö6VÆV'&F–öâ†6çf2ÆG&rÇFW‡BÇ7F"“ ¢7FUö76WB†6çf2Ç7F"Å³ƒƒÃs“ÃcÃSÒ¢f—GFVB‡FW‡BÆG&rÂ$’4â5D’„TÅD…’äB4dR"Å³3ÃC“Ã#ƒÃc#ÒÇ6—¦SÓSrÆÖ–æ–×VÓÓCÆ6öÆ÷W#ÕU%ÄRÆ&öÆCÕG'VR¢Æ&VÇ3Õ²‚$’¶VW6ÆVâ"Â"3DT4c"’Â‚$’VBæBG&–æ²vVÆÂ"Â"3cd#“T"’Â‚$’Ö÷fRæB&W7B"Äõ$ätR’Â‚$’Ö¶R6fR6†ö–6W2"Å$TB•Ð¢vÓ#c²ÆVgCÓs²F÷Ócƒ²7sÒƒ#CÖv’òó#²6ƒÓ3“ ¢f÷"’Â†Æ&VÂÆ6öÆ÷W"’–âVçVÖW&FR†Æ&VÇ2“ ¢&÷rÆ6öÃÖF—fÖöB†’Ã"“²ƒÖÆVgB¶6öÂ¢†7r¶v“²“×F÷·&÷r¢†6‚¶v¢æVÂ†G&rÅ·ƒÇ“Çƒ¶7rÇ“¶6…ÒÆf–ÆÃÒ"4dddDc‚"Æ÷WFÆ–æSÖ6öÆ÷W"Çv–GFƒÓRÇ&F—W3Ó3B¢G&uö6†V6²†G&rÅ·ƒ³3RÇ“³#Çƒ³sÇ“³#SUÒÇ6fSÕG'VR¢f—GFVB‡FW‡BÆG&rÆÆ&VÂÅ·ƒ³#RÇ“³cÇƒ¶7rÓ3RÇ“³3#ÒÇ6—¦SÓ3’ÆÖ–æ–×VÓÓ#bÆ&öÆCÕG'VRÆÆ–æW3Ó"ÆÆ–vãÒ&ÆVgB"¢æVÂ†G&rÅ³sÃ#SSÃ#3Ã3sÒÆf–ÆÃÔu$TTâÆ÷WFÆ–æSÒ"3ST“D""Çv–GFƒÓBÇ&F—W3Ó3B¢f—GFVB‡FW‡BÆG&rÂ$†VÇF‡’6†ö–6W2†VÇÖRÆV&âÂÆ’Âw&÷ræB6&Rf÷"÷F†W'2â"Å³#cÃ#cÃ###Ã#sƒÒÇ6—¦SÓC2ÆÖ–æ–×VÓÓ3Æ&öÆCÕG'VRÆÆ–æW3Ó"¢f—GFVB‡FW‡BÆG&rÂ$ÆV&æW"6–væGW&S¢õõõõõõõõõõõõõõõõõõõõõõõõõò"Å³33Ã#ƒcÃ#SÃ#““ÒÇ6—¦SÓ3"ÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VR  ¦FVbfö÷FW"†G&rÇFW‡BÇ6÷W&6R“ ¢æVÂ†G&rÅ³SÃ3SÃ#33Ã33“UÒÆf–ÆÃÔu$TTâÆ÷WFÆ–æSÒ"3ST“D""Çv–GFƒÓ2¢f—GFVB‡FW‡BÆG&rÂ%DT4„U"5TR"Å³#RÃ3ƒÃS#Ã33cUÒÇ6—¦SÓ#RÆÖ–æ–×VÓÓ#Æ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÆG&rÇ6÷W&6U²&7W'&–7VÇVÒ%Õ²'FV6†W%öf6–Æ—FF–öâ%ÒÅ³SCRÃ3sÃCRÃ33sÒÇ6—¦SÓ#RÆÖ–æ–×VÓÓrÆ6öÆ÷W#Ô”ä²ÆÆ–æW3Ó2ÆÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÆG&rÂ$„ôÔRÄ”ä²"Å³CcÃ3ƒÃsRÃ33cUÒÇ6—¦SÓ#RÆÖ–æ–×VÓÓ#Æ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÆG&rÇ6÷W&6U²&7W'&–7VÇVÒ%Õ²'&VçEö†öÖUö7F—f—G’%ÒÅ³s3Ã3sÃ##cRÃ33sÒÇ6—¦SÓ#2ÆÖ–æ–×VÓÓbÆ6öÆ÷W#Ô”ä²ÆÆ–æW3ÓBÆÆ–vãÒ&ÆVgB"¢&–çFVC×6÷W&6U²'vR%Õ²'&–çFVB%Ð¢f—GFVB‡FW‡BÆG&rÇ7G"‡&–çFVB’Å³#sÃ3CÃ#3Ã3CsÒÇ6—¦SÓ#’ÆÖ–æ–×VÓÓ#2Æ6öÆ÷W#Ò"3cCsC„""Æ&öÆCÕG'VR  ¦FVb&VæFW%ööæR†çVÖ&W"Â÷WGWEöF—#¢F‚ÂWf–FVæ6UöF—#¢F‚ÂFW‡BÂÆövòÂ7F"“ ¢vÆö&Â5D•dUõtRÂ5D•dUô4åd0¢6÷W&6RÂ6÷W&6U÷F‚ÒÆöE÷6÷W&6R†çVÖ&W"¢FVf–æ—F–öãÔ5D•d•D”U5¶çVÖ&W%Ð¢6çf3Ô–ÖvRææWr‚%$t""Â…t”ED‚Ä„T”t…B’Â"4ddd4cr"¢G&sÔ–ÖvTG&räG&r†6çf2¢5D•dUõtRÂ5D•dUô4åd2ÒçVÖ&W"Â6çf0¢G'“ ¢†VFW"†6çf2ÆG&rÇFW‡BÆÆövòÇ6÷W&6RÆFVf–æ—F–öâ¢Æ–÷WCÖFVf–æ—F–öå²&Æ–÷WB%Ð¢–bÆ–÷WBæ÷B–â²&6W'F–f–6FR"Â&6VÆV'&F–öâ'Ó ¢6ö×ÆWFVEöÖöFVÂ†6çf2ÆG&rÇFW‡BÇ7F"ÆFVf–æ—F–öå²&ÖöFVÂ%Ò¢–bÆ–÷WBÓÒ'6÷'B#¢&VæFW%÷6÷'B†G&rÇFW‡BÆFVf–æ—F–öâ¢VÆ–bÆ–÷WBÓÒ&ÖF6‚#¢&VæFW%öÖF6‚†G&rÇFW‡BÆFVf–æ—F–öâ¢VÆ–bÆ–÷WBÓÒ'6WVVæ6R#¢&VæFW%÷6WVVæ6R†G&rÇFW‡BÆFVf–æ—F–öâ¢VÆ–bÆ–÷WBÓÒ'—'2#¢&VæFW%÷—'2†G&rÇFW‡BÆFVf–æ—F–öâ¢VÆ–bÆ–÷WBÓÒ&¦÷W&æÂ#¢&VæFW%ö¦÷W&æÂ†G&rÇFW‡B¢VÆ–bÆ–÷WBÓÒ'&öÖ—6R#¢&VæFW%÷&öÖ—6R†G&rÇFW‡B¢VÆ–bÆ–÷WBÓÒ'&W6VçFF–öâ#¢&VæFW%÷&W6VçFF–öâ†G&rÇFW‡B¢VÆ–bÆ–÷WBÓÒ&6W'F–f–6FR#¢&VæFW%ö6W'F–f–6FR†6çf2ÆG&rÇFW‡BÇ7F"Ç6÷W&6R¢VÆ–bÆ–÷WBÓÒ&&FvW2#¢&VæFW%ö&FvW2†G&rÇFW‡B¢VÆ–bÆ–÷WBÓÒ&6VÆV'&F–öâ#¢&VæFW%ö6VÆV'&F–öâ†6çf2ÆG&rÇFW‡BÇ7F"¢VÇ6S¢&—6RfÇVTW'&÷"†b%Vç7W÷'FVBÆ–÷WB¶Æ–÷WGÒ"¢fö÷FW"†G&rÇFW‡BÇ6÷W&6R¢f–æÆÇ“ ¢5D•dUõtRÂ5D•dUô4åd2ÒæöæRÂæöæP¢÷WGWEöF—"æÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR“²Wf–FVæ6UöF—"æÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR¢÷WGWCÖ÷WGWEöF—"öb$„‚ÔÄ´rÕcBÕ¶çVÖ&W#£6GÒçær ¢6çf2ç6fR†÷WGWBÂ%är"ÆG“Òƒ3Ã3’¢Wf–FVæ6S×°¢'vUö–B#¦b$„‚ÔÄ´rÕcBÕ¶çVÖ&W#£6GÒ"Â'7FGW2#¢%52"Â'6÷W&6R#§7G"‡6÷W&6U÷F‚ç&VÆF—fU÷Fò…$ôõB’’À¢'‡—6–6Å÷vR#¦çVÖ&W"Â'&–çFVE÷vR#§6÷W&6U²'vR%Õ²'&–çFVB%ÒÂ&Æ–÷WB#¦Æ–÷WBÀ¢&6ö×ÆWFVEöW†×ÆU÷f—6–&ÆR#¦Æ–÷WBæ÷B–â²&6W'F–f–6FR"Â&6VÆV'&F–öâ'ÒÀ¢&–æFWVæFVçEöç7vW'5÷VæÖ&¶VB#¥G'VRÂ'&W7öç6U÷76U÷W'÷6VgVÂ#¥G'VRÀ¢&öff–6–ÅöÆövõ÷W6VB#¥G'VRÂ&&÷fVE÷7F%÷W6VB#¥G'VRÂ&FWFW&Ö–æ—7F–5÷FW‡B#¥G'VRÀ¢'&VÖ—VÕö–ÆÇW7G&F–öç5ööæÇ’#¥G'VRÂ'&ö6VGW&Åö–ÆÇW7G&F–öç5÷W6VB#¤fÇ6RÀ¢&6çf2#¥µt”ED‚Ä„T”t…EÒÂ&G’#£3À¢Ð¢†Wf–FVæ6UöF—"öb$„‚ÔÄ´rÕcBÕ¶çVÖ&W#£6GÒæ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2†Wf–FVæ6RÆ–æFVçCÓ"’²%Æâ"ÆVæ6öF–æsÒ'WFbÓ‚"¢&WGW&â÷WGW@  ¦FVb6öçF7E÷6†VWB‡F‡2Â÷WGWB“ ¢F‡VÖ%÷sÓ3²F‡VÖ%öƒ×&÷VæB‡F‡VÖ%÷r¤„T”t…Bõt”ED‚“²6öÇ3ÓC²&÷w3ÖÖF‚æ6V–Â†ÆVâ‡F‡2’ö6öÇ2¢6†VWCÔ–ÖvRææWr‚%$t""Â‡F‡VÖ%÷r¦6öÇ2ÇF‡VÖ%ö‚§&÷w2’Â'v†—FR"¢f÷"’ÇF‚–âVçVÖW&FR‡F‡2“ ¢–ÖvSÔ–ÖvRæ÷Vâ‡F‚’æ6öçfW'B‚%$t""“²–ÖvRçF‡VÖ&æ–Â‚‡F‡VÖ%÷rÇF‡VÖ%ö‚’Ä–ÖvRå&W6×Æ–æräÄä5¤õ2¢6†VWBç7FR†–ÖvRÂ‚†’V6öÇ2’§F‡VÖ%÷rÂ†’òö6öÇ2’§F‡VÖ%ö‚’¢÷WGWBç&VçBæÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR“²6†VWBç6fR†÷WGWBÂ%är"  ¦FVb6öç6öÆ–FFU÷Fb‡F‡2Â÷WGWB“ ¢g&öÒ–ò–×÷'B'—FW4”ð¢g&öÒ&W÷'FÆ"æÆ–"çvW6—¦W2–×÷'B@¢g&öÒ&W÷'FÆ"æÆ–"çWF–Ç2–×÷'B–ÖvU&VFW ¢g&öÒ&W÷'FÆ"çFfvVâ–×÷'B6çf22Feö6çf0¢÷WGWBç&VçBæÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR¢Fö7VÖVçC×Feö6çf2ä6çf2‡7G"†÷WGWB’ÇvW6—¦SÔBÇvT6ö×&W76–öãÓ¢Fö7VÖVçBç6WEF—FÆR‚$†VÇF‡’†&—G2b6fWG’ÒÄ´r6öçFVçBvW2"¢Fö7VÖVçBç6WE7V&¦V7B‚$†VÇF‡’†&—G2b6fWG’Ä´r‡—6–6ÂvW2‚ÕC2"¢f÷"F‚–âF‡3 ¢§VsÔ'—FW4”ò‚“²–ÖvRæ÷Vâ‡F‚’æ6öçfW'B‚%$t""’ç6fR†§VrÂ$¥Tr"ÇVÆ—G“Ó“"Ç7V'6×Æ–æsÓÆ÷F–Ö—¦SÕG'VRÆG“Òƒ3Ã3’“²§Vrç6VV²ƒ¢Fö7VÖVçBæG&t–ÖvR„–ÖvU&VFW"†§Vr’ÃÃÇv–GFƒÔE³ÒÆ†V–v‡CÔE³Ò¢Fö7VÖVçBç6†÷uvR‚¢Fö7VÖVçBç6fR‚  ¦FVb'6U÷vW2‡fÇVS¢7G"’ÓâGWÆU¶–çBÂââåÓ ¢6VÆV7FVCÕµÐ¢f÷"Fö¶Vâ–âfÇVRç7Æ—B‚"Â"“ ¢Fö¶Vã×Fö¶Vâç7G&—‚’çWW"‚¢–bæ÷BFö¶Vã¢6öçF–çVP¢–b"Ò"–âFö¶Vã ¢7F'E÷FW‡BÆVæE÷FW‡C×Fö¶Vâç7Æ—B‚"Ò"Ã¢7F'EöF–v—G3Ò""æ¦ö–â†6‚f÷"6‚–â7F'E÷FW‡B–b6‚æ—6F–v—B‚’“²VæEöF–v—G3Ò""æ¦ö–â†6‚f÷"6‚–âVæE÷FW‡B–b6‚æ—6F–v—B‚’¢–bæ÷B7F'EöF–v—G2÷"æ÷BVæEöF–v—G3¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b$–çfÆ–BvR&ævS¢·Fö¶VçÒ"¢7F'BÆVæCÖ–çB‡7F'EöF–v—G2’Æ–çB†VæEöF–v—G2¢–b7F'CæVæC¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b%vR&ævR×W7B&R66VæF–æs¢·Fö¶VçÒ"¢6VÆV7FVBæW‡FVæB‡&ævR‡7F'BÆVæB³’¢VÇ6S ¢F–v—G3Ò""æ¦ö–â†6‚f÷"6‚–âFö¶Vâ–b6‚æ—6F–v—B‚’¢–bæ÷BF–v—G3¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b$–çfÆ–BvS¢·Fö¶VçÒ"¢6VÆV7FVBæVæB†–çB†F–v—G2’¢÷&FW&VC×GWÆR†F–7Bæg&öÖ¶W—2‡6VÆV7FVB’“²–çfÆ–CÕ¶âf÷"â–â÷&FW&VB–bâæ÷B–âtU5Ð¢–bæ÷B÷&FW&VB÷"–çfÆ–C¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b%7W÷'FVBvW2&R‚ÕC3²–çfÆ–B6VÆV7F–öã¢¶–çfÆ–B÷"fÇVWÒ"¢&WGW&â÷&FW&V@  ¦FVbÖ–â‚“ ¢'6W#Ö&w'6Rä&wVÖVçE'6W"‚¢'6W"æFEö&wVÖVçB‚"ÒÖÆövò"ÇG—SÕF‚Ç&WV—&VCÕG'VR¢'6W"æFEö&wVÖVçB‚"Ò×7F""ÇG—SÕF‚Ç&WV—&VCÕG'VR¢'6W"æFEö&wVÖVçB‚"Ò×vW2"ÇG—S×'6U÷vW2ÆFVfVÇCÕtU2¢'6W"æFEö&wVÖVçB‚"ÒÖ÷WGWBÖF—""ÇG—SÕF‚ÆFVfVÇCÕ$ôõBò'v÷&²Ö†VÇF‡’Ö†&—G2×6fWG’ÖÆ¶r÷vW2"¢'6W"æFEö&wVÖVçB‚"ÒÖWf–FVæ6RÖF—""ÇG—SÕF‚ÆFVfVÇCÕ$ôõBò'v÷&²Ö†VÇF‡’Ö†&—G2×6fWG’ÖÆ¶röWf–FVæ6R"¢'6W"æFEö&wVÖVçB‚"ÒÖ6öçF7B×6†VWB"ÇG—SÕF‚¢'6W"æFEö&wVÖVçB‚"Ò×Fb"ÇG—SÕF‚¢&w3×'6W"ç'6Uö&w2‚¢FW‡CÖÆöEöÖöGVÆR‚&†VÇF‡•ö†&—G5÷FW‡EöVæv–æR"ÅDU…EôTät”äR¢ÆövóÔ–ÖvRæ÷Vâ†&w2æÆövò’æ6öçfW'B‚%$t$"“²7F#Ô–ÖvRæ÷Vâ†&w2ç7F"’æ6öçfW'B‚%$t$"¢÷WGWG3Õ·&VæFW%ööæR†âÆ&w2æ÷WGWEöF—"Æ&w2æWf–FVæ6UöF—"ÇFW‡BÆÆövòÇ7F"’f÷"â–â&w2çvW5Ð¢6öçF7CÖ&w2æ6öçF7E÷6†VWB÷"&w2æ÷WGWEöF—"ç&VçBöb$„‚ÔÄ´rÕ¶&w2çvW5³Ó£6GÒÕ¶&w2çvW5²ÓÓ£6GÒÖ6öçF7B×6†VWBçær ¢6öçF7E÷6†VWB†÷WGWG2Æ6öçF7B¢–b&w2çFc¢6öç6öÆ–FFU÷Fb†÷WGWG2Æ&w2çFb¢7VÖÖ'“×²&&öö²#¢$†VÇF‡’†&—G2b6fWG’"Â&ÆWfVÂ#¢$Ä´r"Â'66÷R#¥¶b%¶ã£6GÒ"f÷"â–â&w2çvW5ÒÂ&vVæW&FVB#¦ÆVâ†÷WGWG2’Â&f–ÆVB#£Â&6öçF7E÷6†VWB#§7G"†6öçF7B’Â'Fb#§7G"†&w2çFb’–b&w2çFbVÇ6RæöæWÐ¢&w2æWf–FVæ6UöF—"æÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR¢†&w2æWf–FVæ6UöF—"ò&†VÇF‡’Ö†&—G2×6fWG’×7VÖÖ'’æ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2‡7VÖÖ'’Æ–æFVçCÓ"’²%Æâ"ÆVæ6öF–æsÒ'WFbÓ‚"¢&–çB†§6öâæGV×2‡7VÖÖ'’Æ–æFVçCÓ"’“²&WGW&â   ¦–bõöæÖUõóÓÒ%õöÖ–åõò# ¢&—6R7—7FVÔW†—B†Ö–â‚’ 