#!/usr/bin/env python3
"""Validate BCube Learning Page Contract V2 and its illustration before composition."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_SPEC = ROOT / "bcube-publishing-sdk/contracts/learning-page-contract-v2.json"
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"

PLACEHOLDER_PHRASES = (
    "one dominant learning scene",
    "one dominant focus for",
    "introduce the page purpose clearly",
    "use this page for orientation only",
    "use the page for its stated front-matter purpose",
    "art activity discussion",
    "what can you show or tell about",
)
DEFAULT_TEACHER_FRAGMENT = "model once, invite one response, pause for processing"
DEFAULT_PARENT_FRAGMENT = "use a familiar home routine or everyday object"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rectangle_inside(inner: list[int], outer: list[int]) -> bool:
    return (
        len(inner) == 4
        and len(outer) == 4
        and inner[0] >= outer[0]
        and inner[1] >= outer[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
        and inner[2] > inner[0]
        and inner[3] > inner[1]
    )


def rectangles_overlap(a: list[int], b: list[int]) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def image_metrics(path: Path, label: str, minimum_side: int) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        if min(width, height) < minimum_side:
            raise ValueError(f"{label} is too small: {width}x{height}; minimum side is {minimum_side}px")
        if label == "illustration" and width >= 2200 and height >= 3200:
            raise ValueError("Illustration looks like a full A4 page; provide illustration-only artwork")
        white = Image.new("RGB", rgb.size, (255, 255, 255))
        difference = ImageChops.difference(rgb, white).convert("L")
        mask = difference.point(lambda value: 255 if value > 12 else 0)
        bbox = mask.getbbox()
        if bbox is None:
            raise ValueError(f"{label} is blank or near-white")
        visible_width = bbox[2] - bbox[0]
        visible_height = bbox[3] - bbox[1]
        visible_occupancy = round((visible_width * visible_height) / (width * height), 4)
        nonwhite_fraction = round(
            sum(1 for value in mask.getdata() if value) / (width * height),
            4,
        )
        stddev = round(sum(ImageStat.Stat(rgb).stddev) / 3, 3)
        if label == "illustration" and nonwhite_fraction < 0.015:
            raise ValueError(
                f"Illustration contains too little visible artwork: non-white fraction {nonwhite_fraction}"
            )
        return {
            "path": str(path),
            "size": [width, height],
            "mode": image.mode,
            "visible_bbox": list(bbox),
            "visible_occupancy": visible_occupancy,
            "nonwhite_fraction": nonwhite_fraction,
            "mean_channel_stddev": stddev,
        }


def text_values(contract: dict[str, Any]) -> dict[str, str]:
    return {
        "title": str(contract["identity"].get("title") or ""),
        "objective": str(contract["learning"].get("objective") or ""),
        "student_instruction": str(contract["learning"].get("student_instruction") or ""),
        "expected_response": str(contract["learning"].get("expected_response") or ""),
        "teacher_model": str(contract["guidance"]["teacher"].get("model") or ""),
        "teacher_question": str(contract["guidance"]["teacher"].get("question") or ""),
        "parent_extension": str(contract["guidance"].get("parent_extension") or ""),
        "illustration_scene": str(contract["illustration"].get("scene") or ""),
        "illustration_focal_point": str(contract["illustration"].get("focal_point") or ""),
    }


def validate_text(contract: dict[str, Any], spec: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    values = text_values(contract)
    missing = [key for key, value in values.items() if not value.strip()]
    if missing:
        raise ValueError(f"Learning contract contains empty required text: {missing}")
    combined = " ".join(values.values()).casefold()
    placeholders = [phrase for phrase in PLACEHOLDER_PHRASES if phrase in combined]
    if placeholders:
        raise ValueError(f"Learning contract contains placeholder phrases: {placeholders}")
    if DEFAULT_TEACHER_FRAGMENT in values["teacher_model"].casefold():
        raise ValueError("Learning contract still uses the default teacher prompt")
    if DEFAULT_PARENT_FRAGMENT in values["parent_extension"].casefold():
        raise ValueError("Learning contract still uses the default parent prompt")
    limits = {
        "title": template["rules"]["max_title_chars"],
        "objective": spec["content_policy"]["objective_max_chars"],
        "student_instruction": spec["content_policy"]["student_instruction_max_chars"],
        "expected_response": spec["content_policy"]["expected_response_max_chars"],
        "teacher_model": spec["content_policy"]["teacher_model_max_chars"],
        "teacher_question": spec["content_policy"]["teacher_question_max_chars"],
        "parent_extension": spec["content_policy"]["parent_extension_max_chars"],
    }
    overflow = {
        key: {"length": len(values[key]), "limit": limit}
        for key, limit in limits.items()
        if len(values[key]) > limit
    }
    if overflow:
        raise ValueError(f"Learning-page text exceeds contract limits: {overflow}")
    return {
        "lengths": {key: len(value) for key, value in values.items()},
        "placeholder_count": 0,
        "default_guidance_count": 0,
    }


def validate_components(contract: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    layout = contract["activity"].get("layout_variant")
    layout_spec = spec["layout_variants"].get(layout)
    if not isinstance(layout_spec, dict):
        raise ValueError(f"Unsupported learning layout variant: {layout!r}")
    primary = contract["activity"].get("primary")
    if primary not in layout_spec["activities"]:
        raise ValueError(f"Activity {primary!r} is not permitted by layout {layout!r}")
    components = contract.get("deterministic_components")
    if not isinstance(components, list) or not components:
        raise ValueError("Learning contract requires deterministic worksheet components")
    types: list[str] = []
    rendered_count = 0
    for index, item in enumerate(components):
        if not isinstance(item, dict):
            raise ValueError(f"Deterministic component {index} must be an object")
        component_type = str(item.get("type") or "")
        if component_type not in layout_spec["allowed_component_types"]:
            raise ValueError(f"{layout} does not permit component {component_type!r}")
        types.append(component_type)
        count = item.get("count", 1)
        if not isinstance(count, int) or not 1 <= count <= 8:
            raise ValueError(f"Component {component_type!r} has invalid count {count!r}")
        rendered_count += count
    missing = [value for value in layout_spec["required_component_types"] if value not in types]
    if missing:
        raise ValueError(f"{layout} is missing required worksheet components: {missing}")
    expected_count = contract.get("qa_requirements", {}).get("component_count")
    if expected_count != len(components):
        raise ValueError(
            f"Contract component count mismatch: expected {expected_count}, found {len(components)}"
        )
    return {
        "layout_variant": layout,
        "primary_activity": primary,
        "component_types": types,
        "component_objects": len(components),
        "rendered_response_targets": rendered_count,
    }


def validate_geometry(contract: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    common = template["common_bounds"]
    layout_name = contract["activity"]["layout_variant"]
    layout = template["layout_variants"].get(layout_name)
    if not isinstance(layout, dict):
        raise ValueError(f"No geometry registered for layout {layout_name!r}")
    body = common["learning_body"]
    illustration = layout["illustration"]
    response = layout["response"]
    if not rectangle_inside(illustration, body):
        raise ValueError(f"{layout_name} illustration bounds leave the locked learning body")
    if not rectangle_inside(response, body):
        raise ValueError(f"{layout_name} response bounds leave the locked learning body")
    if rectangles_overlap(illustration, response):
        raise ValueError(f"{layout_name} illustration and response areas overlap")
    if rectangles_overlap(common["teacher_panel"], common["parent_panel"]):
        raise ValueError("Teacher and parent panels overlap")
    return {
        "learning_body": body,
        "illustration": illustration,
        "response": response,
        "illustration_response_gap": response[1] - illustration[3],
        "teacher_parent_overlap": False,
    }


def validate(contract_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    spec = load(CONTRACT_SPEC)
    template = load(TEMPLATE_PATH)
    if contract.get("contract_version") != spec["contract_version"]:
        raise ValueError(
            f"Contract version mismatch: {contract.get('contract_version')!r}; "
            f"expected {spec['contract_version']!r}"
        )
    missing = [section for section in spec["required_sections"] if section not in contract]
    if missing:
        raise ValueError(f"Learning contract is missing sections: {missing}")
    identity = contract["identity"]
    required_identity = [
        "page_id",
        "book_slug",
        "book_title",
        "book_title_lines",
        "level",
        "age",
        "physical_page",
        "page_number",
        "title",
        "page_role",
    ]
    missing_identity = [key for key in required_identity if key not in identity]
    if missing_identity:
        raise ValueError(f"Learning identity is incomplete: {missing_identity}")
    if identity["page_role"] != "learning":
        raise ValueError("Learning Page Contract V2 only supports page_role='learning'")
    if not isinstance(identity["book_title_lines"], list) or not identity["book_title_lines"]:
        raise ValueError("book_title_lines must be a non-empty list")
    if not isinstance(identity["page_number"], int) or identity["page_number"] < 0:
        raise ValueError("page_number must be a non-negative integer")
    illustration_policy = contract["illustration"]
    required_illustration = spec["illustration_policy"]["required_fields"]
    missing_illustration = [key for key in required_illustration if key not in illustration_policy]
    if missing_illustration:
        raise ValueError(f"Illustration policy is incomplete: {missing_illustration}")
    if illustration_policy.get("star_policy") not in spec["illustration_policy"]["star_policy_values"]:
        raise ValueError(f"Invalid Star policy: {illustration_policy.get('star_policy')!r}")
    if not illustration_policy.get("artwork_only"):
        raise ValueError("Illustration policy must require artwork-only input")
    if not illustration_policy.get("no_visible_text"):
        raise ValueError("Illustration policy must prohibit visible text")
    if not illustration_policy.get("no_logo"):
        raise ValueError("Illustration policy must prohibit generated logos")
    if not illustration_policy.get("no_page_layout"):
        raise ValueError("Illustration policy must prohibit page-layout artwork")
    text_qa = validate_text(contract, spec, template)
    component_qa = validate_components(contract, spec)
    geometry_qa = validate_geometry(contract, template)
    illustration = image_metrics(
        resolve(str(contract["assets"]["illustration_path"])),
        "illustration",
        spec["illustration_policy"]["minimum_side_px"],
    )
    if illustration["visible_occupancy"] < spec["illustration_policy"]["minimum_visible_occupancy"]:
        raise ValueError(
            f"Illustration visible occupancy {illustration['visible_occupancy']} is below "
            f"{spec['illustration_policy']['minimum_visible_occupancy']}"
        )
    if illustration["visible_occupancy"] > spec["illustration_policy"]["maximum_visible_occupancy"]:
        raise ValueError(
            f"Illustration visible occupancy {illustration['visible_occupancy']} exceeds "
            f"{spec['illustration_policy']['maximum_visible_occupancy']}"
        )
    logo = image_metrics(resolve(str(contract["assets"]["official_logo_path"])), "official logo", 128)
    semantic_checklist = {
        "scene": illustration_policy["scene"],
        "focal_point": illustration_policy["focal_point"],
        "required_objects": illustration_policy["required_objects"],
        "forbidden_objects": illustration_policy["forbidden_objects"],
        "protected_response_zones": illustration_policy["protected_response_zones"],
        "star_policy": illustration_policy["star_policy"],
        "requires_human_semantic_review": True,
    }
    return {
        "status": "PASS",
        "contract_version": contract["contract_version"],
        "page_id": identity["page_id"],
        "layout_variant": contract["activity"]["layout_variant"],
        "text_qa": text_qa,
        "component_qa": component_qa,
        "geometry_qa": geometry_qa,
        "illustration_qa": illustration,
        "official_logo": logo,
        "semantic_checklist": semantic_checklist,
        "measured": True,
        "hard_coded_pass_flags": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.contract)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BCube Learning Page Contract V2 validation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
