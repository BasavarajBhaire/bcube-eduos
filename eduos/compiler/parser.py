from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ParseError(ValueError):
    pass


@dataclass(frozen=True)
class PageUnit:
    prompt_id: str
    book: str
    level: str
    page_type: str
    title: str
    visible_text: tuple[str, ...]
    template_id: str
    asset_ids: tuple[str, ...]
    raw_manifest: dict[str, Any]


def parse_manifest(path: Path) -> PageUnit:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ParseError(f"cannot read manifest: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ParseError(f"invalid JSON manifest: {exc}") from exc

    identity = payload.get("identity")
    page = payload.get("page")
    composition = payload.get("composition")
    assets = payload.get("assets")
    if not all(isinstance(item, dict) for item in (identity, page, composition, assets)):
        raise ParseError("manifest must contain identity, page, composition and assets objects")

    required = {
        "identity.prompt_id": identity.get("prompt_id"),
        "identity.book": identity.get("book"),
        "identity.level": identity.get("level"),
        "page.type": page.get("type"),
        "page.title": page.get("title"),
        "composition.template": composition.get("template"),
        "assets.logo": assets.get("logo"),
        "assets.illustration": assets.get("illustration"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ParseError("missing required fields: " + ", ".join(missing))

    visible_text = page.get("visible_text", [])
    if not isinstance(visible_text, list) or not all(isinstance(x, str) for x in visible_text):
        raise ParseError("page.visible_text must be a list of strings")

    asset_ids = [assets["logo"], assets["illustration"], *assets.get("characters", [])]
    if len(asset_ids) != len(set(asset_ids)):
        raise ParseError("duplicate asset reference in manifest")

    return PageUnit(
        prompt_id=identity["prompt_id"],
        book=identity["book"],
        level=identity["level"],
        page_type=page["type"],
        title=page["title"],
        visible_text=tuple(visible_text),
        template_id=composition["template"],
        asset_ids=tuple(asset_ids),
        raw_manifest=payload,
    )
