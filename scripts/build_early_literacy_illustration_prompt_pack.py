#!/usr/bin/env python3
"""Build illustration prompts directly from the approved Early Literacy contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/early-literacy-adventures/lkg/curriculum-first-p008-p043-v1.json"
RUNTIME = ROOT / "runtime-contracts/lkg/early-literacy-adventures.json"
OUTPUT = ROOT / "production-prompts/early-literacy-adventures/lkg/v4/phase2-illustration-prompts.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def layout_sentence(count: int) -> str:
    if count == 1:
        return "Create one large coherent illustration centred on the canvas with generous white safe margins."
    columns = 2 if count <= 8 else 3
    rows = (count + columns - 1) // columns
    return (
        f"Arrange the assets in a strict {columns}-column by {rows}-row extraction grid, "
        "following the numbered order below from left to right and top to bottom. "
        "Use wide pure-white gaps; no object may touch, overlap or cross a cell boundary."
    )


def make_prompt(page_id: str, page: dict[str, Any], crops: dict[str, Any]) -> str:
    assets = page["illustration_assets"]
    if not assets:
        return "DETERMINISTIC_NO_ART"
    asset_lines = "\n".join(
        f"{index}. {name}: {description}."
        for index, (name, description) in enumerate(assets.items(), start=1)
    )
    return f"""BCube Content-Aligned Illustration Asset Prompt — {page_id}

BOOK AND LEVEL
Book: Early Literacy Adventures
Level: LKG (4+)
Exact page title: {page['title']}
Learning objective: {page['objective']}
Exact child action: {page['instruction']}

ILLUSTRATION ROLE — LOCKED
Create only the raw illustration artwork required by this exact page contract. Do not create the workbook page. The publishing engine will add all letters, words, sentences, labels, instructions, model example, response mechanics, teacher cue, branding and page number.

EXACT OUTPUT
Create exactly {len(assets)} named visual asset(s), each appearing once:
{asset_lines}

LAYOUT LOCK
{layout_sentence(len(assets))}
The renderer will crop the named assets using the committed crop manifest. Keep every important part fully visible inside its cell.

STYLE
Premium commercial preschool-publishing quality; clean rounded forms; natural friendly expressions where people appear; correct anatomy; bright controlled colours; subtle dimensional shading; pure white background; strong separation; generous safe margins.

TEXT AND WORKSHEET LOCK
No visible words, letters, numerals, handwriting, labels, captions, speech bubbles, instructions, answer marks, circles, ticks, matching lines, arrows, writing boxes, page title, logo, publisher mark, page number, watermark, QR code or official BCube Star mascot.

FAIL CONDITIONS
Reject missing, duplicated, combined, cropped or misordered assets; extra objects; generic classroom or teacher scenes; decorative filler; completed child answers; worksheet frames; dark backgrounds; or artwork that does not directly support the exact child action.
"""


def main() -> int:
    blueprint = load(BLUEPRINT)
    runtime = load(RUNTIME)
    prompts: dict[str, Any] = {}
    for page_id, page in blueprint["pages"].items():
        runtime_page = runtime["pages"][page_id]
        prompts[page_id] = {
            "title": page["title"],
            "output_filename": f"{page_id}.png" if page["illustration_assets"] else "DETERMINISTIC_NO_ART",
            "asset_names": list(page["illustration_assets"]),
            "asset_crops": runtime_page["illustration"]["asset_crops"],
            "prompt": make_prompt(page_id, page, runtime_page["illustration"]["asset_crops"]),
            "status": "READY_FOR_ILLUSTRATION" if page["illustration_assets"] else "DETERMINISTIC_NO_ART",
        }
    document = {
        "version": "early-literacy-phase2-illustration-prompts-v1",
        "book": "Early Literacy Adventures",
        "level": "LKG (4+)",
        "source_blueprint": BLUEPRINT.relative_to(ROOT).as_posix(),
        "policy": "Content-aligned artwork only; exact named assets; deterministic text and worksheet mechanics; no fallback.",
        "pages": prompts,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(prompts)} page prompts to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
