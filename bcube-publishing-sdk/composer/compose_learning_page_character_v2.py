#!/usr/bin/env python3
"""Compose Learning Page V2 and add the official Star asset only when the contract requires it."""
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
POLICY_ENFORCER = ROOT / "bcube-publishing-sdk/normalizers/enforce_learning_illustration_policy_v2.py"
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
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
    evidence["semantic_review"]["uploaded_illustration_contains_star"] = False
    evidence_output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compose(contract_path: Path, output: Path, evidence_output: Path) -> None:
    policy_module = load_module("bcube_learning_illustration_policy_v2", POLICY_ENFORCER)
    contract = load(contract_path)
    policy_module.enforce_policy(contract)
    contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base = load_module("bcube_learning_page_v2_base", BASE_COMPOSER)
    base.compose(contract_path, output, evidence_output)
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
