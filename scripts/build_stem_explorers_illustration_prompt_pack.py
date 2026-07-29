#!/usr/bin/env python3
"""Build content-aligned STEM Explorers LKG illustration prompts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/stem-explorers/lkg/curriculum-first-p008-p043-v1.json"
OUTPUT = ROOT / "production-prompts/stem-explorers/lkg/v4/phase2-illustration-prompts.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def layout_sentence(count: int) -> str:
    if count == 1:
        return "Create one large coherent visual centred on the canvas with generous pure-white safe margins."
    columns = 2 if count <= 6 else 3
    rows = (count + columns - 1) // columns
    return (
        f"Arrange the assets in a strict {columns}-column by {rows}-row extraction grid in the numbered order below. "
        "Use wide pure-white gutters. No asset may touch, overlap or cross a cell boundary."
    )


def make_prompt(page_id: str, page: dict[str, Any]) -> str:
    assets: dict[str, str] = page["illustration_assets"]
    if not assets:
        return "DETERMINISTIC_NO_ART"
    listing = "\n".join(
        f"{index}. {name}: {description}." for index, (name, description) in enumerate(assets.items(), 1)
    )
    return f"""BCube Content-Aligned Illustration Asset Prompt — {page_id}

BOOK AND LEVEL
Book: STEM Explorers
Level: LKG (4+)
Exact page title: {page['title']}
Learning objective: {page['objective']}
Exact child action: {page['instruction']}

ILLUSTRATION ROLE — LOCKED
Create only the raw visual artwork required by this exact activity. Do not create the workbook page. The publishing engine will add the title, learning goal, instruction, object names, labels, completed example, number boxes, answer controls, matching anchors, routes, grids, writing and drawing spaces, teacher cue, logo and page number.

EXACT OUTPUT
Create exactly {len(assets)} visual asset(s), each appearing once:
{listing}

LAYOUT LOCK
{layout_sentence(len(assets))}
Every person, animal and object must be fully visible and comfortably inside its cell. Use a pure white background so every named asset can be extracted cleanly.

STYLE
Premium commercial preschool-publishing illustration; large recognisable forms; thick clean rounded outlines; friendly natural expressions; correct anatomy and object structure; bright controlled colours; subtle dimensional shading; strong separation; generous crop-safe margins.

TEXT AND WORKSHEET LOCK
No visible words, letters, numerals, handwriting, labels, captions, speech bubbles, instructions, answer marks, ticks, crosses, matching lines, arrows, writing boxes, grids, page title, logo, publisher mark, page number, watermark, QR code or official BCube Star mascot.

FAIL CONDITIONS
Reject missing, duplicated, combined, cropped, contaminated or misordered assets; extra filler; unrelated classroom props; decorative empty frames; completed answers; worksheet UI; dark backgrounds; tiny learning targets; or art that does not directly support the exact child action.
"""


def main() -> int:
    blueprint = load(BLUEPRINT)
    pages: dict[str, Any] = {}
    for page_id, page in blueprint["pages"].items():
        pages[page_id] = {
            "title": page["title"],
            "output_filename": f"{page_id}.png" if page["illustration_assets"] else "DETERMINISTIC_NO_ART",
            "asset_names": list(page["illustration_assets"]),
            "prompt": make_prompt(page_id, page),
            "status": "READY_FOR_ILLUSTRATION" if page["illustration_assets"] else "DETERMINISTIC_NO_ART",
        }
    OUTPUT.write_text(json.dumps({
        "version": "stem-explorers-phase2-illustration-prompts-v1",
        "book": "STEM Explorers",
        "level": "LKG (4+)",
        "source_blueprint": BLUEPRINT.relative_to(ROOT).as_posix(),
        "policy": "Content-aligned artwork only; deterministic text and mechanics; no generic fallback.",
        "pages": pages,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} STEM illustration prompts to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
