#!/usr/bin/env python3
"""Compile curriculum-first Early Maths P009-P021 into runtime and illustration artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "curriculum" / "early-maths-adventures" / "lkg" / "curriculum-first-p009-p021-v1.json"
RUNTIME_OUT = ROOT / "runtime-contracts" / "refinements" / "early-maths-lkg-curriculum-first-p009-p021.json"
PROMPT_OUT = ROOT / "production-prompts" / "early-maths-adventures" / "lkg" / "v4" / "regeneration" / "curriculum-first-p009-p021-prompts-v1.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def prompt_for(page_id: str, page: dict[str, Any]) -> str:
    assets = page.get("illustration_assets", {})
    asset_lines = "\n".join(f"- {name}: {desc}" for name, desc in assets.items()) or "- No generated illustration required. The publishing engine creates the complete activity deterministically."
    names = ", ".join(assets) or "none"
    return f"""BCube Curriculum-First Illustration Prompt — {page_id}

BOOK AND LEVEL
Book: Early Maths Adventures
Level: LKG (4+)
Exact page title: {page['title']}
Learning objective: {page['objective']}
Exact child action: {page['instruction']}
Page archetype: {page['archetype']}
Teaching mechanic: {page['mechanic']}

ILLUSTRATION ROLE — LOCKED
Create only the raw visual assets required by the approved teaching blueprint. Do not create or imitate the workbook page. The publishing engine adds the title, instruction, model example, numerals, symbols, prompts, answer choices, connector dots, matching lines, response circles, writing boxes, number lines, jump arcs, teacher cue, branding and page number.

EXACT NAMED ASSETS
{asset_lines}

TEACHING ALIGNMENT
The illustration must support this child thinking: {page['child_thinking']}
Expected child response: {page['expected_response']}

CROP-SAFE LOCK
Use the exact crop names: {names}. Keep each named asset isolated on pure white with at least 10% inter-zone white gutter and 8% clear internal padding. No touching, overlap, merged shadows or neighbouring-object contamination. Make countable objects large and individually distinguishable.

STRICT EXCLUSIONS
No complete worksheet, title, instruction, labels, answer state, numeral unless explicitly named as an asset, card border, panel, response box, response circle, matching line, arrow, number line, tick mark, sequence slot, dotted blank, comparison symbol, crossed-out object, logo, mascot, teacher cue, watermark, QR code, mockup or alternate.

VALIDATION GATES
- {'; '.join(page['validation_gates'])}
- Every expected asset is present exactly once and is independently crop-safe.
- The illustration must not change the approved mechanic “{page['mechanic']}”."""


def main() -> int:
    source = load_json(SOURCE)
    pages = source["pages"]
    runtime_pages: dict[str, Any] = {}
    prompts: dict[str, Any] = {}
    for page_id, page in pages.items():
        runtime_pages[page_id] = {
            "identity": {"title": page["title"]},
            "learning": {
                "objective": page["objective"],
                "instruction": page["instruction"],
                "expected_response": page["expected_response"],
                "model_text": page["model_example"]
            },
            "activity": {
                "archetype": page["archetype"],
                "mechanic": page["mechanic"],
                "render_kind": page["render_kind"],
                "response_mode": "page-specific",
                "mechanics": page["renderer_controls"]
            },
            "illustration": {
                "assets": list(page.get("illustration_assets", {})),
                "requires_generated_art": bool(page.get("illustration_assets")),
                "asset_meanings": page.get("illustration_assets", {})
            },
            "layout": {
                "template": page["archetype"],
                "blueprint": page["layout"],
                "parent_panel": False,
                "home_connection": False,
                "generic_response_panel": False
            },
            "guidance": {"teacher_cue": page["teacher_cue"]},
            "validation": {
                "status": "CURRICULUM_LOCKED",
                "allow_fallback": False,
                "teaching_gates": page["validation_gates"]
            }
        }
        prompts[page_id] = {
            "title": page["title"],
            "requires_generated_art": bool(page.get("illustration_assets")),
            "named_assets": page.get("illustration_assets", {}),
            "prompt": prompt_for(page_id, page)
        }

    RUNTIME_OUT.parent.mkdir(parents=True, exist_ok=True)
    PROMPT_OUT.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_OUT.write_text(json.dumps({
        "version": "early-maths-curriculum-first-p009-p021-v1",
        "scope": list(pages),
        "policy": source["global_rules"],
        "pages": runtime_pages
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PROMPT_OUT.write_text(json.dumps({
        "version": "early-maths-curriculum-first-prompts-p009-p021-v1",
        "pages": prompts
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source": str(SOURCE),
        "runtime_output": str(RUNTIME_OUT),
        "prompt_output": str(PROMPT_OUT),
        "pages": len(pages),
        "policy": "Teaching blueprint is compiled before illustration and renderer implementation."
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
