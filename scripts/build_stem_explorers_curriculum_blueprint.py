#!/usr/bin/env python3
"""Build the curriculum-first STEM Explorers LKG blueprint and audit."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "production-prompts/stem-explorers/lkg/v4/pages"
OUTPUT = ROOT / "curriculum/stem-explorers/lkg/curriculum-first-p008-p043-v1.json"
AUDIT = ROOT / "curriculum/stem-explorers/lkg/phase2-page-audit-v1.json"


def page(
    instruction: str,
    model: str,
    response: str,
    archetype: str,
    mechanic: str,
    assets: dict[str, str],
    controls: dict[str, Any],
    teacher_cue: str,
) -> dict[str, Any]:
    return {
        "instruction": instruction,
        "model_example": model,
        "expected_response": response,
        "archetype": archetype,
        "mechanic": mechanic,
        "illustration_assets": assets,
        "renderer_controls": controls,
        "teacher_cue": teacher_cue,
        "validation_gates": [
            "completed example is visually separate from independent work",
            "independent answers are unmarked",
            "every box, circle, line and blank area has a named child action",
            "all objects and people are fully visible and uncropped",
            "object names appear wherever they support vocabulary or reading",
            "response controls are large enough for an LKG child",
            "no parent or homework panel is rendered",
        ],
    }


DESIGNS: dict[int, dict[str, Any]] = {
    8: page(
        "Compare Picture A and Picture B. Circle five differences in Picture B. Tell one difference.",
        "Two leaves: the second leaf is missing one spot, and the changed spot is circled.",
        "Five differences circled in Picture B and one oral comparison.",
        "paired-observation-scenes", "circle-five-differences",
        {"nature_a": "park scene with tree, flowers, bird, butterfly, pond and frog",
         "nature_b": "the same park scene with exactly five clear changes"},
        {"difference_count": 5, "circle_on": "picture_b", "labels": ["Picture A", "Picture B"]},
        "Guide the child to compare one small area at a time without naming a difference.",
    ),
    9: page(
        "Name each sense organ. Draw a line to what it helps you notice.",
        "Eye connected to a rainbow: I use my eyes to see colours.",
        "Five lines matching eye, ear, nose, tongue and hand to an observation.",
        "sense-to-observation-match", "match-sense-organ",
        {"eye": "one eye", "ear": "one ear", "nose": "one nose", "tongue": "one tongue", "hand": "one hand",
         "rainbow": "colourful rainbow", "bell": "ringing handbell", "flower": "fragrant flower", "lemon": "lemon slice", "feather": "soft feather"},
        {"left": ["eye", "ear", "nose", "tongue", "hand"], "right": ["bell", "feather", "rainbow", "lemon", "flower"],
         "pairs": [["eye", "rainbow"], ["ear", "bell"], ["nose", "flower"], ["tongue", "lemon"], ["hand", "feather"]]},
        "Name one observation at a time and ask which sense would help.",
    ),
    10: page(
        "Look at each numbered picture. Write its number under LIVING or NON-LIVING.",
        "A numbered flower is placed under LIVING because it grows.",
        "Three picture numbers written in each category and one oral reason.",
        "numbered-picture-sort", "sort-living-nonliving",
        {"dog": "friendly dog", "tree": "green tree", "butterfly": "butterfly", "rock": "rock", "car": "toy car", "book": "closed book"},
        {"items": ["dog", "rock", "tree", "book", "butterfly", "car"], "categories": ["LIVING", "NON-LIVING"],
         "correct": {"LIVING": [1, 3, 5], "NON-LIVING": [2, 4, 6]}, "number_boxes_per_category": 3},
        "Ask whether each thing grows or needs food, then let the child write its number.",
    ),
    11: page(
        "Look at the plant. Draw a line from each word to the correct plant part.",
        "The word LEAF is connected to a leaf on the model plant.",
        "Four lines connecting roots, stem, leaves and flower to the plant.",
        "labelled-diagram-match", "match-plant-parts",
        {"plant": "large complete flowering plant showing roots, stem, leaves and flower"},
        {"labels": ["roots", "stem", "leaves", "flower"], "anchor_positions": ["bottom", "centre", "upper sides", "top"]},
        "Point to one plant part and invite the child to say its name before matching.",
    ),
    12: page(
        "Name each animal and habitat. Draw a line between each animal and its home.",
        "Fish connected to a pond.",
        "Five lines connecting animals to suitable habitats.",
        "animal-habitat-match", "match-animal-home",
        {"fish": "fish", "bird": "bird", "rabbit": "rabbit", "bee": "bee", "dog": "dog",
         "pond": "pond", "nest": "bird nest", "burrow": "rabbit burrow", "hive": "beehive", "kennel": "dog kennel"},
        {"left": ["fish", "bird", "rabbit", "bee", "dog"], "right": ["hive", "kennel", "pond", "burrow", "nest"],
         "pairs": [["fish", "pond"], ["bird", "nest"], ["rabbit", "burrow"], ["bee", "hive"], ["dog", "kennel"]]},
        "Ask what each animal needs from its home after the child matches it.",
    ),
    13: page(
        "Look at each weather picture. Match the item that is useful for that weather.",
        "Rainy weather connected to an umbrella.",
        "Four lines matching sunny, rainy, windy and cloudy weather to useful items.",
        "weather-item-match", "match-weather-equipment",
        {"sunny": "sunny day", "rainy": "rainy day", "windy": "windy day", "cloudy": "cloudy day",
         "hat": "sun hat", "umbrella": "umbrella", "kite": "kite", "light_jacket": "light jacket"},
        {"weather": ["sunny", "rainy", "windy", "cloudy"], "items": ["kite", "hat", "light_jacket", "umbrella"],
         "pairs": [["sunny", "hat"], ["rainy", "umbrella"], ["windy", "kite"], ["cloudy", "light_jacket"]]},
        "Name the weather first, then ask what would be useful outside.",
    ),
    14: page(
        "Look at each numbered activity. Write its number under DAY or NIGHT.",
        "A child eating breakfast is placed under DAY.",
        "Four picture numbers written under DAY and four under NIGHT.",
        "numbered-day-night-sort", "sort-daily-activities",
        {"breakfast": "child eating breakfast", "school": "child walking to school", "play": "child playing outdoors", "sun": "bright sun",
         "sleep": "child sleeping", "stars": "moon and stars", "pyjamas": "child putting on pyjamas", "bedtime_story": "adult reading a bedtime story"},
        {"items": ["sleep", "breakfast", "stars", "school", "play", "pyjamas", "sun", "bedtime_story"],
         "categories": ["DAY", "NIGHT"], "number_boxes_per_category": 4},
        "Ask whether the sky is usually light or dark during each activity.",
    ),
    15: page(
        "Circle the pictures that show safe, careful uses of water. Cross the pictures that waste water.",
        "A child turning off a tap is circled.",
        "Five helpful water-use pictures circled and three wasteful pictures crossed.",
        "water-use-scenario-grid", "circle-save-cross-waste",
        {"drink": "child drinking water", "wash_hands": "child washing hands", "water_plant": "child watering one plant with a can", "cook": "adult using water for cooking",
         "turn_off_tap": "child turning off a tap", "running_tap": "tap left running", "hose_waste": "water hose spraying unused water", "overflow": "overflowing bucket"},
        {"items": ["drink", "running_tap", "water_plant", "overflow", "wash_hands", "hose_waste", "cook", "turn_off_tap"],
         "helpful": [1, 3, 5, 7, 8], "wasteful": [2, 4, 6]},
        "Ask the child to say how one careful action saves water.",
    ),
    16: page(
        "Predict first: circle FLOAT or SINK for each object. Test the objects, then circle the result.",
        "A leaf is predicted to FLOAT; after testing, FLOAT is circled in the result column.",
        "A prediction and observed result circled for six familiar objects.",
        "predict-test-table", "predict-and-record-float-sink",
        {"leaf": "leaf", "coin": "coin", "cork": "cork", "spoon": "metal spoon", "plastic_cap": "plastic bottle cap", "stone": "small stone"},
        {"items": ["leaf", "coin", "cork", "spoon", "plastic_cap", "stone"], "columns": ["PREDICT", "RESULT"], "choices": ["FLOAT", "SINK"]},
        "Let the child predict before placing one object at a time in water.",
    ),
    17: page(
        "Look at each numbered object. Write its number under MAGNETIC or NOT MAGNETIC.",
        "A paper clip is placed under MAGNETIC.",
        "Four picture numbers written in each category.",
        "numbered-magnet-sort", "sort-magnetic-objects",
        {"paper_clip": "paper clip", "wood_block": "wooden block", "key": "metal key", "eraser": "rubber eraser", "nail": "iron nail", "plastic_spoon": "plastic spoon", "steel_lid": "steel jar lid", "crayon": "wax crayon"},
        {"items": ["wood_block", "paper_clip", "eraser", "key", "plastic_spoon", "nail", "crayon", "steel_lid"], "categories": ["MAGNETIC", "NOT MAGNETIC"], "number_boxes_per_category": 4},
        "Ask the child to predict first, then test each safe object with a magnet.",
    ),
    18: page(
        "Name each object. Draw a line to its matching shadow.",
        "A cup connected to its cup-shaped shadow.",
        "Six lines connecting objects to their silhouettes.",
        "object-shadow-match", "match-object-shadow",
        {"tree": "tree", "kite": "kite", "cup": "cup", "rabbit": "rabbit", "umbrella": "umbrella", "bicycle": "bicycle",
         "tree_shadow": "tree silhouette", "kite_shadow": "kite silhouette", "cup_shadow": "cup silhouette", "rabbit_shadow": "rabbit silhouette", "umbrella_shadow": "umbrella silhouette", "bicycle_shadow": "bicycle silhouette"},
        {"left": ["tree", "kite", "cup", "rabbit", "umbrella", "bicycle"], "right": ["cup_shadow", "bicycle_shadow", "tree_shadow", "umbrella_shadow", "rabbit_shadow", "kite_shadow"]},
        "Ask the child to compare the outside shape and direction before matching.",
    ),
    19: page(
        "Look at the three paper bridges. Circle the bridge that can hold the most toy animals. Draw one way to make a bridge stronger.",
        "A folded paper bridge with side rails holds two animals; it is circled as stronger than flat paper.",
        "One strong bridge selected and one strengthening idea drawn.",
        "bridge-design-compare-and-draw", "choose-and-improve-bridge",
        {"flat_bridge": "flat paper bridge over two blocks with one toy animal", "folded_bridge": "accordion-fold paper bridge over two blocks holding several toy animals", "rail_bridge": "paper bridge with folded side rails holding several toy animals"},
        {"designs": ["flat_bridge", "folded_bridge", "rail_bridge"], "choice_positions": 3, "drawing_box": "large purposeful bridge-improvement area"},
        "Let the child test folded and flat paper, then ask what made one bridge stronger.",
    ),
    20: page(
        "Match each simple machine to the everyday object that uses it.",
        "A ramp connected to a playground slide.",
        "Six lines matching ramp, wheel and lever examples.",
        "simple-machine-match", "match-machine-example",
        {"ramp": "simple ramp", "wheel": "wheel and axle", "lever": "lever on a fulcrum", "slide": "playground slide", "wheelbarrow": "wheelbarrow", "seesaw": "seesaw", "road_ramp": "loading ramp", "bicycle": "bicycle", "bottle_opener": "bottle opener"},
        {"machines": ["ramp", "wheel", "lever"], "examples": ["seesaw", "bicycle", "slide", "bottle_opener", "road_ramp", "wheelbarrow"], "matches_per_machine": 2},
        "Name the movement each machine makes easier before the child matches.",
    ),
    21: page(
        "Look at each natural object. Circle the word that names its pattern.",
        "A zebra is matched with STRIPES.",
        "One pattern word circled for each of eight natural objects.",
        "nature-pattern-choice-grid", "identify-natural-pattern",
        {"zebra": "zebra stripes", "ladybird": "spotted ladybird", "snail": "spiral snail shell", "leaf": "leaf veins", "tiger": "tiger stripes", "butterfly": "spotted butterfly wings", "sunflower": "sunflower spiral seeds", "fern": "fern leaf pattern"},
        {"items": ["zebra", "ladybird", "snail", "leaf", "tiger", "butterfly", "sunflower", "fern"], "choices": ["STRIPES", "SPOTS", "SPIRAL", "VEINS"]},
        "Invite the child to trace the pattern in the air before choosing its name.",
    ),
    22: page(
        "Look at each numbered action. Write its number under HELPS EARTH or HURTS EARTH.",
        "Putting paper in a recycling bin is placed under HELPS EARTH.",
        "Four picture numbers written in each category.",
        "numbered-earth-action-sort", "sort-environment-actions",
        {"recycle": "child recycling paper", "litter": "person dropping litter", "plant_tree": "child planting a tree", "waste_water": "tap left running", "reuse_bag": "family using reusable bag", "pick_flowers": "child pulling many wild flowers", "turn_off_light": "child turning off unused light", "smoke": "vehicle releasing heavy smoke"},
        {"items": ["litter", "plant_tree", "waste_water", "recycle", "pick_flowers", "reuse_bag", "smoke", "turn_off_light"], "categories": ["HELPS EARTH", "HURTS EARTH"], "number_boxes_per_category": 4},
        "Ask what would happen if everyone made each choice.",
    ),
    23: page(
        "Name the objects. Circle the things that use technology. Choose one and tell what it helps us do.",
        "A torch is circled: It helps us see in the dark.",
        "Six technology objects circled among ten familiar objects and one oral use stated.",
        "technology-object-grid", "identify-everyday-technology",
        {"torch": "torch", "tablet": "tablet", "fan": "electric fan", "telephone": "telephone", "camera": "camera", "washing_machine": "washing machine", "book": "book", "spoon": "spoon", "ball": "ball", "chair": "chair"},
        {"items": ["book", "torch", "spoon", "tablet", "ball", "fan", "chair", "telephone", "camera", "washing_machine"], "technology_count": 6},
        "Ask what each circled object helps people do; accept one short sentence.",
    ),
    24: page(
        "Circle every picture that shows safe technology use. Cross the unsafe pictures.",
        "A child sitting at a table with the screen at a comfortable distance is circled.",
        "Four safe scenarios circled and four unsafe scenarios crossed.",
        "technology-safety-scenarios", "circle-safe-cross-unsafe",
        {"ask_adult": "child asking adult before using a device", "sit_well": "child sitting well at a table with device", "short_time": "child stopping device use to stretch", "clean_hands": "child using device with clean dry hands", "bed_screen": "child using bright screen in bed", "food_device": "child spilling a drink beside a device", "too_close": "child holding screen too close", "unknown_click": "child about to click an unknown pop-up"},
        {"items": ["too_close", "ask_adult", "food_device", "sit_well", "bed_screen", "short_time", "unknown_click", "clean_hands"], "safe": [2, 4, 6, 8]},
        "Discuss one safe habit at a time and ask the child to explain one choice.",
    ),
    25: page(
        "Follow each colour-and-arrow code. Draw the next two symbols in the empty boxes.",
        "Red up, blue right, red up, blue right; the next symbols are red up and blue right.",
        "Two symbols drawn to complete each of four coded patterns.",
        "coding-pattern-rows", "complete-colour-arrow-code",
        {"arrow_up": "up arrow symbol", "arrow_down": "down arrow symbol", "arrow_left": "left arrow symbol", "arrow_right": "right arrow symbol", "red_circle": "red circle", "blue_square": "blue square", "green_triangle": "green triangle", "yellow_star": "yellow star"},
        {"rows": 4, "pattern_types": ["AB", "AAB", "ABC", "AB"], "empty_boxes_per_row": 2, "symbols_large": True},
        "Have the child say the repeating code aloud before drawing.",
    ),
    26: page(
        "Guide the robot to the battery. Draw the route on the grid, then write the arrow steps in the boxes.",
        "Robot moves RIGHT, RIGHT, UP to reach a star; the three arrows are shown.",
        "One route drawn on a large grid and five to seven arrow steps recorded.",
        "robot-grid-route", "draw-route-and-code",
        {"robot": "friendly small robot", "battery": "large battery icon", "rock": "rock obstacle", "water": "puddle obstacle", "box": "wooden box obstacle"},
        {"grid": [6, 6], "start": [5, 0], "goal": [0, 5], "obstacles": [[4, 1], [3, 1], [2, 3], [1, 4]], "step_boxes": 10},
        "Ask the child to point to each square before drawing and say each direction aloud.",
    ),
    27: page(
        "Look at the four bridge designs. Circle the design that is strongest. Draw one support that could improve a weaker bridge.",
        "A bridge with a triangle brace is circled because the brace supports it.",
        "One design selected and one support drawn on a weaker design.",
        "engineering-design-choice", "choose-and-improve-structure",
        {"bridge_no_support": "flat bridge without support", "bridge_one_post": "bridge with one centre post", "bridge_triangle": "bridge with triangular braces", "bridge_arch": "bridge with an arch support"},
        {"designs": ["bridge_one_post", "bridge_no_support", "bridge_arch", "bridge_triangle"], "drawing_overlay_area": True, "choice_positions": 4},
        "Ask where each design carries the load; let the child test paper shapes if available.",
    ),
    28: page(
        "Circle the tower with the widest, most stable base. Then plan your own tall tower in the grid.",
        "A tower with a wide bottom and smaller top is circled as stable.",
        "One stable tower selected and one tower plan drawn.",
        "tower-choice-and-plan", "choose-stable-draw-tower",
        {"tower_narrow": "tall block tower with narrow base", "tower_leaning": "leaning block tower", "tower_wide": "stable block tower with wide base", "tower_uneven": "uneven block tower"},
        {"designs": ["tower_narrow", "tower_wide", "tower_uneven", "tower_leaning"], "drawing_grid": [6, 8], "large_drawing_area": True},
        "Invite the child to build the planned tower and compare it with the drawing.",
    ),
    29: page(
        "Look at each pair. Circle the stronger structure. Tell what makes it strong.",
        "A chair with cross-braced legs is circled instead of a chair with loose legs.",
        "One stronger structure circled in each of five varied pairs.",
        "strong-weak-pairs", "compare-structure-strength",
        {"bridge_pair": "weak flat paper bridge and braced paper bridge", "tower_pair": "narrow leaning tower and wide stable tower", "chair_pair": "loose chair and braced chair", "shelf_pair": "unsupported shelf and shelf with brackets", "tent_pair": "tent without pegs and tent secured with pegs"},
        {"pairs": ["bridge_pair", "tower_pair", "chair_pair", "shelf_pair", "tent_pair"], "answer_positions": [2, 1, 2, 1, 2]},
        "Ask the child to point to the support before choosing the stronger structure.",
    ),
    30: page(
        "Count the cubes used to measure each object. Write the number. Circle the longer or taller object in each pair.",
        "A pencil measures 5 cubes; 5 is written in the box.",
        "Six measurements written and three comparisons circled.",
        "non-standard-measurement", "count-units-and-compare",
        {"pencil": "pencil", "crayon": "crayon", "book": "book", "eraser": "eraser", "plant": "small potted plant", "bottle": "water bottle"},
        {"pairs": [["pencil", "crayon"], ["book", "eraser"], ["plant", "bottle"]], "unit_counts": [7, 4, 6, 3, 8, 5], "writing_boxes": 6},
        "Touch and count each cube with the child before asking which object is longer or taller.",
    ),
    31: page(
        "Look at each numbered object. Write its number under WOOD, METAL or PLASTIC.",
        "A wooden spoon is placed under WOOD.",
        "Three picture numbers written in each material group.",
        "material-sort", "sort-by-material",
        {"wood_spoon": "wooden spoon", "metal_key": "metal key", "plastic_cup": "plastic cup", "wood_block": "wooden block", "metal_can": "metal can", "plastic_bottle": "plastic bottle", "wood_pencil": "wooden pencil", "metal_clip": "metal paper clip", "plastic_comb": "plastic comb"},
        {"items": ["metal_key", "plastic_cup", "wood_spoon", "plastic_bottle", "wood_block", "metal_can", "wood_pencil", "plastic_comb", "metal_clip"], "categories": ["WOOD", "METAL", "PLASTIC"], "number_boxes_per_category": 3},
        "Let the child touch safe examples of the three materials before sorting.",
    ),
    32: page(
        "Predict which ramp will make the ball travel farthest. Circle your prediction. Test, then tick the result.",
        "A high ramp is predicted; after the test, the ramp that rolled farthest is ticked.",
        "One prediction and one observed result recorded, followed by an oral comparison.",
        "ramp-predict-test", "predict-test-compare-distance",
        {"low_ramp": "low toy-car ramp", "medium_ramp": "medium-height toy-car ramp", "high_ramp": "high toy-car ramp"},
        {"ramps": ["medium_ramp", "low_ramp", "high_ramp"], "prediction_controls": 3, "result_controls": 3, "distance_record_line": True},
        "Keep the same ball and starting point; change only the ramp height.",
    ),
    33: page(
        "Look at each science picture. Use the starter to ask one complete question.",
        "Picture of a melting ice cube: What happens when the ice gets warm?",
        "Four oral questions using What, Why, How or Which.",
        "science-question-prompts", "form-question-from-scene",
        {"melting_ice": "ice cube melting in sunlight", "growing_plant": "seedling growing toward light", "floating_boat": "paper boat floating in water", "magnet_clips": "magnet attracting paper clips"},
        {"scenes": ["melting_ice", "growing_plant", "floating_boat", "magnet_clips"], "starters": ["What", "Why", "How", "Which"], "partner_reply_cue": True},
        "Say the starter once, then allow the child to form the rest of the question.",
    ),
    34: page(
        "After testing the objects in water, tick FLOAT or SINK. Draw one thing you noticed.",
        "A floating cork has FLOAT ticked; a short observation is modelled orally.",
        "Results ticked for four objects and one observation drawing completed.",
        "record-investigation-results", "tick-results-and-draw-observation",
        {"cork": "cork floating in a clear bowl", "coin": "coin at bottom of clear bowl", "leaf": "leaf floating in a clear bowl", "stone": "stone at bottom of clear bowl"},
        {"items": ["cork", "coin", "leaf", "stone"], "choices": ["FLOAT", "SINK"], "drawing_box": "one large observation box"},
        "Ask the child to describe the drawing; write their words only if support is needed.",
    ),
    35: page(
        "Read each STEM word. Draw a line to the picture that shows its meaning.",
        "OBSERVE connected to a child looking through a magnifying glass.",
        "Eight words matched to eight action pictures.",
        "stem-vocabulary-match", "match-word-to-action",
        {"observe": "child observing a leaf with magnifying glass", "predict": "child thinking about which object will float", "test": "child placing object in water", "measure": "child measuring pencil with cubes", "sort": "child sorting red and blue buttons", "build": "child building block bridge", "record": "child drawing result on paper", "improve": "child adding support to block tower"},
        {"words": ["observe", "predict", "test", "measure", "sort", "build", "record", "improve"], "pictures_order": ["test", "sort", "observe", "improve", "measure", "record", "build", "predict"]},
        "Read one word at a time and ask what action the child can see.",
    ),
    36: page(
        "Complete each STEM review task. Circle, match, sort and draw as directed.",
        "One leaf observation is modelled: green, smooth and pointed.",
        "Six short tasks reviewing observation, senses, sorting, prediction, measurement and building.",
        "mixed-stem-review", "six-mini-review-tasks",
        {"observation_task": "two similar leaves for detail comparison", "sense_task": "bell, flower and feather with sense icons", "sort_task": "two living and two non-living objects", "prediction_task": "leaf and coin beside water bowl", "measure_task": "pencil beside cube units", "building_task": "two small bridge designs"},
        {"tasks": ["observation_task", "sense_task", "sort_task", "prediction_task", "measure_task", "building_task"], "task_count": 6, "response_controls": "mixed purposeful controls"},
        "Read one task at a time and allow the child to explain one answer.",
    ),
    37: page(
        "Predict which material will absorb the most water. Test each one, then tick the result and draw what you noticed.",
        "A tissue absorbs a water drop; ABSORBS is ticked.",
        "Prediction and results recorded for tissue, foil and plastic, plus one observation drawing.",
        "guided-absorption-investigation", "predict-test-record-absorption",
        {"tissue": "square of tissue", "foil": "square of aluminium foil", "plastic": "square of plastic sheet", "dropper": "child-safe water dropper"},
        {"materials": ["tissue", "foil", "plastic"], "prediction_controls": 3, "result_choices": ["ABSORBS", "DOES NOT ABSORB"], "drawing_box": True},
        "Use equal-size pieces and one drop of water on each material.",
    ),
    38: page(
        "Compare Design A and Design B. Circle the stronger design. Add one support to improve the weaker design.",
        "A tower with a wide base is circled; one brace is drawn on the weaker tower.",
        "One stronger design selected in each of three pairs and one improvement drawn.",
        "engineer-compare-improve", "choose-and-improve-design",
        {"tower_pair": "narrow tower and wide-base tower", "bridge_pair": "flat bridge and triangular-braced bridge", "chair_pair": "chair without cross brace and chair with cross brace"},
        {"pairs": ["tower_pair", "bridge_pair", "chair_pair"], "answer_positions": [2, 2, 2], "improvement_box": "one large drawing overlay"},
        "Ask what changed between the designs before the child chooses.",
    ),
    39: page(
        "Solve each picture challenge. Use observation, prediction, sorting, measuring and building ideas.",
        "A leaf is observed closely and the matching leaf is circled.",
        "Five independent mini-challenges completed with varied response actions.",
        "young-scientist-challenge", "five-stem-mini-challenges",
        {"observe_challenge": "target leaf and three similar leaf choices", "predict_challenge": "ball beside three ramp heights", "sort_challenge": "six numbered objects of wood and metal", "measure_challenge": "two pencils beside cube units", "build_challenge": "three bridge support designs"},
        {"tasks": ["observe_challenge", "predict_challenge", "sort_challenge", "measure_challenge", "build_challenge"], "task_count": 5, "answers_unmarked": True},
        "Observe which strategy the child chooses; do not demonstrate an assessment answer.",
    ),
    40: page(
        "Choose one investigation. Draw what you did and what happened. Finish: I discovered that ___.",
        "A small drawing shows a leaf floating; the adult-supported model says, I discovered that a leaf can float.",
        "One investigation drawing and one dictated or copied discovery.",
        "stem-journal", "draw-and-dictate-discovery",
        {"float_icon": "small bowl with floating leaf", "magnet_icon": "magnet attracting clips", "plant_icon": "growing plant", "bridge_icon": "paper bridge"},
        {"choice_icons": ["float_icon", "magnet_icon", "plant_icon", "bridge_icon"], "drawing_box": "large purposeful area", "writing_lines": 2},
        "Ask the child to describe the drawing; support the writing only when needed.",
    ),
    41: page(
        "Celebrate completion of STEM Explorers.",
        "No completed-example strip is needed on a certificate.",
        "Child name, date and teacher signature are written in the certificate fields.",
        "certificate", "complete-certificate",
        {"badge": "premium STEM explorer achievement badge", "trophy": "small STEM trophy with shapes and gears", "confetti": "compact celebratory stars and confetti"},
        {"fields": ["This certificate is awarded to", "Date", "Teacher signature"], "model_strip": False},
        "Celebrate the child’s curiosity, careful observation and effort.",
    ),
    42: page(
        "Colour one badge for each STEM skill you practised. Choose your favourite skill and tell why.",
        "The OBSERVER badge is lightly coloured as an example.",
        "Up to six skill badges coloured and one favourite skill shared orally.",
        "stem-explorer-badges", "colour-and-reflect",
        {"hero": "happy LKG child holding a magnifying glass beside simple STEM tools", "badge_observe": "outline magnifying-glass badge", "badge_predict": "outline thought-bubble badge", "badge_test": "outline water-bowl badge", "badge_measure": "outline cube-ruler badge", "badge_build": "outline bridge badge", "badge_record": "outline pencil-and-paper badge"},
        {"badges": ["OBSERVE", "PREDICT", "TEST", "MEASURE", "BUILD", "RECORD"], "colouring": True, "reflection_choices": 6},
        "Invite the child to name one page that shows the chosen skill.",
    ),
    43: page(
        "Choose one STEM success. Draw or show it, then tell: I am proud that I ___.",
        "A child points to a paper bridge and says, I am proud that I built a strong bridge.",
        "One celebration choice, one drawing or display, and one short spoken reflection.",
        "stem-celebration", "choose-draw-share",
        {"observe_choice": "magnifying glass and leaf", "experiment_choice": "water bowl and floating cork", "build_choice": "paper bridge with toy animal", "code_choice": "friendly robot following arrows", "celebration": "two children proudly sharing STEM work"},
        {"choices": ["observe_choice", "experiment_choice", "build_choice", "code_choice"], "drawing_box": "medium purposeful celebration drawing area", "sentence_starter": "I am proud that I ___."},
        "Let each child share one success; keep the reflection short and positive.",
    ),
}


def source_for(page_number: int) -> tuple[Path, dict[str, Any], str]:
    matches = sorted(SOURCE_DIR.glob(f"ST-LKG-V4-P{page_number:03d}-*.json"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one source JSON for P{page_number:03d}, found {matches}")
    source_path = matches[0]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    md_path = source_path.with_suffix(".md")
    md_text = md_path.read_text(encoding="utf-8")
    match = re.search(r"PAGE\s+\d+:\s*([^\r\n]+)", md_text)
    execution = match.group(1).strip() if match else ""
    return source_path, source, execution


def main() -> int:
    if set(DESIGNS) != set(range(8, 44)):
        missing = sorted(set(range(8, 44)) - set(DESIGNS))
        extra = sorted(set(DESIGNS) - set(range(8, 44)))
        raise RuntimeError(f"Blueprint scope mismatch. Missing={missing}, extra={extra}")

    pages: dict[str, Any] = {}
    audit_rows: list[dict[str, Any]] = []
    for number in range(8, 44):
        source_path, source, execution = source_for(number)
        page_id = f"ST-LKG-V4-P{number:03d}"
        design = dict(DESIGNS[number])
        design.update({
            "title": source["page"]["title"],
            "objective": source["curriculum"]["objective"],
            "physical_page": number,
            "printed_page": source["page"].get("printed"),
            "source_prompt": source_path.relative_to(ROOT).as_posix(),
            "source_execution": execution,
            "parent_panel": False,
        })
        pages[page_id] = design
        audit_rows.append({
            "page_id": page_id,
            "title": design["title"],
            "source_objective": design["objective"],
            "source_instruction": source["curriculum"].get("instruction", ""),
            "source_execution": execution,
            "phase2_instruction": design["instruction"],
            "phase2_archetype": design["archetype"],
            "response_mechanic": design["mechanic"],
            "model_required": bool(design["renderer_controls"].get("model_strip", True)),
            "illustration_asset_count": len(design["illustration_assets"]),
            "status": "REBUILT_CONTENT_ALIGNED",
            "diagnosis": "Generic Investigation Discussion replaced with exact child action and response mechanics.",
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "version": "stem-explorers-curriculum-first-v1",
        "book": "STEM Explorers",
        "level": "LKG (4+)",
        "scope": "ST-LKG-V4-P008 through ST-LKG-V4-P043",
        "policy": "Task-specific interactive pages; no parent panel; no generic response box; response-safe independent work.",
        "pages": pages,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    AUDIT.write_text(json.dumps({
        "version": "stem-explorers-phase2-audit-v1",
        "summary": {
            "pages_audited": len(audit_rows),
            "generic_source_instruction_pages": sum(row["source_instruction"] == "Investigation Discussion" for row in audit_rows),
            "content_aligned_rebuilds": len(audit_rows),
            "parent_panels": 0,
        },
        "pages": audit_rows,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} page blueprints to {OUTPUT}")
    print(f"Wrote audit to {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
