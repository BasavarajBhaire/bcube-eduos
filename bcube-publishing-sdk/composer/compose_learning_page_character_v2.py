#!/usr/bin/env python3
"""Compose Learning Page V2 with compact adult highlights and approved Star policy."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"


def load_module():
    spec = importlib.util.spec_from_file_location("bcube_learning_page_v2_base", BASE_COMPOSER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {BASE_COMPOSER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trim_near_white(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    image.putdata(
        [
            (255, 255, 255, 0) if r > 246 and g > 246 and b > 246 else (r, g, b, a)
            for r, g, b, a in image.getdata()
        ]
    )
    bbox = image.getbbox()
    if bbox is None:
        raise ValueError("Official Star asset contains no visible artwork")
    return image.crop(bbox)


def install_refined_learning_components(base) -> None:
    """Replace oversized adult panels and improve primary-colour model cues."""
    original_model_example = base.model_example_box

    def compact_adult_panel(draw, bounds, heading, body, fill, outline, template):
        colours = template["colours"]
        typography = template["typography"]
        x0, y0, x1, y1 = bounds
        display_heading = {
            "TEACHER GUIDANCE": "TEACHER TIP",
            "PARENT PARTNERSHIP": "HOME CONNECTION",
        }.get(heading, heading)
        draw.rounded_rectangle(bounds, radius=26, fill=colours["white"], outline=outline, width=4)
        banner = [x0 + 16, y0 + 14, x1 - 16, y0 + 78]
        draw.rounded_rectangle(banner, radius=22, fill=fill, outline=outline, width=2)
        heading_render = base.fitted_text(
            draw,
            display_heading,
            [banner[0] + 20, banner[1] + 4, banner[2] - 20, banner[3] - 4],
            max_size=typography["adult_heading"],
            min_size=24,
            colour=colours["navy"],
            bold=True,
            max_lines=1,
        )
        body_render = base.fitted_text(
            draw,
            body,
            [x0 + 30, y0 + 92, x1 - 30, y1 - 22],
            max_size=typography["adult_body_max"],
            min_size=typography["adult_body_min"],
            colour=colours["line"],
            align="left",
            max_lines=7,
        )
        return {
            "bounds": bounds,
            "style": "compact-highlight",
            "banner": banner,
            "heading": heading_render,
            "body": body_render,
        }

    def refined_model_example(draw, bounds, label_text, colours, typography):
        lowered = str(label_text).casefold()
        if not all(value in lowered for value in ("red", "yellow", "blue")):
            return original_model_example(draw, bounds, label_text, colours, typography)
        draw.rounded_rectangle(bounds, radius=24, fill=colours["gold"], outline="#E1B12C", width=3)
        x0, y0, x1, y1 = bounds
        swatches = [
            ("Red", "#E53935"),
            ("Yellow", "#FFD600"),
            ("Blue", "#1565C0"),
        ]
        gap = 34
        usable = x1 - x0 - 80
        item_width = (usable - gap * 2) // 3
        rendered = []
        for index, (name, fill) in enumerate(swatches):
            left = x0 + 40 + index * (item_width + gap)
            item = [left, y0 + 18, left + item_width, y1 - 18]
            draw.rounded_rectangle(item, radius=22, fill=colours["white"], outline=fill, width=4)
            circle_size = min(74, item[3] - item[1] - 20)
            circle = [item[0] + 24, item[1] + (item[3] - item[1] - circle_size) // 2,
                      item[0] + 24 + circle_size, item[1] + (item[3] - item[1] + circle_size) // 2]
            draw.ellipse(circle, fill=fill, outline="#FFFFFF", width=3)
            text = base.fitted_text(
                draw,
                name,
                [circle[2] + 18, item[1] + 8, item[2] - 16, item[3] - 8],
                max_size=typography["component_label_max"],
                min_size=typography["component_label_min"],
                colour=colours["navy"],
                bold=True,
                align="left",
                max_lines=1,
            )
            rendered.append({"name": name, "bounds": item, "swatch": circle, "text": text})
        return {"type": "model_example", "bounds": bounds, "style": "primary-colour-swatches", "items": rendered}

    base.adult_panel = compact_adult_panel
    base.model_example_box = refined_model_example


def overlay_official_star(contract: dict[str, Any], output: Path, evidence_output: Path) -> None:
    policy = contract["illustration"]["star_policy"]
    if policy in {"prohibited", "not-required"}:
        return
    if policy != "official-asset-separate":
        raise ValueError(f"Unsupported Star policy: {policy!r}")
    star_value = contract.get("assets", {}).get("official_star_path")
    if not star_value:
        raise ValueError("Contract requires the official Star asset but official_star_path is missing")
    template = load(TEMPLATE_PATH)
    layout = template["layout_variants"][contract["activity"]["layout_variant"]]
    illustration_bounds = layout["illustration"]
    x0, y0, x1, y1 = illustration_bounds
    max_width = min(330, round((x1 - x0) * 0.18))
    max_height = min(360, round((y1 - y0) * 0.28))
    star = trim_near_white(resolve(str(star_value)))
    scale = min(max_width / star.width, max_height / star.height)
    width = max(1, round(star.width * scale))
    height = max(1, round(star.height * scale))
    star = star.resize((width, height), Image.Resampling.LANCZOS)
    left = x1 - width - 34
    top = y1 - height - 28
    with Image.open(output) as page:
        canvas = page.convert("RGBA")
    canvas.paste(star, (left, top), star)
    canvas.convert("RGB").save(output, "PNG", dpi=(template["canvas"]["dpi"], template["canvas"]["dpi"]))
    evidence = load(evidence_output)
    evidence["components"]["official_star"] = {
        "asset_path": str(resolve(str(star_value))),
        "rendered_bounds": [left, top, left + width, top + height],
        "policy": policy,
    }
    evidence["inputs"]["star_sha256"] = sha256(resolve(str(star_value)))
    evidence["artifact_sha256"] = sha256(output)
    evidence["semantic_review"]["star_policy"] = policy
    evidence_output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compose(contract_path: Path, output: Path, evidence_output: Path) -> None:
    base = load_module()
    install_refined_learning_components(base)
    base.compose(contract_path, output, evidence_output)
    contract = load(contract_path)
    overlay_official_star(contract, output, evidence_output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()
    compose(args.contract, args.output, args.evidence_output)
    print(json.dumps({"status": "COMPOSED_WITH_CHARACTER_POLICY", "artifact": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"BCube learning-page character composition FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
