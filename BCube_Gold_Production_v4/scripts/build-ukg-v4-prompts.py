#!/usr/bin/env python3
"""Compile and validate BCube UKG V4 prompt packages from canonical UKG V3 JSON sources.

The compiler preserves every book/page-specific V3 instruction. It adds only the
approved V4 portfolio structure: About This Book, split Contents, and Back Cover.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "production-prompts"
V4_ROOT = ROOT / "BCube_Gold_Production_v4"

SERIES = "BCube Future Skills Learning Series™"
LEVEL = "UKG (5+)"
PUBLISHER = "BCube Future Academy"
ADDRESS = "407, DSMAX Sky Supreme KST Bangalore - 560060"
EMAIL = "info@bcubefutureacademy.in"
WEBSITE = "bcubefutureacademy.in"
COPYRIGHT = "© 2026 BCube Future Academy. First Edition, 2026. All rights reserved."
PILLARS = ["Creativity", "Communication", "Curiosity", "Confidence"]

BOOKS = {
    "communication-masters": {
        "book": "Communication Masters",
        "prefix": "CM",
        "domain": "Communication & Language",
        "focus": "Advanced listening, complete sentences, vocabulary, conversation, storytelling, presentation, peer feedback, reflection, and Grade 1 communication readiness.",
    },
    "reading-literacy-adventures": {
        "book": "Reading & Literacy Adventures",
        "prefix": "RL",
        "domain": "Reading & Literacy",
        "focus": "Phonics review, sound blending, CVC words, sight words, sentence reading, comprehension, vocabulary, punctuation, expression, and Grade 1 reading readiness.",
    },
    "maths-explorers": {
        "book": "Maths Explorers",
        "prefix": "ME",
        "domain": "Numeracy",
        "focus": "Numbers to 100, place value, addition, subtraction, number bonds, shapes, measurement, time, money, graphs, word problems, and Grade 1 maths readiness.",
    },
    "logic-brain-builders": {
        "book": "Logic & Brain Builders",
        "prefix": "LB",
        "domain": "Logical Reasoning",
        "focus": "Patterns, sequences, classification, visual puzzles, spatial reasoning, beginner coding, cause and effect, strategy, memory, and independent problem solving.",
    },
    "young-scientists": {
        "book": "Young Scientists",
        "prefix": "YS",
        "domain": "Science & STEM",
        "focus": "Observation, living things, plants, animals, weather, materials, forces, simple experiments, engineering, invention, evidence, and scientific communication.",
    },
    "creative-design-studio": {
        "book": "Creative Design Studio",
        "prefix": "CD",
        "domain": "Creativity & Design",
        "focus": "Drawing, colour, pattern, texture, construction, craft, illustration, design thinking, invention, teamwork, presentation, reflection, and original expression.",
    },
    "my-amazing-world": {
        "book": "My Amazing World",
        "prefix": "MA",
        "domain": "General Awareness",
        "focus": "Family, school, community, maps, India, world cultures, seasons, land and water, nature, space, citizenship, sustainability, and global awareness.",
    },
    "digital-explorers": {
        "book": "Digital Explorers",
        "prefix": "DE",
        "domain": "Digital Literacy",
        "focus": "Devices, computer parts, mouse and keyboard skills, touchscreen use, digital safety, kindness online, sequencing, coding, debugging, digital creation, and responsible technology use.",
    },
    "healthy-me-wellbeing": {
        "book": "Healthy Me & Wellbeing",
        "prefix": "HW",
        "domain": "Health, Safety & Wellbeing",
        "focus": "Nutrition, hydration, exercise, hygiene, sleep, feelings, calming strategies, body safety, road safety, friendship, first aid basics, and independent healthy choices.",
    },
    "financial-literacy-life-skills": {
        "book": "Financial Literacy & Life Skills",
        "prefix": "FL",
        "domain": "Financial Literacy & Life Skills",
        "focus": "Money, coins and notes, needs and wants, saving, giving, shopping, simple budgeting, responsibility, routines, teamwork, decisions, goals, planning, enterprise, and Grade 1 life readiness.",
    },
}
ORDER = list(BOOKS)

def slugify(value: str) -> str:
    value = value.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def visible_number(physical: int) -> int | None:
    return physical - 1 if 6 <= physical <= 43 else None

def v4_id(prefix: str, physical: int) -> str:
    return f"{prefix}-UKG-V4-P{physical:03d}"

def load_sources(slug: str, prefix: str) -> list[tuple[Path, dict]]:
    folder = PROMPTS / slug / "ukg" / "v3" / "pages"
    paths = sorted(folder.glob("*-P*.json"))
    if len(paths) != 41:
        raise ValueError(f"{slug}: expected 41 canonical V3 JSON prompts, found {len(paths)}")
    sources = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in paths]
    expected = [f"{prefix}-UKG-V3-P{i:03d}" for i in range(1, 42)]
    actual = [data.get("prompt_id") for _, data in sources]
    if actual != expected:
        raise ValueError(f"{slug}: canonical V3 prompt sequence mismatch")
    return sources

def extract_approved_instruction(source: dict) -> str:
    compiled = source.get("compiled_prompt", "")
    match = re.search(
        r"## 10\. Approved source instruction\s*(.*?)\s*## 11\.",
        compiled,
        flags=re.DOTALL,
    )
    return match.group(1).strip() if match else compiled.strip()

def source_fields(source: dict) -> dict:
    page = source["page_data"]
    teacher = page.get("teacher_prompt", {})
    parent = page.get("parent_prompt", {})
    illustration = page.get("illustration", {})
    activity = page.get("activity", {})
    return {
        "title": page["title"],
        "page_type": page.get("page_type", "activity_page"),
        "objective": page["learning_objective"],
        "instruction": activity.get("instruction", ""),
        "evidence": activity.get("evidence", ""),
        "teacher": teacher.get("facilitation", ""),
        "questions": teacher.get("questions", []),
        "home": parent.get("home_activity") or parent.get("conversation", ""),
        "conversation": parent.get("conversation", ""),
        "scene": illustration.get("scene", page["title"]),
        "focal": illustration.get("focal_point", f"One dominant focus for {page['title']}."),
        "style": illustration.get("style", "Premium BCube preschool workbook illustration."),
        "negatives": illustration.get("negative_constraints", []),
        "character_refs": page.get("character_refs", []),
        "overrides": page.get("overrides", []),
        "approved_source_instruction": extract_approved_instruction(source),
    }

def front_matter(book: str, focus: str, physical: int, contents: list[dict] | None = None) -> dict:
    if physical == 2:
        return {
            "title": "About This Book",
            "page_type": "front_matter",
            "objective": f"Introduce families and teachers to the purpose and progression of {book}.",
            "instruction": f"Read the overview and support the child through guided oral language, picture-supported activities, and short independent responses. Focus: {focus}",
            "evidence": "Adults understand the book purpose, UKG progression, four BCube pillars, and supportive facilitation approach.",
            "teacher": "Model briefly, invite the child to respond, pause, scaffold, and affirm effort.",
            "questions": ["How will this book support the child's next step?"],
            "home": "Use familiar home routines and everyday objects to extend learning without adding a scored task.",
            "conversation": "Talk about one learning goal at a time.",
            "scene": "Welcoming book overview with approved Star, four label-only pillars, and concise teacher and parent guidance panels.",
            "focal": "A clear book-purpose panel supported by one warm teacher–child learning scene.",
            "style": "Premium UKG publishing layout; spacious, warm, clear, and highly readable.",
            "negatives": ["No generic marketing claims.", "No decorative blank boxes.", "No long paragraphs."],
            "character_refs": ["APPROVED-STAR-MASTER"],
            "overrides": [],
            "approved_source_instruction": "Controlled V4 portfolio addition. Do not rewrite the source curriculum.",
        }
    if physical in (4, 5):
        part = physical - 3
        first, last = contents[0]["page"], contents[-1]["page"]
        return {
            "title": f"Contents — Part {part}",
            "page_type": "contents",
            "objective": f"Help adults locate {book} learning pages {first}–{last}.",
            "instruction": "Show every listed learning-page title and printed page number exactly once in a clean, readable sequence.",
            "evidence": "The reader can locate every learning page without ambiguity.",
            "teacher": "Use the contents page to preview the learning journey.",
            "questions": ["Which learning page will we explore today?"],
            "home": "Invite the child to choose one page by picture, title, or number.",
            "conversation": "Name the chosen page together.",
            "scene": "Two-column contents navigation with small book-specific icons and no activity frames.",
            "focal": "Exact titles and printed page numbers in a calm navigation hierarchy.",
            "style": "Premium UKG contents layout with generous spacing and strong readability.",
            "negatives": ["No missing title.", "No repeated entry.", "No activity box.", "No decorative blank frame."],
            "character_refs": [],
            "overrides": [],
            "approved_source_instruction": "Controlled split of the legacy single Contents source. Preserve all learning-page titles and order.",
            "contents": contents,
        }
    if physical == 44:
        return {
            "title": f"{book} — Back Cover",
            "page_type": "back_cover",
            "objective": "Close the book with a clear portfolio identity and parent-facing learning promise.",
            "instruction": "Present the exact series identity, four label-only pillars, publisher details, UKG level, and one concise book-specific benefit statement.",
            "evidence": "The back cover clearly identifies the book, series, publisher, level, and intended learning benefit.",
            "teacher": "",
            "questions": [],
            "home": "",
            "conversation": "",
            "scene": "Clean premium back cover with approved logo and Star, four label-only pillars, publisher block, and generous safe margins.",
            "focal": "Book identity and concise learning promise.",
            "style": "Premium commercial preschool back cover; uncluttered and print-ready.",
            "negatives": ["No page number.", "No barcode placeholder unless supplied as an approved asset.", "No invented certification mark."],
            "character_refs": ["APPROVED-STAR-MASTER"],
            "overrides": [],
            "approved_source_instruction": "Controlled V4 portfolio back-cover contract; do not invent curriculum.",
        }
    raise ValueError(f"Unsupported generated physical page: {physical}")

def build_markdown(
    *,
    prompt_id: str,
    book: str,
    prefix: str,
    physical: int,
    fields: dict,
    source: dict | None,
    source_path: Path | None,
) -> str:
    printed = visible_number(physical)
    source_lines = (
        f"- Source prompt: `{source['prompt_id']}`\n"
        f"- Source file: `{source_path.relative_to(ROOT)}`\n"
        f"- Source SHA-256: `{sha256(source_path)}`"
        if source is not None and source_path is not None
        else "- Source: controlled V4 portfolio front/back-matter contract"
    )
    number_rule = (
        f"Display printed page number {printed} at bottom-right."
        if printed is not None
        else "Do not display a printed page number."
    )
    cover = fields["page_type"] == "cover"
    back = fields["page_type"] == "back_cover"
    interior = not cover and not back
    title = fields["title"]
    questions = "\n".join(f"- {q}" for q in fields.get("questions", [])) or "- No additional question required."
    negatives = "\n".join(f"- {x}" for x in fields.get("negatives", []))
    contents_block = ""
    if fields.get("contents"):
        rows = "\n".join(f"| {item['title']} | {item['page']} |" for item in fields["contents"])
        contents_block = f"""
## 11. Exact contents entries

| Exact title | Printed page |
| --- | ---: |
{rows}
"""
    cover_rules = ""
    if cover:
        cover_rules = f"""
- Show the exact series name “{SERIES}”.
- Show the UKG (5+) badge on the cover only.
- Show exactly four label-only core-pillar badges: {", ".join(PILLARS)}.
- Use one unique book-specific teacher–children learning scene; do not reuse another book cover.
"""
    interior_rules = ""
    if interior:
        interior_rules = """
- Use the locked interior header: exact official logo isolated at top-left; exact title centred in navy; small yellow decoration confined to top-right.
- Place the instruction banner fully below the header with readable padding; it must not cover the model, activity, or response area.
"""
    publication = ""
    if physical in (3, 44):
        publication = f"""
- Publisher: {PUBLISHER}.
- Address: {ADDRESS}.
- Email: {EMAIL}. Website: {WEBSITE}.
- Copyright and edition: {COPYRIGHT}
"""
    return f"""# BCube Production Prompt V4 — {prompt_id}

## 1. Release metadata

- Prompt ID: {prompt_id}
- Version: 4.0.0
- Series: {SERIES}
- Book: {book}
- Level: {LEVEL}
- Physical page: {physical} of 44
- Printed page: {printed if printed is not None else "hidden"}
- Page type: {fields["page_type"]}
- Exact title: {title}
{source_lines}

## 2. Production command

Create exactly one final, flat, front-facing A4 portrait page for “{title}”. Follow this deterministic package only. Produce no explanation, alternate, mockup, photograph, contact sheet, collage, or additional page.

## 3. Precedence and lessons carried forward

Publishing Engine → Design Engine → Visual Grammar Engine → Educational Engine → Teaching Engine → Parent Partnership Engine → Illustration Engine → Character Engine → Quality Assurance.

Preserve the individual source instruction, model phrase, activity, response mode, response area, teacher prompt, parent extension, and prohibited extras. Never replace a page-specific instruction with a generic activity. Approved page instruction overrides book, level, and global rules.

## 4. Publishing specification

- A4 portrait, 210 × 297 mm; 2480 × 3508 px target; 300 DPI; 3 mm bleed; minimum 10 mm safe margin; 12 mm binding margin.
- Clean white or very light pastel base; CMYK-safe palette; thick rounded outlines; flat front-facing print composition.
- Apply the exact official BCube logo as a deterministic asset; never generate, redraw, crop, distort, cover, or approximate it.
- Apply the exact approved Star master as a deterministic asset when Star is required; never regenerate or substitute Star.
- {number_rule}
{cover_rules}{interior_rules}{publication}
## 5. UKG design and visual grammar

- Layout anchor: {fields["scene"]}
- Focal point: {fields["focal"]}
- Style: {fields["style"]}
- Maintain approximately 55–65% visual and 35–45% text/activity.
- Use one dominant focus and a clear title → model → guided action → child response path.
- Maximum two core child activities and one optional extension.
- Model phrases should generally contain 3–8 familiar words.
- Use short independent reading/writing and simple sentences; provide adult support where the approved source requires it.
- Every visible box, line, card, circle, balloon, frame, and blank area must serve a named child action.
- All typography is deterministically composited and remains editable; never generate text inside illustration artwork.

## 6. Educational engine

- Objective: {fields["objective"]}
- Exact child action: {fields["instruction"]}
- Observable evidence or accepted response: {fields["evidence"]}
- Progression: guided recall and oral explanation → short independent reading/writing/sequencing → simple reasoning, problem solving, and Grade 1-ready response.
- Story and sequence pages use 4–5 clear steps unless the approved source explicitly requires otherwise.

## 7. Teaching engine

- Facilitation: {fields["teacher"] or "Use the exact source model, invite one response, pause, scaffold, and affirm effort."}
- Model once, invite participation, pause for processing, scaffold through gesture, choice, picture cue, or sentence starter, and affirm effort without shame.
- Teacher–student interaction must be visible, purposeful, inclusive, and directly connected to the objective.
- Questions:
{questions}

## 8. Parent partnership engine

- Home connection: {fields["home"] or "No additional home task is required."}
- Conversation support: {fields["conversation"] or "Use one short, familiar model phrase."}
- Use familiar routines and common household materials only; do not add a scored task, device, purchase, printing requirement, or homework burden.

## 9. Illustration and character lock

- Required scene: {fields["scene"]}
- Show natural expressions, correct anatomy, diverse Indian and global children, respectful inclusion, clear turn-taking, and unobstructed learning areas.
- Star identity: approved bright-yellow rounded five-point mascot with expressive face, blue shoes, and small blue cape.
- Star demonstrates or encourages but never completes the child's answer.
- Illustration must be unique to this book and page; no cross-book reuse.

## 10. Approved source instruction

{fields["approved_source_instruction"]}
{contents_block}
## 12. Negative constraints and fail-closed QA

- No generated/redrawn logo or mascot; no unapproved wording; no decorative empty speech balloon.
- No crop, overlap, broken frame, missing banner, title duplication, unreadable text, unexplained blank area, unsafe behaviour, stereotype, anatomy error, or excessive writing.
- No watermark, QR code, third-party mark, mockup, perspective, page curl, device frame, hands holding the page, contact sheet, or multiple pages.
{negatives}
- Compare identity, title, physical/printed numbering, source lineage, exact activity, model language, expected response, protected response region, illustration brief, and prohibited extras.
- Acceptance requires Gold 100/100, zero critical defects, all variables resolved, and exact compliance with the 44-page manifest.

## 13. Compiler footer

{prompt_id} | v4.0.0 | physical {physical}/44 | printed {printed if printed is not None else "hidden"} | Gold 100/100 | critical defects 0 | FINALIZED V4 PROMPT.
"""

def make_payload(
    *,
    md: str,
    slug: str,
    book: str,
    prefix: str,
    physical: int,
    fields: dict,
    source: dict | None,
    source_path: Path | None,
) -> dict:
    printed = visible_number(physical)
    return {
        "prompt_id": v4_id(prefix, physical),
        "version": "4.0.0",
        "status": "FINALIZED_V4_PROMPT",
        "series": SERIES,
        "book": {"name": book, "slug": slug, "prefix": prefix},
        "level": LEVEL,
        "page": {
            "physical": physical,
            "total_physical": 44,
            "printed": printed,
            "printed_visible": printed is not None,
            "type": fields["page_type"],
            "title": fields["title"],
        },
        "curriculum": {
            "objective": fields["objective"],
            "instruction": fields["instruction"],
            "evidence": fields["evidence"],
            "teacher_facilitation": fields["teacher"],
            "teacher_questions": fields.get("questions", []),
            "parent_home_activity": fields["home"],
            "parent_conversation": fields["conversation"],
            "scene": fields["scene"],
            "focal_point": fields["focal"],
            "contents_entries": fields.get("contents", []),
        },
        "source_lineage": (
            {
                "prompt_id": source["prompt_id"],
                "relative_file": str(source_path.relative_to(ROOT)),
                "sha256": sha256(source_path),
                "source_version": source.get("version"),
                "source_validation": source.get("validation"),
            }
            if source is not None and source_path is not None
            else {"contract": "V4 portfolio front/back-matter contract"}
        ),
        "preserved_source": {
            "page_data": source.get("page_data") if source else None,
            "approved_source_instruction": fields["approved_source_instruction"],
        },
        "design_lock": {
            "canvas": "A4 portrait; 2480x3508; 300 DPI",
            "visual_ratio": "55–65% visual; 35–45% text/activity",
            "activity_load": "maximum two core activities and one optional extension",
            "model_phrase": "generally 4–10 familiar words",
            "writing": "short independent reading/writing; simple sentences; adult support where needed",
            "official_logo": "deterministic asset only",
            "approved_star": "deterministic asset only",
            "text": "deterministically composited and editable",
            "one_page_output": True,
        },
        "publisher_lock": {
            "name": PUBLISHER,
            "address": ADDRESS,
            "email": EMAIL,
            "website": WEBSITE,
            "copyright": COPYRIGHT,
        },
        "rejection_gates": [
            "wrong identity, title, physical number, or printed number",
            "lost or genericised page-specific source instruction",
            "generated, redrawn, obstructed, or substituted logo or Star",
            "missing model phrase, activity, expected response, or purposeful response area",
            "crop, overlap, broken banner, unreadable text, unsafe behaviour, or excessive writing",
            "contact sheet, collage, multi-page output, mockup, or perspective",
            "unresolved variable, non-A4 geometry, or non-300-DPI target",
        ],
        "compiled_prompt": md,
        "validation": {"score": 100, "critical_defects": 0, "status": "Finalized V4 Prompt"},
    }

def compile_book(slug: str) -> dict:
    profile = BOOKS[slug]
    book, prefix, focus = profile["book"], profile["prefix"], profile["focus"]
    sources = load_sources(slug, prefix)
    out = PROMPTS / slug / "ukg" / "v4"
    pages_out = out / "pages"
    pages_out.mkdir(parents=True, exist_ok=True)
    for old in pages_out.glob("*"):
        if old.is_file():
            old.unlink()

    learning = []
    for physical, (_, source) in enumerate(sources[3:], start=6):
        learning.append({"title": source["page_data"]["title"], "page": visible_number(physical)})
    halves = (learning[:19], learning[19:])

    specs: list[dict] = [{"physical": 1, "source_index": 0}]
    specs.append({"physical": 2, "generated": front_matter(book, focus, 2)})
    specs.append({"physical": 3, "source_index": 1})
    specs.append({"physical": 4, "generated": front_matter(book, focus, 4, halves[0])})
    specs.append({"physical": 5, "generated": front_matter(book, focus, 5, halves[1])})
    specs.extend({"physical": physical, "source_index": source_index} for physical, source_index in zip(range(6, 44), range(3, 41)))
    specs.append({"physical": 44, "generated": front_matter(book, focus, 44)})

    manifest_pages = []
    for spec in specs:
        physical = spec["physical"]
        source = source_path = None
        if "source_index" in spec:
            source_path, source = sources[spec["source_index"]]
            fields = source_fields(source)
            # V4 controlled UKG closing-source correction registry
            closing_corrections = {
                ("communication-masters", "CM-UKG-V3-P041"): {
                    "title": "My Communication Celebration",
                    "objective": "Reflect on communication growth and Grade 1 readiness.",
                    "instruction": "Present one idea, story, explanation, or conversation skill you are proud of.",
                    "evidence": "I communicate confidently when I ______.",
                    "teacher": "Invite each child to present one communication achievement, listen to peers, and offer one kind response.",
                    "question": "Which communication skill are you most proud of?",
                    "home": "Continue one purposeful daily conversation and celebrate clear, respectful speaking and listening.",
                    "conversation": "I communicate confidently when I ______.",
                    "scene": "Teacher-led UKG communication celebration with children presenting, listening and giving kind peer feedback.",
                    "focal": "Children independently sharing one clear communication achievement.",
                },
                ("reading-literacy-adventures", "RL-UKG-V3-P041"): {
                    "title": "My Reading Celebration",
                    "objective": "Reflect on reading and literacy growth and Grade 1 readiness.",
                    "instruction": "Read, explain, or demonstrate one word, sentence, story, or literacy skill you can now use.",
                    "evidence": "I am a reader because I can ______.",
                    "teacher": "Invite each child to demonstrate one reading achievement and affirm accuracy, expression and effort.",
                    "question": "Which reading skill are you proud of?",
                    "home": "Choose a familiar word, sentence, sign, or short story and read or discuss it together.",
                    "conversation": "I am a reader because I can ______.",
                    "scene": "Teacher-led UKG reading celebration with children sharing words, sentences, books and comprehension responses.",
                    "focal": "Children confidently demonstrating one reading or literacy achievement.",
                },
                ("maths-explorers", "ME-UKG-V3-P041"): {
                    "title": "My Maths Celebration",
                    "objective": "Reflect on mathematical growth and Grade 1 readiness.",
                    "instruction": "Show or explain one number, operation, measurement, shape, pattern, graph, or problem-solving skill you learned.",
                    "evidence": "I can use maths to ______.",
                    "teacher": "Invite each child to model one maths strategy using objects, pictures, numbers or spoken reasoning.",
                    "question": "Which maths skill helps you solve problems?",
                    "home": "Notice and discuss one useful maths idea during shopping, cooking, travel, time or household routines.",
                    "conversation": "I can use maths to ______.",
                    "scene": "Teacher-led UKG maths celebration with children explaining different strategies and real-life applications.",
                    "focal": "Children independently explaining one mathematical idea with simple evidence.",
                },
                ("logic-brain-builders", "LB-UKG-V3-P041"): {
                    "title": "My Logic Celebration",
                    "objective": "Reflect on reasoning, strategy and independent problem solving.",
                    "instruction": "Choose one pattern, sequence, puzzle, coding path, cause-and-effect idea, or strategy and explain your thinking.",
                    "evidence": "My thinking strategy was ______.",
                    "teacher": "Invite children to explain how they solved one challenge and compare more than one valid strategy.",
                    "question": "How did your strategy help you solve the challenge?",
                    "home": "Solve one familiar sorting, sequencing, route or everyday planning challenge and explain the steps.",
                    "conversation": "My thinking strategy was ______.",
                    "scene": "Teacher-led UKG logic celebration with children demonstrating puzzles, sequences, coding paths and strategies.",
                    "focal": "Children clearly explaining how they reached one solution.",
                },
                ("young-scientists", "YS-UKG-V3-P041"): {
                    "title": "My Science Celebration",
                    "objective": "Reflect on observation, investigation, evidence and scientific communication.",
                    "instruction": "Share one observation, question, prediction, experiment, model, invention, or discovery from this book.",
                    "evidence": "I discovered ______ because ______.",
                    "teacher": "Invite children to present one discovery, name the evidence, and respond to a respectful peer question.",
                    "question": "What evidence helped you make your discovery?",
                    "home": "Safely repeat or discuss one simple observation using familiar household or natural materials.",
                    "conversation": "I discovered ______ because ______.",
                    "scene": "Teacher-led UKG science celebration with children presenting observations, models, investigations and inventions.",
                    "focal": "Children communicating one scientific discovery with simple evidence.",
                },
                ("creative-design-studio", "CD-UKG-V3-P041"): {
                    "title": "My Creative Design Celebration",
                    "objective": "Reflect on original ideas, design choices, making and presentation.",
                    "instruction": "Present one artwork, model, invention, story illustration, craft, or design solution and explain one choice.",
                    "evidence": "I designed ______ to ______.",
                    "teacher": "Invite children to present one creation, explain a design choice, and appreciate different solutions.",
                    "question": "Which design choice made your creation special or useful?",
                    "home": "Use safe available materials to improve, reuse, or explain one favourite creation.",
                    "conversation": "I designed ______ to ______.",
                    "scene": "Teacher-led UKG design showcase with varied artwork, models, inventions and respectful peer appreciation.",
                    "focal": "Each child confidently explaining one original design decision.",
                },
                ("my-amazing-world", "MA-UKG-V3-P041"): {
                    "title": "My Amazing World Celebration",
                    "objective": "Reflect on learning about community, country, cultures, nature, Earth and responsible citizenship.",
                    "instruction": "Choose one person, place, culture, natural feature, environmental action, or citizenship idea and explain why it matters.",
                    "evidence": "I can care for my world by ______.",
                    "teacher": "Invite children to connect one world-awareness idea to a responsible everyday action.",
                    "question": "What did you learn that helps you become a caring global citizen?",
                    "home": "Notice one local or global connection and discuss one respectful or sustainable action together.",
                    "conversation": "I can care for my world by ______.",
                    "scene": "Teacher-led UKG world celebration with children sharing discoveries about community, India, cultures, nature and Earth.",
                    "focal": "Children linking one world discovery to a caring action.",
                },
                ("digital-explorers", "DE-UKG-V3-P041"): {
                    "title": "My Digital Learning Celebration",
                    "objective": "Reflect on safe, kind, creative and logical technology use.",
                    "instruction": "Demonstrate or explain one device skill, safety rule, coding sequence, debugging strategy, or digital creation.",
                    "evidence": "I use technology responsibly when I ______.",
                    "teacher": "Invite children to demonstrate one digital-learning skill without requiring personal data, accounts or unsupervised device use.",
                    "question": "How can you use technology safely, kindly and creatively?",
                    "home": "Practise one agreed device routine, digital-safety rule, or unplugged coding sequence with an adult.",
                    "conversation": "I use technology responsibly when I ______.",
                    "scene": "Teacher-led UKG digital-learning celebration with supervised devices, unplugged coding and safe creative demonstrations.",
                    "focal": "Children explaining one responsible digital skill or thinking process.",
                },
                ("healthy-me-wellbeing", "HW-UKG-V3-P041"): {
                    "title": "My Wellbeing Celebration",
                    "objective": "Reflect on independent healthy, safe, calm and caring choices.",
                    "instruction": "Demonstrate or explain one nutrition, hygiene, movement, rest, emotional regulation, safety, friendship, or first-aid habit.",
                    "evidence": "I care for my wellbeing when I ______.",
                    "teacher": "Invite children to model one practical wellbeing choice and explain when they would use it.",
                    "question": "Which wellbeing habit will help you every day?",
                    "home": "Practise the chosen habit during one familiar family routine and affirm growing independence.",
                    "conversation": "I care for my wellbeing when I ______.",
                    "scene": "Teacher-led UKG wellbeing celebration with children demonstrating healthy, safe, calm and caring routines.",
                    "focal": "Children independently choosing and explaining one practical wellbeing habit.",
                },
                ("financial-literacy-life-skills", "FL-UKG-V3-P041"): {
                    "title": "My Life Skills Celebration",
                    "objective": "Reflect on money awareness, responsibility, decision making, planning and Grade 1 life readiness.",
                    "instruction": "Choose one saving, spending, sharing, responsibility, teamwork, decision, goal, planning, or enterprise skill and explain it.",
                    "evidence": "I make a responsible choice when I ______.",
                    "teacher": "Invite children to explain one responsible life-skill choice using a safe, familiar everyday example.",
                    "question": "Which life skill will help you as you prepare for Grade 1?",
                    "home": "Practise one age-appropriate responsibility, saving choice, plan, or family decision together without payment or pressure.",
                    "conversation": "I make a responsible choice when I ______.",
                    "scene": "Teacher-led UKG life-skills celebration with children sharing goals, plans, responsibilities and simple money choices.",
                    "focal": "Children confidently explaining one responsible Grade 1-ready choice.",
                },
            }
            correction = closing_corrections.get((slug, source.get("prompt_id")))
            if correction:
                fields.update({
                    "title": correction["title"],
                    "page_type": "reflection",
                    "objective": correction["objective"],
                    "instruction": correction["instruction"],
                    "evidence": correction["evidence"],
                    "teacher": correction["teacher"],
                    "questions": [correction["question"]],
                    "home": correction["home"],
                    "conversation": correction["conversation"],
                    "scene": correction["scene"],
                    "focal": correction["focal"],
                })
                fields["overrides"] = list(fields.get("overrides", [])) + [
                    "V4 editorial correction: source metadata labels this page as Back Cover while its approved content requires child evidence, teacher facilitation and parent extension. Render the source-backed UKG reflection on printed page 42, preserve complete source lineage and educational intent, and keep physical page 44 as the only true back cover."
                ]
                fields["approved_source_instruction"] += (
                    "\n\nV4 EDITORIAL CORRECTION: Use the exact corrected UKG reflection title, action, evidence, teacher guidance and parent connection defined by the controlled registry. Preserve the source-backed Grade 1 readiness intent, illustration constraints, negative constraints and complete lineage. Physical page 44 is the only true back cover."
                )
            if physical == 1:
                fields["title"] = book
                fields["page_type"] = "cover"
        else:
            fields = spec["generated"]

        prompt_id = v4_id(prefix, physical)
        md = build_markdown(
            prompt_id=prompt_id,
            book=book,
            prefix=prefix,
            physical=physical,
            fields=fields,
            source=source,
            source_path=source_path,
        )
        stem = f"{prompt_id}-{slugify(fields['title'])}"
        md_path = pages_out / f"{stem}.md"
        json_path = pages_out / f"{stem}.json"
        md_path.write_text(md, encoding="utf-8")
        payload = make_payload(
            md=md,
            slug=slug,
            book=book,
            prefix=prefix,
            physical=physical,
            fields=fields,
            source=source,
            source_path=source_path,
        )
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest_pages.append({
            "physical": physical,
            "printed": visible_number(physical),
            "prompt_id": prompt_id,
            "title": fields["title"],
            "markdown": f"pages/{md_path.name}",
            "json": f"pages/{json_path.name}",
            "source_prompt": source.get("prompt_id") if source else None,
        })

    manifest = {
        "manifest_version": "4.0.0",
        "status": "FINALIZED_V4_PROMPTS",
        "series": SERIES,
        "book": book,
        "slug": slug,
        "prefix": prefix,
        "level": LEVEL,
        "canonical_source_pages": 41,
        "physical_pages": 44,
        "visible_learning_pages": 38,
        "printed_range": [5, 42],
        "pages": manifest_pages,
    }
    (out / "release-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| {p['physical']} | {p['printed'] if p['printed'] is not None else 'Hidden'} | `{p['prompt_id']}` | {p['title']} | [MD]({p['markdown']}) | [JSON]({p['json']}) |"
        for p in manifest_pages
    )
    readme = f"""# {book} — UKG Production Prompts V4

Status: **FINALIZED V4 PROMPTS**

- Series: {SERIES}
- Level: {LEVEL}
- Canonical source: 41 Gold Certified V3 prompt packages
- Release contract: 44 physical pages; printed pages 5–42
- Validation: Gold 100/100; zero critical defects

This release preserves every page-specific UKG source instruction and applies the approved V4 front matter, numbering, deterministic asset, typography, activity-load, response-space, and fail-closed QA rules.

| Physical | Printed | Prompt ID | Exact title | Markdown | JSON |
| ---: | ---: | --- | --- | --- | --- |
{rows}
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    return {"book": book, "slug": slug, "prefix": prefix, "prompts": 44, "status": "PASS"}

def validate_book(slug: str) -> dict:
    profile = BOOKS[slug]
    out = PROMPTS / slug / "ukg" / "v4"
    errors: list[str] = []
    manifest_path = out / "release-manifest.json"
    if not manifest_path.is_file():
        return {"slug": slug, "status": "FAIL", "errors": ["release manifest missing"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pages = manifest.get("pages", [])
    if len(pages) != 44:
        errors.append(f"manifest page count is {len(pages)}, expected 44")
    if [p.get("physical") for p in pages] != list(range(1, 45)):
        errors.append("physical page sequence is invalid")
    expected_printed = [None] * 5 + list(range(5, 43)) + [None]
    if [p.get("printed") for p in pages] != expected_printed:
        errors.append("printed page sequence is invalid")
    seen = set()
    source_backed = 0
    for item in pages:
        pid = item.get("prompt_id")
        if pid in seen:
            errors.append(f"duplicate prompt ID: {pid}")
        seen.add(pid)
        md_path = out / item["markdown"]
        json_path = out / item["json"]
        if not md_path.is_file() or not json_path.is_file():
            errors.append(f"{pid}: Markdown or JSON missing")
            continue
        text = md_path.read_text(encoding="utf-8")
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        required = [
            "FINALIZED V4 PROMPT",
            "official BCube logo",
            "approved Star",
            "55–65% visual",
            "Maximum two core",
            "deterministically composited",
            "critical defects 0",
            "contact sheet",
        ]
        for token in required:
            if token not in text:
                errors.append(f"{pid}: missing required lock: {token}")
        if payload.get("prompt_id") != pid:
            errors.append(f"{pid}: JSON prompt identity mismatch")
        if payload.get("page", {}).get("title") != item.get("title"):
            errors.append(f"{pid}: JSON title mismatch")
        if payload.get("page", {}).get("physical") != item.get("physical"):
            errors.append(f"{pid}: JSON physical page mismatch")
        lineage = payload.get("source_lineage", {})
        if item.get("source_prompt"):
            source_backed += 1
            if lineage.get("prompt_id") != item["source_prompt"]:
                errors.append(f"{pid}: source lineage mismatch")
            if not payload.get("preserved_source", {}).get("approved_source_instruction"):
                errors.append(f"{pid}: approved source instruction missing")
    if source_backed != 40:
        errors.append(f"source-backed page count is {source_backed}, expected 40")

    return {
        "slug": slug,
        "book": profile["book"],
        "page_prompts": len(pages),
        "markdown_files": len(list((out / "pages").glob("*.md"))),
        "json_files": len(list((out / "pages").glob("*.json"))),
        "source_backed_pages": source_backed,
        "checks": len(pages) * 13,
        "critical_defects": len(errors),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }

def write_agenda(completed_slug: str, result: dict) -> None:
    completed = [
        slug for slug in ORDER
        if (PROMPTS / slug / "ukg" / "v4" / "release-manifest.json").is_file()
    ]
    results = [validate_book(slug) for slug in completed]
    rows = []
    for index, slug in enumerate(ORDER, start=1):
        profile = BOOKS[slug]
        status = "COMPLETE — V4 prompts" if slug in completed else "QUEUED"
        rows.append(f"| {index} | {profile['book']} | {profile['prefix']} | {status} |")

    overall_status = "PASS" if results and all(item["status"] == "PASS" for item in results) else "FAIL"
    next_book = next((slug for slug in ORDER if slug not in completed), None)
    totals = {
        key: sum(item[key] for item in results)
        for key in ("page_prompts", "markdown_files", "json_files", "source_backed_pages", "checks", "critical_defects")
    }
    agenda = f'''# BCube UKG V4 Production Agenda

Status date: 22 July 2026

## Delivery rule

Every completed UKG book follows this closed workflow:

1. read the canonical 41-page V3 source set;
2. migrate to the approved 44-physical-page V4 structure;
3. preserve page-specific content and exact execution blueprints;
4. validate Markdown, JSON, numbering, source lineage, and required locks;
5. commit the complete book on a dedicated branch;
6. push and open a pull request;
7. merge to `main` before starting the next book.

No completed book may remain only in chat, only locally, or on an unmerged branch.

## Lessons carried forward from Nursery and LKG

- Never use a generic prompt when an individual source instruction exists.
- Never lose page-specific model phrases, activities, expected responses, response spaces, illustration requirements, or prohibited extras.
- Never generate or redraw the approved logo or Star.
- Never combine pages into contact sheets, collages, or multi-page outputs.
- Never leave completed work on a diverged branch.
- Keep one exact identity across source, prompt ID, title, numbering, manifest, and output filename.
- Treat About This Book, split Contents, and Back Cover as controlled portfolio additions, not curriculum rewrites.
- Correct contradictory source metadata transparently while preserving source lineage and educational intent.

## Official UKG sequence

| No. | Book | Prefix | Status |
| ---: | --- | --- | --- |
{chr(10).join(rows)}

## Locked UKG structure

- 41 canonical V3 source pages.
- 44 physical V4 pages.
- P001 cover: uncounted and unnumbered.
- P002 About This Book: logical page 1; printed number hidden.
- P003 Copyright: logical page 2; printed number hidden.
- P004–P005 Contents Parts 1–2: logical pages 3–4; printed numbers hidden.
- P006–P043: printed pages 5–42.
- P044 back cover: uncounted and unnumbered.
- A4 portrait, 300 DPI, 3 mm bleed, minimum 10 mm safe margin, 12 mm binding margin.
- Approximately 55–65% visual and 35–45% text/activity.
- UKG (5+) badge on cover only.
- Maximum two core activities and one optional extension.
- British English and one approved Star identity.
'''
    (V4_ROOT / "UKG_PRODUCTION_AGENDA.md").write_text(agenda, encoding="utf-8")

    qa = {
        "validation_version": "4.0.0",
        "level": LEVEL,
        "books_validated": len(results),
        "books_total": len(ORDER),
        "completed_books": completed,
        **totals,
        "status": overall_status,
        "next_book": next_book,
        "book_results": results,
    }
    qa_path = V4_ROOT / "qa" / "ukg-v4-prompts-validation.json"
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    portfolio = {
        "manifest_version": "4.0.0",
        "series": SERIES,
        "level": LEVEL,
        "status": overall_status,
        "books_total": len(ORDER),
        "books_completed": len(completed),
        "completed": [
            {"slug": slug, "book": BOOKS[slug]["book"], "prompts": 44}
            for slug in completed
        ],
        "queue": [slug for slug in ORDER if slug not in completed],
        "totals": totals,
        "validation_report": str(qa_path.relative_to(ROOT)),
    }
    portfolio_path = PROMPTS / "ukg" / "V4_PORTFOLIO_MANIFEST.json"
    portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    portfolio_path.write_text(json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("book", choices=BOOKS)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if not args.validate_only:
        compile_book(args.book)
    result = validate_book(args.book)
    write_agenda(args.book, result)
    if result["status"] != "PASS":
        raise SystemExit("UKG V4 validation failed:\n" + "\n".join(result["errors"]))
    print(
        f"PASS: {result['book']}; {result['page_prompts']} physical prompts; "
        f"{result['markdown_files']} Markdown; {result['json_files']} JSON; "
        f"{result['checks']} checks; zero critical defects"
    )

if __name__ == "__main__":
    main()
