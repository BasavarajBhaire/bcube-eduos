#!/usr/bin/env python3
"""Render Early Maths from the exact approved Work Mode archive.

The archive may use nested page folders, semantic per-asset filenames, or a
single composite page sheet.  P022-P044 use the semantic filenames produced by
the approved prompts rather than the older compiler aliases.  This adapter
aligns the generated runtime contract to those real files before rendering.
No generic artwork fallback is allowed.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from io import BytesIO
from pathlib import Path, PurePosixPath

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/render_early_maths_full_book_approved_assets.py"

MODULE_NAME = "early_maths_full_book_approved_assets_base"
spec = importlib.util.spec_from_file_location(MODULE_NAME, BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE}")
module = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = module
spec.loader.exec_module(module)

original_assemble_sheet = module.assemble_sheet


def crop_manifest(names: list[str]) -> dict[str, dict[str, float]]:
    """Build deterministic, non-overlapping source-sheet zones for named files."""
    count = len(names)
    if count <= 1:
        cols = 1
    elif count <= 4:
        cols = 2
    elif count <= 6:
        cols = 3
    elif count <= 8:
        cols = 4
    else:
        cols = 5
    rows = (count + cols - 1) // cols
    outer = 0.04
    gap = 0.025
    cell_w = (1.0 - 2 * outer - gap * (cols - 1)) / cols
    cell_h = (1.0 - 2 * outer - gap * (rows - 1)) / rows
    result: dict[str, dict[str, float]] = {}
    for index, name in enumerate(names):
        row, col = divmod(index, cols)
        result[name] = {
            "x": round(outer + col * (cell_w + gap), 6),
            "y": round(outer + row * (cell_h + gap), 6),
            "w": round(cell_w, 6),
            "h": round(cell_h, 6),
        }
    return result


def comparison_items(pairs: list[list[str]], prompts: list[str], answers: list[str]) -> list[dict[str, object]]:
    return [
        {"assets": pair, "prompt": prompt, "answer": answer}
        for pair, prompt, answer in zip(pairs, prompts, answers)
    ]


# These specifications mirror the actual filenames in the user's approved ZIP.
# They intentionally replace the old pair_1/main_scene/etc. compiler aliases.
ARCHIVE_PAGE_SPECS: dict[str, dict[str, object]] = {
    "EM-LKG-V4-P022": {
        "title": "3D Objects",
        "objective": "Recognise common 3D objects.",
        "instruction": "Match each solid to the object with the same shape.",
        "assets": ["sphere", "cube", "cylinder", "cone", "party_hat", "beach_ball", "tin_can", "dice"],
        "mechanic": "match-3d-solid-to-object",
        "render_kind": "quantity-numeral-match",
        "layout": "solid-match-four-pairs-approved-assets-v1",
        "mechanics": {
            "asset_order": ["sphere", "cube", "cylinder", "cone", "party_hat", "beach_ball", "tin_can", "dice"],
            "left": ["sphere", "cube", "cylinder", "cone"],
            # Full derangement: no independent pair is horizontally pre-solved.
            "right": ["dice", "party_hat", "beach_ball", "tin_can"],
            "pairs": [
                {"left": "sphere", "right": "beach_ball"},
                {"left": "cube", "right": "dice"},
                {"left": "cylinder", "right": "tin_can"},
                {"left": "cone", "right": "party_hat"},
            ],
        },
    },
    "EM-LKG-V4-P023": {
        "title": "Shape Hunt",
        "objective": "Find shapes in familiar objects.",
        "instruction": "Find each target shape in the playground picture.",
        "assets": ["main_playground_scene", "option_house_window", "option_tree", "option_circle_rectangle", "option_rectangle_triangle"],
        "mechanic": "shape-hunt-scene",
        "render_kind": "shape-hunt",
        "layout": "hero-scene-target-strip-approved-assets-v1",
        "mechanics": {
            "asset_order": ["main_playground_scene", "option_house_window", "option_tree", "option_circle_rectangle", "option_rectangle_triangle"],
            "hero": "main_playground_scene",
            "targets": ["option_house_window", "option_tree", "option_circle_rectangle", "option_rectangle_triangle"],
        },
    },
    "EM-LKG-V4-P024": {
        "title": "Patterns",
        "objective": "Recognise repeating patterns.",
        "instruction": "Say each repeating pattern. Draw the next item in the box.",
        "assets": ["pattern_stars", "pattern_shapes", "pattern_leaf_flower"],
        "mechanic": "identify-repeating-pattern",
        "render_kind": "pattern-observation",
        "layout": "pattern-three-strips-approved-assets-v1",
    },
    "EM-LKG-V4-P025": {
        "title": "Complete the Pattern",
        "objective": "Complete repeating patterns.",
        "instruction": "Look at each pattern. Draw or say what comes next.",
        "assets": ["row_apples_bananas", "row_circle_triangles", "row_coloured_cubes", "row_small_big_stars"],
        "mechanic": "complete-repeating-pattern",
        "render_kind": "pattern-completion",
        "layout": "complete-pattern-four-rows-approved-assets-v1",
    },
    "EM-LKG-V4-P026": {
        "title": "Position Words",
        "objective": "Understand basic position words.",
        "instruction": "Look at each picture. Circle the correct position word.",
        "assets": ["ball_in_box", "cat_on_mat", "shoe_under_chair", "kite_above_tree", "dog_next_to_boy", "ball_between_cones"],
        "mechanic": "position-word-choice",
        "render_kind": "comparison-pairs",
        "layout": "position-six-scenes-approved-assets-v1",
        "mechanics": {
            "asset_order": ["ball_in_box", "cat_on_mat", "shoe_under_chair", "kite_above_tree", "dog_next_to_boy", "ball_between_cones"],
            "pairs": [["ball_in_box"], ["cat_on_mat"], ["shoe_under_chair"], ["kite_above_tree"], ["dog_next_to_boy"], ["ball_between_cones"]],
            "items": [
                {"asset": "ball_in_box", "choices": ["in", "on", "under"], "answer": "in"},
                {"asset": "cat_on_mat", "choices": ["on", "under", "beside"], "answer": "on"},
                {"asset": "shoe_under_chair", "choices": ["under", "above", "in"], "answer": "under"},
                {"asset": "kite_above_tree", "choices": ["above", "in", "beside"], "answer": "above"},
                {"asset": "dog_next_to_boy", "choices": ["beside", "between", "under"], "answer": "beside"},
                {"asset": "ball_between_cones", "choices": ["between", "on", "above"], "answer": "between"},
            ],
        },
    },
    "EM-LKG-V4-P027": {
        "title": "Directions",
        "objective": "Follow simple directions.",
        "instruction": "Trace each path from the start object to its destination.",
        "assets": ["mouse_to_cheese", "bee_to_flower", "car_to_garage"],
        "mechanic": "follow-direction-path",
        "render_kind": "direction-paths",
        "layout": "directions-three-paths-approved-assets-v1",
    },
    "EM-LKG-V4-P028": {
        "title": "Directions",
        "objective": "Recognise left, right, up and down.",
        "instruction": "Listen to the direction. Circle the picture that shows it.",
        "assets": ["child_facing_left", "child_facing_right", "bird_flying_up", "bird_flying_down", "car_moving_left", "car_moving_right"],
        "mechanic": "direction-word-choice",
        "render_kind": "comparison-pairs",
        "layout": "direction-three-pairs-approved-assets-v1",
        "mechanics": {
            "asset_order": ["child_facing_left", "child_facing_right", "bird_flying_up", "bird_flying_down", "car_moving_left", "car_moving_right"],
            "pairs": [["child_facing_left", "child_facing_right"], ["bird_flying_up", "bird_flying_down"], ["car_moving_left", "car_moving_right"]],
            "items": comparison_items(
                [["child_facing_left", "child_facing_right"], ["bird_flying_up", "bird_flying_down"], ["car_moving_left", "car_moving_right"]],
                ["Circle left.", "Circle up.", "Circle right."],
                ["child_facing_left", "bird_flying_up", "car_moving_right"],
            ),
        },
    },
}


def add_comparison_spec(page: int, title: str, objective: str, instruction: str, assets: list[str], pairs: list[list[str]], prompts: list[str], answers: list[str]) -> None:
    page_id = f"EM-LKG-V4-P{page:03d}"
    ARCHIVE_PAGE_SPECS[page_id] = {
        "title": title,
        "objective": objective,
        "instruction": instruction,
        "assets": assets,
        "mechanic": title.lower().replace(" & ", "-").replace(" ", "-"),
        "render_kind": "comparison-pairs",
        "layout": f"comparison-{len(pairs)}-pairs-approved-assets-v1",
        "mechanics": {"asset_order": assets, "pairs": pairs, "items": comparison_items(pairs, prompts, answers)},
    }


add_comparison_spec(29, "Big & Small", "Compare objects by size.", "Circle the object named in each row.",
    ["big_elephant", "small_elephant", "big_ball", "small_ball", "big_teddy", "small_teddy"],
    [["big_elephant", "small_elephant"], ["big_ball", "small_ball"], ["big_teddy", "small_teddy"]],
    ["Circle the big elephant.", "Circle the small ball.", "Circle the big teddy."],
    ["big_elephant", "small_ball", "big_teddy"])
add_comparison_spec(30, "Tall & Short", "Compare objects by height.", "Circle the object named in each row.",
    ["tall_giraffe", "short_giraffe", "tall_tree", "short_tree", "tall_building", "short_building"],
    [["tall_giraffe", "short_giraffe"], ["tall_tree", "short_tree"], ["tall_building", "short_building"]],
    ["Circle the tall giraffe.", "Circle the short tree.", "Circle the tall building."],
    ["tall_giraffe", "short_tree", "tall_building"])
add_comparison_spec(31, "Heavy & Light", "Identify objects that are usually heavy or light.", "Circle the object named in each row.",
    ["heavy_rock", "light_feather", "heavy_watermelon", "light_leaf", "heavy_suitcase", "light_balloon"],
    [["heavy_rock", "light_feather"], ["heavy_watermelon", "light_leaf"], ["heavy_suitcase", "light_balloon"]],
    ["Circle the heavy object.", "Circle the light object.", "Circle the heavy object."],
    ["heavy_rock", "light_leaf", "heavy_suitcase"])
add_comparison_spec(32, "Long & Short", "Compare objects by length.", "Circle the object named in each row.",
    ["long_pencil", "short_pencil", "long_ribbon", "short_ribbon", "long_rope", "short_rope"],
    [["long_pencil", "short_pencil"], ["long_ribbon", "short_ribbon"], ["long_rope", "short_rope"]],
    ["Circle the long pencil.", "Circle the short ribbon.", "Circle the long rope."],
    ["long_pencil", "short_ribbon", "long_rope"])
add_comparison_spec(33, "Full & Empty", "Distinguish full containers from empty containers.", "Circle the container named in each row.",
    ["full_glass", "empty_glass", "full_basket", "empty_basket", "full_bucket", "empty_bucket"],
    [["full_glass", "empty_glass"], ["full_basket", "empty_basket"], ["full_bucket", "empty_bucket"]],
    ["Circle the full glass.", "Circle the empty basket.", "Circle the full bucket."],
    ["full_glass", "empty_basket", "full_bucket"])
add_comparison_spec(34, "Capacity", "Compare which container can hold more or less.", "Compare each pair. Circle the container named in each row.",
    ["large_jug", "small_cup", "large_bucket", "small_mug", "large_bottle", "small_bottle"],
    [["large_jug", "small_cup"], ["large_bucket", "small_mug"], ["large_bottle", "small_bottle"]],
    ["Circle the one that holds more.", "Circle the one that holds less.", "Circle the one that holds more."],
    ["large_jug", "small_mug", "large_bottle"])


ARCHIVE_PAGE_SPECS.update({
    "EM-LKG-V4-P035": {
        "title": "Time Awareness", "objective": "Order familiar daily activities.",
        "instruction": "Write 1, 2 and 3 to show the order of the day.",
        "assets": ["morning_wake_up", "afternoon_play", "night_sleep"],
        "mechanic": "daily-routine-order", "render_kind": "sequence-completion", "layout": "daily-routine-three-events-approved-assets-v1",
        "mechanics": {"asset_order": ["afternoon_play", "night_sleep", "morning_wake_up"], "events": ["afternoon_play", "night_sleep", "morning_wake_up"]},
    },
    "EM-LKG-V4-P036": {
        "title": "Sorting", "objective": "Sort objects by one visible attribute.",
        "instruction": "Write each picture number under its colour.",
        "assets": ["red_button_1", "red_button_2", "blue_button_1", "blue_button_2", "red_block_1", "red_block_2", "blue_block_1", "blue_block_2"],
        "mechanic": "sort-by-one-attribute", "render_kind": "classification", "layout": "sorting-eight-items-approved-assets-v1",
        "mechanics": {"asset_order": ["red_button_1", "blue_block_1", "blue_button_1", "red_block_1", "blue_button_2", "red_block_2", "red_button_2", "blue_block_2"], "categories": [{"id": "red", "label": "RED"}, {"id": "blue", "label": "BLUE"}]},
    },
    "EM-LKG-V4-P037": {
        "title": "Classifying", "objective": "Group familiar items by category.",
        "instruction": "Write each picture number in the correct group.",
        "assets": ["apple", "banana", "orange", "cat", "dog", "rabbit", "car", "bus", "bicycle"],
        "mechanic": "classify-familiar-items", "render_kind": "classification", "layout": "classification-three-categories-approved-assets-v1",
        "mechanics": {"asset_order": ["apple", "dog", "bus", "banana", "rabbit", "car", "orange", "cat", "bicycle"], "categories": [{"id": "fruit", "label": "FRUITS"}, {"id": "animal", "label": "ANIMALS"}, {"id": "vehicle", "label": "VEHICLES"}]},
    },
    "EM-LKG-V4-P038": {
        "title": "Picture Graph", "objective": "Read and compare quantities in a simple picture graph.",
        "instruction": "Look at the picture graph. Count the fruit. Circle each answer.",
        "assets": ["graph_apple", "graph_banana", "graph_orange"],
        "mechanic": "read-picture-graph", "render_kind": "picture-graph", "layout": "picture-graph-three-categories-approved-assets-v1",
        "mechanics": {"asset_order": ["graph_apple", "graph_banana", "graph_orange"]},
    },
    "EM-LKG-V4-P039": {
        "title": "Problem Solving", "objective": "Solve simple visual maths situations.",
        "instruction": "Look at each picture. Think, count and tell the answer.",
        "assets": ["problem_missing_ball", "problem_share_apples", "problem_bus_seats"],
        "mechanic": "mixed-maths-problems", "render_kind": "mixed-review", "layout": "problem-solving-three-scenes-approved-assets-v1",
        "mechanics": {"asset_order": ["problem_missing_ball", "problem_share_apples", "problem_bus_seats"]},
    },
    "EM-LKG-V4-P040": {
        "title": "Maths Around Me", "objective": "Notice maths in everyday surroundings.",
        "instruction": "Find a number, a shape, a size pair and a pattern in the scene.",
        "assets": ["maths_around_me_scene"],
        "mechanic": "maths-around-me-find", "render_kind": "observe-reflect", "layout": "single-observation-scene-approved-assets-v1",
        "mechanics": {"asset_order": ["maths_around_me_scene"], "hero": "maths_around_me_scene"},
    },
    "EM-LKG-V4-P041": {
        "title": "Maths Review", "objective": "Review counting, comparison, shapes and patterns.",
        "instruction": "Complete each short maths review activity.",
        "assets": ["review_five_stars", "review_two_apples", "review_four_apples", "review_circle", "review_triangle", "review_square", "review_pattern_red_blue", "review_pattern_next_blue"],
        "mechanic": "mixed-maths-review", "render_kind": "mixed-review", "layout": "maths-review-approved-assets-v1",
        "mechanics": {"asset_order": ["review_five_stars", "review_two_apples", "review_four_apples", "review_circle", "review_triangle", "review_square", "review_pattern_red_blue", "review_pattern_next_blue"]},
    },
    "EM-LKG-V4-P042": {
        "title": "Certificate", "objective": "Celebrate achievement.",
        "instruction": "Celebrate completing Early Maths Adventures.",
        "assets": ["certificate_math_badge", "certificate_trophy", "certificate_shape_border", "certificate_confetti_left", "certificate_confetti_right"],
        "mechanic": "certificate-celebration-assets", "render_kind": "certificate", "layout": "certificate-approved-assets-v1",
        "mechanics": {"asset_order": ["certificate_math_badge", "certificate_trophy", "certificate_shape_border", "certificate_confetti_left", "certificate_confetti_right"]},
    },
    "EM-LKG-V4-P043": {
        "title": "I Am a Maths Explorer", "objective": "Celebrate confidence and interest in early maths.",
        "instruction": "Look at the picture and talk about the maths you can do.",
        "assets": ["maths_explorer_celebration"],
        "mechanic": "maths-reflection-choice", "render_kind": "observe-reflect", "layout": "maths-explorer-single-scene-approved-assets-v1",
        "mechanics": {"asset_order": ["maths_explorer_celebration"], "hero": "maths_explorer_celebration"},
    },
    "EM-LKG-V4-P044": {
        "title": "Early Maths Adventures — Back Cover", "objective": "Close the book with a clear learning identity.",
        "instruction": "Back cover illustration.",
        "assets": ["early_maths_back_cover_scene"],
        "mechanic": "back-cover-illustration", "render_kind": "back-cover", "layout": "back-cover-approved-assets-v1",
        "mechanics": {"asset_order": ["early_maths_back_cover_scene"], "hero": "early_maths_back_cover_scene"},
    },
})


TEACHER_CUES = {
    "EM-LKG-V4-P022": "Name each solid, then ask the child to trace its outline in the air before matching.",
    "EM-LKG-V4-P023": "Name one target at a time. Let the child find and point to it in the playground scene.",
    "EM-LKG-V4-P024": "Say the repeating unit together, then let the child draw the next item in each box.",
    "EM-LKG-V4-P025": "Cover the final space. Ask what repeats, then let the child draw the next item.",
    "EM-LKG-V4-P026": "Read the three position words aloud and let the child circle the word that matches the picture.",
    "EM-LKG-V4-P027": "Ask the child to touch the start object, then trace the dotted route to the destination.",
    "EM-LKG-V4-P028": "Say left, up or right for one row at a time. Let the child circle the matching picture.",
    "EM-LKG-V4-P029": "Compare one pair at a time and ask the child to show big or small with both hands.",
    "EM-LKG-V4-P030": "Check that both objects begin on the same baseline before the child compares their height.",
    "EM-LKG-V4-P031": "Let the child pretend to lift both objects, then circle the heavy or light one named.",
    "EM-LKG-V4-P032": "Point to the common starting edge before comparing which object is long or short.",
    "EM-LKG-V4-P033": "Ask what is inside each container, then let the child circle full or empty as directed.",
    "EM-LKG-V4-P034": "Read more or less for one row at a time. Let the child compare and circle the named container.",
    "EM-LKG-V4-P035": "Say first, next and last as the child writes one order number beside each scene.",
    "EM-LKG-V4-P036": "Name the sorting rule once. The child writes each picture number under red or blue.",
    "EM-LKG-V4-P037": "Name the three groups, then let the child place each numbered picture by category.",
    "EM-LKG-V4-P038": "Count one graph row at a time. Ask the questions only after all three rows are counted.",
    "EM-LKG-V4-P039": "Ask what changes in each scene, then let the child count and record one answer.",
    "EM-LKG-V4-P040": "Give one target at a time and let the child scan, point and circle it in the scene.",
    "EM-LKG-V4-P041": "Complete one review activity at a time and keep every independent answer unmarked.",
    "EM-LKG-V4-P042": "Read the certificate aloud and celebrate the child's effort.",
    "EM-LKG-V4-P043": "Invite the child to choose one achievement and complete the sentence: I can ____.",
    "EM-LKG-V4-P044": "",
}


def page_stems(archive: zipfile.ZipFile, page_id: str) -> set[str]:
    return {PurePosixPath(name).stem for name in module.page_members(archive, page_id).values()}


def prepare_contract(contract: dict[str, object], archive: zipfile.ZipFile) -> dict[str, object]:
    """Align P022-P044 to the actual approved archive and persist for composers."""
    pages = contract.get("pages")
    if not isinstance(pages, dict):
        raise ValueError("Compiled runtime contract has no pages object")
    for page_id, spec in ARCHIVE_PAGE_SPECS.items():
        page = pages.get(page_id)
        if not isinstance(page, dict):
            raise ValueError(f"Runtime contract missing {page_id}")
        expected = list(spec["assets"])
        available = page_stems(archive, page_id)
        missing = sorted(set(expected) - available)
        if missing:
            raise FileNotFoundError(
                f"Approved archive is missing semantic assets for {page_id}: {missing}; "
                f"found {sorted(available)}"
            )
        page["identity"]["title"] = spec["title"]
        page["learning"]["objective"] = spec["objective"]
        page["learning"]["instruction"] = spec["instruction"]
        page.setdefault("guidance", {})["teacher_cue"] = TEACHER_CUES[page_id]
        mechanics = spec.get("mechanics") or {"asset_order": expected}
        page["activity"].update({
            "mechanic": spec["mechanic"],
            "render_kind": spec["render_kind"],
            "mechanics": mechanics,
        })
        page["illustration"].update({
            "source_asset": f"{page_id}.png",
            "requires_generated_art": True,
            "artwork_only": True,
            "assets": expected,
            "asset_crops": crop_manifest(expected),
            "asset_layout": "approved-semantic-files-v1",
        })
        page["layout"].update({
            "template": spec["layout"],
            "parent_panel": False,
            "home_connection": False,
            "generic_response_panel": False,
        })
        page["validation"].update({
            "status": "READY",
            "allow_fallback": False,
            "illustration_contract_aligned": True,
        })
    module.CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return contract


def direct_sheet_member(archive: zipfile.ZipFile, page_id: str) -> str | None:
    """Find a page-owned composite sheet regardless of an outer ZIP folder."""
    matches: list[str] = []
    for raw_name in archive.namelist():
        if raw_name.endswith("/"):
            continue
        path = PurePosixPath(raw_name)
        if path.stem != page_id:
            continue
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        matches.append(raw_name)
    if len(matches) > 1:
        raise ValueError(f"Duplicate composite illustration sheets for {page_id}: {matches}")
    return matches[0] if matches else None


def assemble_sheet(page, archive: zipfile.ZipFile, page_id: str, output: Path) -> int:
    """Use a composite page sheet when present; otherwise use named assets."""
    direct_member = direct_sheet_member(archive, page_id)
    if direct_member is not None:
        image = Image.open(BytesIO(archive.read(direct_member))).convert("RGB")
        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output, "PNG")
        return len(page.get("illustration", {}).get("assets", []))
    try:
        return original_assemble_sheet(page, archive, page_id, output)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"{exc}. The ZIP must contain either named assets inside a {page_id}/ folder "
            f"or one composite sheet named {page_id}.png"
        ) from exc


module.assemble_sheet = assemble_sheet
module.prepare_contract = prepare_contract

if __name__ == "__main__":
    raise SystemExit(module.main())
