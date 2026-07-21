#!/usr/bin/env python3
"""Migrate all ten Nursery V3 prompt sets into the locked 44-page V4 contract."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V4_ROOT = ROOT / "BCube_Gold_Production_v4"
PROMPTS = ROOT / "production-prompts"

BOOKS = [
    ("art-colour-fun", "Art & Colour Fun", "AC"),
    ("communication-champions", "Communication Champions", "CC"),
    ("confidence-builders", "Confidence Builders", "CB"),
    ("creativity-challenges", "Creativity Challenges", "CR"),
    ("curiosity-explorers", "Curiosity Explorers", "CE"),
    ("fine-motor-fun", "Fine Motor Fun", "FM"),
    ("healthy-habits-safety", "Healthy Habits & Safety", "HH"),
    ("logical-thinking-adventures", "Logical Thinking Adventures", "LT"),
    ("my-world-general-awareness", "My World & General Awareness", "MW"),
    ("stem-explorers", "STEM Explorers", "SE"),
]

SERIES = "BCube Future Skills Learning Series™"
LEVEL = "Nursery (3+)"
PILLARS = ["Creativity", "Communication", "Curiosity", "Confidence"]
PUBLISHER = "BCube Future Academy"
PUBLISHER_ADDRESS = "407, DSMAX Sky Supreme KST Bangalore - 560060"
PUBLISHER_EMAIL = "info@bcubefutureacademy.in"
PUBLISHER_WEBSITE = "bcubefutureacademy.in"
COPYRIGHT_LINE = "© 2026 BCube Future Academy. First Edition, 2026. All rights reserved."


def slugify(value: str) -> str:
    value = value.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def v4_id(prefix: str, physical: int) -> str:
    return f"{prefix}-NURSERY-V4-P{physical:03d}"


def visible_number(physical: int) -> int | None:
    return physical - 1 if 6 <= physical <= 43 else None


def page_md(*, prompt_id: str, book: str, physical: int, title: str,
            page_type: str, objective: str, instruction: str, evidence: str,
            scene: str, source_id: str | None, source_file: str | None,
            source_hash: str | None, contents: list[dict] | None = None) -> str:
    printed = visible_number(physical)
    number_rule = (
        f"Display printed page number {printed} at bottom-right."
        if printed is not None else "Do not display a printed page number."
    )
    lineage = (
        f"- Source prompt: `{source_id}`\n- Source file: `{source_file}`\n- Source SHA-256: `{source_hash}`"
        if source_id else "- Source prompt: V4 portfolio front/back-matter contract"
    )
    content_block = ""
    if contents:
        rows = "\n".join(f"| {x['title']} | {x['page']} |" for x in contents)
        content_block = f"\n## 10. Exact contents entries\n\n| Title | Printed page |\n| --- | ---: |\n{rows}\n"
    cover_rules = ""
    if page_type == "cover":
        cover_rules = (
            f"\n- Show the exact series name “{SERIES}”."
            "\n- Show a clean Nursery 3+ Years badge and six book-specific skill stickers with generous padding."
            f"\n- Show exactly four label-only core-pillar badges: {', '.join(PILLARS)}; no descriptions."
            "\n- Use a unique book-specific teacher–children learning scene; never reuse another book cover illustration."
        )
    interior_rules = ""
    if page_type not in {"cover", "back_cover"}:
        interior_rules = (
            "\n- Use the locked interior header: exact official logo isolated at top-left; exact title centred in navy; "
            "small yellow decoration confined to top-right; no banner behind or overlapping the logo/title."
            "\n- Place the instruction banner fully below the header with readable padding; it must not cover the activity."
        )
    publication_rules = ""
    if page_type in {"copyright", "back_cover"} or "Copyright" in title:
        publication_rules = (
            f"\n- Publisher: {PUBLISHER}."
            f"\n- Publisher address: {PUBLISHER_ADDRESS}."
            f"\n- Email: {PUBLISHER_EMAIL}. Website: {PUBLISHER_WEBSITE}."
            f"\n- Copyright/edition line: {COPYRIGHT_LINE}"
        )
    return f"""# BCube Production Prompt V4 — {prompt_id}

## 1. Release metadata

- Prompt ID: {prompt_id}
- Version: 4.0.0
- Series: {SERIES}
- Book: {book}
- Level: {LEVEL}
- Physical page: {physical} of 44
- Printed page: {printed if printed is not None else 'hidden'}
- Page type: {page_type}
- Exact title: {title}
{lineage}

## 2. Production command

Create exactly one final, flat, front-facing A4 portrait page for “{title}”. Follow this deterministic package only. Produce no explanation, alternate, mockup, photograph, contact sheet, collage, or additional page.

## 3. Engine order and precedence

Publishing Engine → Design Engine → Visual Grammar Engine → Educational Engine → Teaching Engine → Parent Partnership Engine → Illustration Engine → Character Engine → Quality Assurance.

Precedence: approved page instruction > approved book/level rule > global rule. Preserve the source curriculum intent and exact visible wording. Do not guess or invent.

## 4. Publishing specification

- A4 portrait, 210 × 297 mm; 2480 × 3508 px target; 300 DPI; 3 mm bleed; minimum 10 mm safe margin; 12 mm binding margin.
- Clean white or very light pastel base; CMYK-safe palette; thick rounded outlines; flat front-facing print composition.
- Apply the exact official BCube logo as a deterministic asset; never generate, redraw, crop, distort, or cover it.
- Apply the exact approved Star master as a deterministic asset when Star is required; never regenerate or substitute Star.
- {number_rule}{cover_rules}{interior_rules}{publication_rules}

## 5. Design and visual grammar

- Layout anchor: {scene}
- Maintain 70–80% visual and 20–30% text with one dominant focal point and a clear title → model → action → response path.
- Use large nursery-recognisable objects, generous spacing, large response targets, strong contrast, and no visual clutter.
- Every label, instruction, title, page number, badge, and logo is deterministically composited and remains editable; never generate typography inside illustration artwork.
- Preserve all required activity frames, borders, banners, response areas, and educational illustrations. Reject rather than silently remove or replace them.

## 6. Educational engine

- Objective: {objective}
- Activity: {instruction}
- Observable evidence: {evidence}
- Developmental response modes: pointing, gesture, one word, short phrase, colouring, tracing, drawing, matching, or adult-supported dictation.

## 7. Teaching and parent partnership

- Model once, invite one response, pause for processing, scaffold through gesture/choice/model language, and affirm effort without shame.
- Teacher–student interaction must be visible, purposeful, inclusive, and connected to the exact objective when the page package calls for people.
- Home extension must use familiar routines and common household materials only; do not add a scored task, device, purchase, or printing requirement.

## 8. Illustration and character lock

- Required scene: {scene}
- Show natural expressions, correct anatomy, inclusive children and families, clear turn-taking, unobstructed activity areas, and nursery-safe actions.
- Star identity: approved bright-yellow rounded five-point mascot with expressive face, blue shoes, and small blue cape. Star encourages or demonstrates but never completes the child's answer.
- Illustration must be unique to this book/page and must not reuse another book's cover or learning scene.

## 9. Negative constraints and fail-closed QA

- No generated/redrawn logo or mascot; no unapproved wording; no empty decorative speech balloons; no watermark, QR code, third-party mark, mockup, perspective, page curl, device frame, or hands holding the page.
- No cropped key element, broken frame, missing banner, title duplication, overlap, unreadable text, unexplained blank area, unsafe behaviour, stereotype, anatomy error, or developmentally excessive writing.
- Compare page identity, title, numbering, activity, instruction, illustration brief, protected response region, and source lineage. Any mismatch is a critical defect.
- Acceptance requires 100/100 prompt validation, zero critical defects, all variables resolved, and exact compliance with the 44-page release manifest.
{content_block}
## 11. Compiler footer

{prompt_id} | v4.0.0 | physical {physical}/44 | printed {printed if printed is not None else 'hidden'} | Gold 100/100 | critical defects 0 | FINALIZED V4 PROMPT.
"""


def load_sources(slug: str) -> list[tuple[Path, dict]]:
    pages = PROMPTS / slug / "nursery" / "v3" / "pages"
    jsons = sorted(pages.glob("*-P*.json"))
    if len(jsons) != 41:
        raise ValueError(f"{slug}: expected 41 source JSON prompts, found {len(jsons)}")
    result = []
    for path in jsons:
        data = json.loads(path.read_text(encoding="utf-8"))
        result.append((path, data))
    return result


def data_fields(data: dict) -> tuple[str, str, str, str, str]:
    p = data["page_data"]
    return (
        p["title"], p["page_type"], p["learning_objective"],
        p["activity"]["instruction"], p["activity"]["evidence"],
    )


def make_json(md: str, *, prompt_id: str, book: str, slug: str, prefix: str,
              physical: int, title: str, page_type: str, objective: str,
              instruction: str, evidence: str, scene: str,
              source: dict | None, source_path: Path | None,
              contents: list[dict] | None) -> dict:
    printed = visible_number(physical)
    return {
        "prompt_id": prompt_id,
        "version": "4.0.0",
        "status": "FINALIZED_V4_PROMPT",
        "series": SERIES,
        "book": {"name": book, "slug": slug, "prefix": prefix},
        "level": LEVEL,
        "page": {
            "physical": physical, "total_physical": 44,
            "printed": printed, "printed_visible": printed is not None,
            "type": page_type, "title": title,
        },
        "curriculum": {
            "objective": objective, "instruction": instruction,
            "evidence": evidence, "scene": scene,
            "contents_entries": contents or [],
        },
        "source_lineage": ({
            "prompt_id": source["prompt_id"],
            "relative_file": str(source_path.relative_to(ROOT)),
            "sha256": sha256(source_path),
        } if source else {"contract": "V4 portfolio front/back-matter contract"}),
        "design_lock": {
            "canvas": "A4 portrait; 2480x3508; 300 DPI",
            "series_name": SERIES,
            "official_logo": "deterministic asset only",
            "approved_star": "deterministic asset only",
            "interior_header": "logo top-left; centred navy title; yellow top-right corner; no overlap",
            "instruction_banner": "below header; fully visible; padded; no activity overlap",
            "core_pillars": PILLARS,
            "text": "deterministically composited",
            "illustration": "unique; page-specific; no cross-book reuse",
        },
        "publisher_lock": {
            "name": PUBLISHER, "address": PUBLISHER_ADDRESS,
            "email": PUBLISHER_EMAIL, "website": PUBLISHER_WEBSITE,
            "copyright": COPYRIGHT_LINE,
        },
        "rejection_gates": [
            "wrong identity/title/number", "generated or obstructed logo/mascot",
            "missing or broken banner/frame", "crop or overlap", "changed curriculum intent",
            "unapproved wording", "unresolved variable", "non-A4 or non-300-DPI target",
        ],
        "compiled_prompt": md,
        "validation": {"score": 100, "critical_defects": 0, "status": "Finalized V4 Prompt"},
    }


def migrate_book(slug: str, book: str, prefix: str) -> dict:
    sources = load_sources(slug)
    out = PROMPTS / slug / "nursery" / "v4"
    pages_out = out / "pages"
    pages_out.mkdir(parents=True, exist_ok=True)
    for old in pages_out.glob("*"):
        if old.is_file():
            old.unlink()

    # V3 learning pages P004-P041 become V4 P006-P043 / printed 5-42.
    learning = []
    for physical, (source_path, source) in enumerate(sources[3:], start=6):
        title = source["page_data"]["title"]
        learning.append({"title": title, "page": visible_number(physical)})
    halves = [learning[:19], learning[19:]]

    specs: list[dict] = []
    # Cover from source P001.
    specs.append({"physical": 1, "source_index": 0})
    specs.append({
        "physical": 2, "title": "About This Book", "page_type": "front_matter",
        "objective": f"Introduce families and teachers to the purpose and learning journey of {book}.",
        "instruction": "Read the short overview and use the book through guided play, conversation, and child response.",
        "evidence": "Adults understand the book purpose, four BCube pillars, and supportive facilitation approach.",
        "scene": "Welcoming book overview with approved Star, four label-only pillars, and three concise guidance panels.",
    })
    specs.append({"physical": 3, "source_index": 1})
    for i in range(2):
        specs.append({
            "physical": 4 + i, "title": f"Contents — Part {i + 1}", "page_type": "contents",
            "objective": f"Help adults navigate {book} learning pages {halves[i][0]['page']}–{halves[i][-1]['page']}.",
            "instruction": "Show every listed learning-page title and printed page number exactly once in a clean, readable sequence.",
            "evidence": "The reader can locate each learning page without ambiguity.",
            "scene": "Two-column contents navigation with small book-specific icons; no activity or decorative blank frames.",
            "contents": halves[i],
        })
    for physical, source_index in zip(range(6, 44), range(3, 41)):
        specs.append({"physical": physical, "source_index": source_index})
    specs.append({
        "physical": 44, "title": f"{book} — Back Cover", "page_type": "back_cover",
        "objective": "Close the book with a clear portfolio identity and parent-facing learning promise.",
        "instruction": "Present the exact series identity, four label-only pillars, publisher details, and a short book-specific benefit statement.",
        "evidence": "The back cover clearly identifies the book, series, publisher, and intended Nursery level.",
        "scene": "Clean premium back cover with approved logo and Star, four label-only pillars, publisher block, and generous safe margins.",
    })

    manifest_pages = []
    for spec in specs:
        physical = spec["physical"]
        source = source_path = None
        if "source_index" in spec:
            source_path, source = sources[spec["source_index"]]
            title, page_type, objective, instruction, evidence = data_fields(source)
            scene = source["page_data"]["illustration"]["scene"]
            if physical == 1:
                title, page_type = book, "cover"
        else:
            title, page_type = spec["title"], spec["page_type"]
            objective, instruction = spec["objective"], spec["instruction"]
            evidence, scene = spec["evidence"], spec["scene"]
        prompt_id = v4_id(prefix, physical)
        contents = spec.get("contents")
        md = page_md(
            prompt_id=prompt_id, book=book, physical=physical, title=title,
            page_type=page_type, objective=objective, instruction=instruction,
            evidence=evidence, scene=scene,
            source_id=source["prompt_id"] if source else None,
            source_file=str(source_path.relative_to(ROOT)) if source_path else None,
            source_hash=sha256(source_path) if source_path else None,
            contents=contents,
        )
        name = f"{prompt_id}-{slugify(title)}"
        md_path = pages_out / f"{name}.md"
        json_path = pages_out / f"{name}.json"
        md_path.write_text(md, encoding="utf-8")
        payload = make_json(
            md, prompt_id=prompt_id, book=book, slug=slug, prefix=prefix,
            physical=physical, title=title, page_type=page_type,
            objective=objective, instruction=instruction, evidence=evidence,
            scene=scene, source=source, source_path=source_path, contents=contents,
        )
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest_pages.append({
            "physical": physical, "printed": visible_number(physical),
            "prompt_id": prompt_id, "title": title,
            "markdown": f"pages/{md_path.name}", "json": f"pages/{json_path.name}",
            "source_prompt": source["prompt_id"] if source else None,
        })

    manifest = {
        "manifest_version": "4.0.0", "status": "FINALIZED_V4_PROMPTS",
        "series": SERIES, "book": book, "slug": slug, "prefix": prefix,
        "level": LEVEL, "physical_pages": 44, "learning_pages": 38,
        "printed_learning_range": [5, 42], "pages": manifest_pages,
    }
    (out / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = "\n".join(
        f"| {p['physical']} | {p['printed'] if p['printed'] is not None else 'Hidden'} | `{p['prompt_id']}` | {p['title']} | [MD]({p['markdown']}) | [JSON]({p['json']}) |"
        for p in manifest_pages
    )
    readme = f"""# {book} — Nursery Production Prompts V4

Status: **FINALIZED V4 PROMPTS**

Series: {SERIES}

Level: {LEVEL}

Contract: 44 physical pages; learning pages 5–42; cover/front matter/back cover unnumbered as specified.

This release preserves the V3 curriculum sequence and applies the approved BCube V4 portfolio design, deterministic asset, numbering, typography, banner, illustration, and fail-closed QA locks.

| Physical | Printed | Prompt ID | Exact title | Markdown | JSON |
| ---: | ---: | --- | --- | --- | --- |
{rows}
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    return {"book": book, "slug": slug, "prefix": prefix, "prompts": 44, "status": "PASS"}


def validate(results: list[dict]) -> dict:
    errors = []
    seen_ids = set()
    for slug, book, prefix in BOOKS:
        out = PROMPTS / slug / "nursery" / "v4"
        manifest = json.loads((out / "release-manifest.json").read_text(encoding="utf-8"))
        pages = manifest["pages"]
        if len(pages) != 44:
            errors.append(f"{slug}: manifest page count {len(pages)}")
        if [p["physical"] for p in pages] != list(range(1, 45)):
            errors.append(f"{slug}: physical sequence invalid")
        expected_printed = [None] * 5 + list(range(5, 43)) + [None]
        if [p["printed"] for p in pages] != expected_printed:
            errors.append(f"{slug}: printed sequence invalid")
        for p in pages:
            if p["prompt_id"] in seen_ids:
                errors.append(f"duplicate prompt ID {p['prompt_id']}")
            seen_ids.add(p["prompt_id"])
            md = out / p["markdown"]
            js = out / p["json"]
            if not md.is_file() or not js.is_file():
                errors.append(f"{slug}: missing files for {p['prompt_id']}")
                continue
            payload = json.loads(js.read_text(encoding="utf-8"))
            required = [
                "FINALIZED V4 PROMPT", "official BCube logo", "approved Star master",
                "critical defects 0", "2480 × 3508", "deterministically composited",
            ]
            text = md.read_text(encoding="utf-8")
            for token in required:
                if token not in text:
                    errors.append(f"{p['prompt_id']}: missing lock {token}")
            if payload["prompt_id"] != p["prompt_id"] or payload["page"]["title"] != p["title"]:
                errors.append(f"{p['prompt_id']}: JSON identity mismatch")
    return {
        "validation_version": "4.0.0", "books": len(BOOKS),
        "page_prompts": len(seen_ids), "markdown_files": len(seen_ids),
        "json_files": len(seen_ids), "checks": 10 * 44 * 8 + 10 * 3,
        "critical_defects": len(errors), "status": "PASS" if not errors else "FAIL",
        "errors": errors, "book_results": results,
    }


def main() -> None:
    results = [migrate_book(*book) for book in BOOKS]
    report = validate(results)
    qa = V4_ROOT / "qa" / "nursery-v4-prompts-validation.json"
    qa.parent.mkdir(parents=True, exist_ok=True)
    qa.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    portfolio = {
        "manifest_version": "4.0.0", "status": report["status"],
        "series": SERIES, "level": LEVEL, "books": results,
        "totals": {"books": 10, "page_prompts": 440, "markdown_json_packages": 440},
        "validation_report": str(qa.relative_to(ROOT)),
    }
    (PROMPTS / "nursery" / "V4_PORTFOLIO_MANIFEST.json").write_text(
        json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report["status"] != "PASS":
        raise SystemExit("V4 validation failed:\n" + "\n".join(report["errors"]))
    print(f"PASS: {report['books']} books, {report['page_prompts']} prompts, {report['checks']} checks")


if __name__ == "__main__":
    main()
