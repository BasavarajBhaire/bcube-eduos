#!/usr/bin/env python3
"""Deterministic BCube A4 page composer.

Composition is fail-closed: the exact versioned template and every referenced
asset must resolve successfully before a render plan can be produced.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from asset_registry import AssetRegistryError, ResolvedAsset, resolve_asset
from template_registry import TemplateRegistry, TemplateRegistryError

A4_WIDTH = 2480
A4_HEIGHT = 3508
DPI = 300


class CompositionPreflightError(RuntimeError):
    """Raised when composition dependencies cannot be verified."""


def _asset_ids(manifest: dict[str, Any]) -> list[str]:
    assets = manifest["assets"]
    ordered: list[str] = [assets["logo"], assets["illustration"]]
    ordered.extend(assets.get("characters", []))
    if len(ordered) != len(set(ordered)):
        raise CompositionPreflightError("duplicate asset reference in manifest")
    return ordered


def preflight(
    manifest: dict[str, Any],
    *,
    repository_root: Path,
    template_registry_path: Path,
    asset_registry_path: Path,
) -> dict[str, Any]:
    """Resolve the exact template and all immutable assets.

    No render plan is returned unless every dependency passes validation.
    """
    try:
        template = TemplateRegistry(template_registry_path).resolve(
            manifest["composition"]["template"]
        )
        resolved_assets: list[ResolvedAsset] = [
            resolve_asset(asset_id, asset_registry_path, repository_root)
            for asset_id in _asset_ids(manifest)
        ]
    except (KeyError, TemplateRegistryError, AssetRegistryError) as exc:
        raise CompositionPreflightError(str(exc)) from exc

    page_type = manifest["page"]["type"]
    if template["page_type"] != page_type:
        raise CompositionPreflightError(
            f"template page_type {template['page_type']} does not match manifest page_type {page_type}"
        )

    canvas = template["canvas"]
    if (
        canvas["width_px"] != A4_WIDTH
        or canvas["height_px"] != A4_HEIGHT
        or canvas["dpi"] != DPI
    ):
        raise CompositionPreflightError("template canvas does not match locked A4 geometry")

    if page_type == "cover" and manifest["page"].get("show_page_number", True):
        raise CompositionPreflightError("cover pages cannot show a page number")

    return {
        "template": template,
        "assets": [
            {
                **asdict(asset),
                "path": str(asset.path),
            }
            for asset in resolved_assets
        ],
    }


def build_plan(
    manifest: dict[str, Any],
    *,
    repository_root: Path = Path("."),
    template_registry_path: Path = Path("eduos/registries/template-registry.json"),
    asset_registry_path: Path = Path("eduos/registries/asset-registry.json"),
) -> dict[str, Any]:
    verified = preflight(
        manifest,
        repository_root=repository_root,
        template_registry_path=template_registry_path,
        asset_registry_path=asset_registry_path,
    )
    page = manifest["page"]
    return {
        "canvas": {
            "width": A4_WIDTH,
            "height": A4_HEIGHT,
            "dpi": DPI,
            "background": manifest["composition"].get("background", "#FFFFFF"),
        },
        "template": verified["template"],
        "resolved_assets": verified["assets"],
        "layers": [
            {"kind": "illustration", "asset": manifest["assets"]["illustration"], "mode": "contain"},
            {"kind": "logo", "asset": manifest["assets"]["logo"], "mode": "exact_asset"},
            {"kind": "title", "text": page["title"], "mode": "deterministic_text"},
            {"kind": "visible_text", "items": page["visible_text"], "mode": "deterministic_text"},
            {"kind": "page_number", "value": page["number"], "visible": page.get("show_page_number", True)},
        ],
        "output_filename": f"{manifest['identity']['prompt_id']}.png",
    }


def render(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    repository_root: Path = Path("."),
    template_registry_path: Path = Path("eduos/registries/template-registry.json"),
    asset_registry_path: Path = Path("eduos/registries/asset-registry.json"),
) -> Path:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("Rendering requires Pillow: pip install Pillow") from exc

    plan = build_plan(
        manifest,
        repository_root=repository_root,
        template_registry_path=template_registry_path,
        asset_registry_path=asset_registry_path,
    )
    canvas = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), plan["canvas"]["background"])
    draw = ImageDraw.Draw(canvas)
    # Rendering remains a deterministic proof until the typography registry is locked.
    # Crucially, rendering cannot begin until template and asset preflight succeeds.
    draw.rectangle((100, 100, A4_WIDTH - 100, A4_HEIGHT - 100), outline="black", width=4)
    draw.text((140, 140), manifest["page"]["title"], fill="black")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / plan["output_filename"]
    canvas.save(output, dpi=(DPI, DPI))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose a deterministic BCube page")
    parser.add_argument("manifest")
    parser.add_argument("output_dir", nargs="?")
    parser.add_argument("--root", default=".")
    parser.add_argument("--template-registry", default="eduos/registries/template-registry.json")
    parser.add_argument("--asset-registry", default="eduos/registries/asset-registry.json")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    kwargs = {
        "repository_root": Path(args.root),
        "template_registry_path": Path(args.template_registry),
        "asset_registry_path": Path(args.asset_registry),
    }
    if args.output_dir is None:
        print(json.dumps(build_plan(manifest, **kwargs), indent=2))
        return 0
    output = render(manifest, Path(args.output_dir), **kwargs)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
