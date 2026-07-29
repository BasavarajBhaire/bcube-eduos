#!/usr/bin/env python3
"""Build content-aligned Logical Thinking illustration prompts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/logical-thinking-adventures/lkg/curriculum-first-p008-p043-v1.json"
RUNTIME = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"
OUTPUT = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/phase2-illustration-prompts.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def layout_sentence(count: int) -> str:
    if count == 1:
        return "Create one large coherent illustration centred on the canvas with generous pure-white safe margins."
    cols = 2 if count <= 12 else 3
    rows = (count + cols - 1) // cols
    return (
        f"Arrange the assets in a strict {cols}-column by {rows}-row extraction grid in the numbered order below. "
        "Keep wide pure-white gaps; no asset may touch, overlap or cross a cell boundary."
    )


def make_prompt(page_id: str, page: dict[str, Any]) -> str:
    assets = page["illustration_assets"]
    if not assets:
        return "DETERMINISTIC_NO_ART"
    lines = "\n".join(f"{index}. {name}: {description}." for index, (name, description) in enumerate(assets.items(), 1))
    return f"""BCube Content-Aligned Illustration Asset Prompt — {page_id}

BOOK AND LEVEL
Book: Logical Thinking Adventures
Level: LKG (4+)
Exact page title: {page['title']}
Learning objective: {page['objective']}
Exact child action: {page['instruction']}

ILLUSTRATION ROLE — LOCKED
Create only the raw illustration artwork required by this page contract. Do not create the workbook page. The publishing engine will add all names, directions, labels, model examples, response circles, number boxes, matching anchors, lines, grids, teacher cue, branding and page number.

EXACT OUTPUT
Create exactly {len(assets)} named visual asset(s), each appearing once:
{lines}

LAYOUT LOCK
{layout_sentence(len(assets))}
Keep every important part fully visible inside its cell. Use a pure white background so the renderer can crop every named asset cleanly.

STYLE
Premium commercial preschool-publishing quality; large recognisable forms; thick clean rounded outlines; friendly natural expressions where people appear; correct anatomy; bright controlled colours; subtle dimensional shading; generous safe margins.

TEXT AND WORKSHEET LOCK
No visible words, letters, numerals, handwriting, labels, captions, speech bubbles, instructions, answer marks, circles, ticks, matching lines, arrows, writing boxes, page title, logo, publisher mark, page number, watermark, QR code or official BCube Star mascot.

FAIL CONDITIONS
Reject missing, duplicated, combined, cropped or misordered assets; extra objects; classroom filler; empty decorative frames; completed child answers; worksheet UI; dark backgrounds; or art that does not directly support the exact child action.
"""


def main() -> int:
    blueprint = load(BLUEPRINT)
    runtime = load(RUNTIME)
    pages: dict[str, Any] = {}
    for page_id, page in blueprint["pages"].items():
        runtime_page = runtime["pages"][page_id]
        pages[page_id] = {
            "title": page["title"],
            "output_filename": f"{page_id}.png" if page["illustration_assets"] else "DETERMINISTIC_NO_ART",
            "asset_names": list(page["illustration_assets"]),
            "asset_crops": runtime_page["illustration"]["asset_crops"],
            "prompt": make_prompt(page_id, page),
            "status": "READY_FOR_ILLUSTRATION" if page["illustration_assets"] else "DETERMINISTIC_NO_ART",
        }
    document = {
        "version": "logical-thinking-phase2-illustration-prompts-v1",
        "book": "Logical Thinking Adventures", "level": "LKG (4+)",
        "source_blueprint": BLUEPRINT.relative_to(ROOT).as_posix(),
        "policy": "Content-aligned artwork only; deterministic text and mechanics; no generic fallback.",
        "pages": pages,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} Logical Thinking illustration prompts to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
