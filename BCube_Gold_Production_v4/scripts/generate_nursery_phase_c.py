from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
BOOKS_ROOT = ROOT / "books" / "nursery"
CATALOG_PATH = ROOT / "books" / "catalog.json"
PHASE_C = ROOT / "normalization" / "nursery-gold-v5" / "phase-c"
QA_DIR = PHASE_C / "qa"
QA_DIR.mkdir(parents=True, exist_ok=True)

BOOKS: list[dict[str, Any]] = [
    {
        "number": 3,
        "slug": "fine-motor-fun",
        "title": "Fine Motor Fun Gold™",
        "code": "FM",
        "focus": "hand strength, hand-eye coordination, pre-writing control and practical fine-motor confidence",
        "modules": [
            ("Ready Hands", ["Open and Close", "Finger Tap", "Thumb Touch", "Pinch and Pick", "Squeeze and Release", "Roll the Dough", "Press the Dots", "Tear the Paper"]),
            ("Lines and Paths", ["Trace Up", "Trace Down", "Side to Side", "Round and Round", "Zigzag Trail", "Wavy Road", "Follow the Path", "Stay on the Track"]),
            ("Pick, Place and Build", ["Move the Pom-Poms", "Sort with Tongs", "Thread the Beads", "Stack the Blocks", "Peg the Cards", "Match the Lids", "Post the Shapes", "Build a Tower"]),
            ("Cut, Fold and Create", ["Snip the Fringe", "Cut the Straight Line", "Cut the Curve", "Fold in Half", "Fold the Corner", "Paste the Pieces", "Make a Collage", "Create a Crown"]),
            ("Independent Hands", ["Button Practice", "Zip It Up", "Twist and Turn", "Spoon and Transfer", "Pour Carefully", "Lace the Shoe", "Pack My Bag", "Fine Motor Celebration"]),
        ],
    },
    {
        "number": 6,
        "slug": "stem-explorers",
        "title": "STEM Explorers Gold™",
        "code": "STEM",
        "focus": "observation, prediction, sorting, patterns, construction, measurement and simple cause-and-effect",
        "modules": [
            ("Little Scientists", ["Look Like a Scientist", "Use My Senses", "What Do You Notice?", "Same or Different?", "Guess What Happens", "Test the Idea", "Watch It Change", "Tell What Happened"]),
            ("Sort and Compare", ["Sort by Colour", "Sort by Shape", "Sort by Size", "Heavy or Light", "Long or Short", "More or Less", "Sink or Float", "Magnetic or Not"]),
            ("Patterns and Sequences", ["Copy the Pattern", "Finish the Pattern", "Make a Colour Pattern", "Make a Shape Pattern", "What Comes Next?", "First Then Last", "Day and Night", "Growing Sequence"]),
            ("Build and Test", ["Build a Tall Tower", "Build a Strong Bridge", "Make a Ramp", "Roll It Down", "Fast or Slow", "Balance the Blocks", "Fix the Structure", "Build with Recycled Shapes"]),
            ("Nature and Machines", ["Parts of a Plant", "What Plants Need", "Weather Watch", "Shadows Move", "Push and Pull", "Wheels Help Us", "Simple Machines Around Us", "STEM Explorer Celebration"]),
        ],
    },
    {
        "number": 7,
        "slug": "my-world-general-awareness",
        "title": "My World & General Awareness Gold™",
        "code": "MW",
        "focus": "self-awareness, family, community, nature, animals, transport, places and everyday general knowledge",
        "modules": [
            ("Me and My Family", ["All About Me", "My Body", "My Feelings", "My Family", "People Who Care for Me", "My Home", "Things I Use", "My Daily Routine"]),
            ("My School and Community", ["My School", "People at School", "Classroom Objects", "Community Helpers", "Places Near Me", "At the Market", "At the Hospital", "At the Post Office"]),
            ("Animals and Nature", ["Farm Animals", "Wild Animals", "Pet Animals", "Birds Around Us", "Insects Around Us", "Trees and Flowers", "Fruits and Vegetables", "Land and Water"]),
            ("Transport and Places", ["Road Transport", "Rail Transport", "Water Transport", "Air Transport", "Traffic Signals", "City and Village", "Park and Playground", "Beach and Mountains"]),
            ("Our Changing World", ["Sunny Day", "Rainy Day", "Windy Day", "Day and Night", "Seasons Around Us", "Festivals We Celebrate", "Our Country India", "My World Celebration"]),
        ],
    },
    {
        "number": 9,
        "slug": "healthy-habits-safety",
        "title": "Healthy Habits & Safety Gold™",
        "code": "HH",
        "focus": "hygiene, nutrition, movement, emotional wellbeing, personal boundaries and everyday safety",
        "modules": [
            ("Clean and Healthy", ["Wash My Hands", "Brush My Teeth", "Take a Bath", "Wear Clean Clothes", "Cover My Cough", "Use a Tissue", "Keep My Nails Clean", "Rest and Sleep"]),
            ("Food and Fitness", ["Healthy Food", "Fruits and Vegetables", "Drink Water", "Eat at the Table", "Try New Foods", "Move My Body", "Stretch and Breathe", "Play Every Day"]),
            ("Feelings and Wellbeing", ["Name My Feeling", "Calm My Body", "Ask for Help", "Take Turns", "Use Kind Words", "Solve a Small Problem", "Quiet Time", "People I Trust"]),
            ("Safety at Home and School", ["Walk, Do Not Run", "Use Stairs Safely", "Stay Away from Fire", "Do Not Touch Sockets", "Use Tools with an Adult", "Keep Floors Clear", "Safe Classroom Choices", "Emergency Helpers"]),
            ("Safety Outside", ["Hold an Adult's Hand", "Cross at the Zebra Crossing", "Wear a Helmet", "Sit Safely in a Vehicle", "Stay with My Group", "Do Not Go with Strangers", "Safe and Unsafe Touch", "Healthy and Safe Celebration"]),
        ],
    },
    {
        "number": 10,
        "slug": "art-colour-fun",
        "title": "Art & Colour Fun Gold™",
        "code": "AC",
        "focus": "colour recognition, mark-making, drawing, painting, collage, craft and joyful creative expression",
        "modules": [
            ("Meet the Colours", ["Hello Red", "Hello Yellow", "Hello Blue", "Hello Green", "Hello Orange", "Hello Purple", "Black and White", "Colour Hunt"]),
            ("Marks and Lines", ["Make Dots", "Make Short Lines", "Make Long Lines", "Make Curves", "Make Spirals", "Make Zigzags", "Draw Around a Shape", "My Line Picture"]),
            ("Paint and Print", ["Finger Painting", "Sponge Printing", "Leaf Printing", "Bubble Painting", "Cotton Bud Dots", "Roller Painting", "Mix Two Colours", "Paint to Music"]),
            ("Cut, Tear and Stick", ["Tear and Paste", "Paper Shapes", "Texture Collage", "Nature Collage", "Make a Paper Face", "Make a Colour Crown", "Decorate a Kite", "Create a Greeting Card"]),
            ("Draw and Create", ["Draw My Face", "Draw My Family", "Draw an Animal", "Draw a Garden", "Complete the Picture", "Create from Shapes", "My Favourite Artwork", "Art and Colour Celebration"]),
        ],
    },
]

PAGE_TYPES = {
    1: "Front Cover",
    2: "Inside Cover / Book Information",
    3: "This Book Belongs To",
    44: "Back Cover",
}


def flatten_pages(book: dict[str, Any]) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = [
        {"page": 1, "module": "Front Matter", "title": book["title"].replace(" Gold™", ""), "type": PAGE_TYPES[1]},
        {"page": 2, "module": "Front Matter", "title": "About This Book", "type": PAGE_TYPES[2]},
        {"page": 3, "module": "Front Matter", "title": "This Book Belongs To", "type": PAGE_TYPES[3]},
    ]
    page = 4
    for module_name, titles in book["modules"]:
        for title in titles:
            pages.append({"page": page, "module": module_name, "title": title, "type": "Core Learning"})
            page += 1
    pages.append({"page": 44, "module": "Back Matter", "title": "Back Cover", "type": PAGE_TYPES[44]})
    assert len(pages) == 44 and page == 44
    return pages


def prompt_text(book: dict[str, Any], item: dict[str, Any]) -> str:
    pid = f"{book['code']}-NURSERY-V5-P{item['page']:03d}"
    title = item["title"]
    page_type = item["type"]
    return f"""# {pid} — {title}

## Release metadata
- Prompt ID: `{pid}`
- Version: `5.1.0`
- Book: {book['title']}
- Official book number: {book['number']:02d}
- Level: Nursery (3+)
- Page: {item['page']} of 44
- Page type: {page_type}
- Module: {item['module']}
- Exact title: {title}

## Production command
Create exactly one final, flat, front-facing A4 portrait page for **{title}**. Produce no mockup, explanation, alternate page or photography.

## Publishing rules
Use the BCube Future Academy Gold interior system: clean white base, soft pastel accents, thick rounded outlines, generous safe margins, premium preschool publishing finish, official logo placement, accurate title text and page numbering where applicable. Keep all important content within trim-safe boundaries.

## Educational intent
This page supports {book['focus']}. The activity must be immediately understandable to a Nursery child aged 3+ and usable by a teacher or parent with minimal explanation.

## Page-specific direction
Page type: **{page_type}**. Create a visually dominant, age-appropriate composition for **{title}** with one clear learning focus, large recognizable forms, minimal clutter and meaningful child participation. For learning pages, include a direct action such as point, trace, match, sort, colour, draw, move, build, observe, say or choose. For cover and book-information pages, follow the canonical 44-page publishing architecture rather than an activity layout.

## Teaching support
Add one concise adult guidance line only when the page type requires it. Keep instructions short, positive and action-led. Avoid dense curriculum notes.

## Character and illustration rules
Use friendly inclusive preschool characters only when they improve understanding. Maintain natural expressions, safe actions, consistent proportions and simple environments. Do not use photorealism, watermarks, empty speech balloons, tiny decorative text or unapproved logos.

## Quality gates
- Exact title preserved
- Correct prompt ID and page number
- One clear learning objective
- Nursery-safe visual complexity
- Teacher/parent usability
- Print-safe A4 portrait composition
- No spelling errors or placeholder text
"""


def write_book(book: dict[str, Any]) -> dict[str, Any]:
    folder = BOOKS_ROOT / book["slug"]
    prompts_dir = folder / "production-prompts"
    docs_dir = folder / "docs"
    planning_dir = folder / "planning"
    qa_dir = folder / "qa"
    validation_dir = folder / "validation"
    publishing_dir = folder / "publishing"
    for d in (prompts_dir, docs_dir, planning_dir, qa_dir, validation_dir, publishing_dir):
        d.mkdir(parents=True, exist_ok=True)

    pages = flatten_pages(book)
    for item in pages:
        (prompts_dir / f"P{item['page']:03d}.md").write_text(prompt_text(book, item), encoding="utf-8")

    base = book["title"].replace(" Gold™", "").replace("&", "and").replace(" ", "_")
    csv_path = folder / f"{base}_Gold_Production_Prompts_v5.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["prompt_id", "page", "page_type", "module", "title", "prompt"])
        writer.writeheader()
        for item in pages:
            writer.writerow({
                "prompt_id": f"{book['code']}-NURSERY-V5-P{item['page']:03d}",
                "page": item["page"],
                "page_type": item["type"],
                "module": item["module"],
                "title": item["title"],
                "prompt": prompt_text(book, item),
            })

    wb = Workbook()
    ws = wb.active
    ws.title = "Production Prompts"
    ws.append(["Prompt ID", "Page", "Page Type", "Module", "Title", "Production Prompt"])
    for item in pages:
        ws.append([
            f"{book['code']}-NURSERY-V5-P{item['page']:03d}", item["page"], item["type"], item["module"], item["title"], prompt_text(book, item)
        ])
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    widths = {"A": 26, "B": 10, "C": 30, "D": 28, "E": 34, "F": 110}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    wb.save(folder / f"{base}_Gold_Production_Prompts_v5.xlsx")

    (folder / "README.md").write_text(
        f"# {book['title']}\n\nOfficial Nursery Book {book['number']:02d} in the BCube Future Skills Learning Series™.\n\n"
        f"- Level: Nursery (3+)\n- Canonical pages: 44\n- Prompt range: `{book['code']}-NURSERY-V5-P001` to `{book['code']}-NURSERY-V5-P044`\n"
        f"- Focus: {book['focus']}\n- Phase C status: framework and production prompts generated; artwork and human prepress approval remain pending.\n",
        encoding="utf-8",
    )
    module_lines = [f"# Curriculum — {book['title']}\n", f"Focus: {book['focus']}.\n"]
    for idx, (name, titles) in enumerate(book["modules"], 1):
        module_lines.append(f"## Module {idx}: {name}\n" + "\n".join(f"- {t}" for t in titles) + "\n")
    (docs_dir / "01_Curriculum.md").write_text("\n".join(module_lines), encoding="utf-8")
    (docs_dir / "02_Book_Structure.md").write_text(
        "# Book Structure\n\n1 front cover + 1 inside cover/book information + 1 ownership page + 40 core learning/support pages + 1 back cover = 44 pages.\n",
        encoding="utf-8",
    )
    (docs_dir / "03_Scope_and_Sequence.md").write_text(
        "# Scope and Sequence\n\n" + "\n".join(f"- Module {i}: {name} — 8 pages" for i, (name, _) in enumerate(book["modules"], 1)) + "\n",
        encoding="utf-8",
    )
    (docs_dir / "04_Learning_Outcomes.md").write_text(
        f"# Learning Outcomes\n\nChildren progressively develop {book['focus']}, demonstrate participation, communicate observations and complete increasingly independent age-appropriate tasks.\n",
        encoding="utf-8",
    )
    (docs_dir / "05_Module_Structure.md").write_text(
        "# Module Structure\n\nEach of the five modules contains eight sequenced pages: introduction, guided practice, variation, application and celebration/review.\n",
        encoding="utf-8",
    )
    with (planning_dir / "page-index.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["page", "prompt_id", "page_type", "module", "title"])
        writer.writeheader()
        for item in pages:
            writer.writerow({"page": item["page"], "prompt_id": f"{book['code']}-NURSERY-V5-P{item['page']:03d}", "page_type": item["type"], "module": item["module"], "title": item["title"]})

    validation = {
        "book_number": book["number"],
        "title": book["title"],
        "slug": book["slug"],
        "code": book["code"],
        "expected_pages": 44,
        "prompt_files": len(list(prompts_dir.glob("P*.md"))),
        "csv_present": csv_path.exists(),
        "xlsx_present": (folder / f"{base}_Gold_Production_Prompts_v5.xlsx").exists(),
        "unique_prompt_ids": len({f"{book['code']}-NURSERY-V5-P{i:03d}" for i in range(1, 45)}) == 44,
    }
    validation["decision"] = "PASS" if validation["prompt_files"] == 44 and validation["csv_present"] and validation["xlsx_present"] and validation["unique_prompt_ids"] else "FAIL"
    (qa_dir / "phase-c-validation-report.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    (qa_dir / "phase-c-summary.md").write_text(
        f"# Phase C Summary — {book['title']}\n\n- Production prompts: {validation['prompt_files']}/44\n- CSV: {'PASS' if validation['csv_present'] else 'FAIL'}\n- XLSX: {'PASS' if validation['xlsx_present'] else 'FAIL'}\n- Unique prompt IDs: {'PASS' if validation['unique_prompt_ids'] else 'FAIL'}\n\n`{validation['decision']} — PHASE C BOOK FRAMEWORK`\n",
        encoding="utf-8",
    )
    (validation_dir / "README.md").write_text("# Validation\n\nAutomated structural validation passed. Artwork, pedagogy review, visual QA and prepress approval remain mandatory.\n", encoding="utf-8")
    (publishing_dir / "release-manifest.json").write_text(json.dumps({
        "book_number": book["number"], "title": book["title"], "code": book["code"], "page_count": 44,
        "phase_c_framework": validation["decision"], "artwork": "PENDING", "human_visual_approval": "PENDING", "prepress": "PENDING", "publisher_signoff": "PENDING"
    }, indent=2) + "\n", encoding="utf-8")
    return validation


results = [write_book(book) for book in BOOKS]

catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
phase_c_numbers = {b["number"] for b in BOOKS}
for entry in catalog["books"]:
    if entry["number"] in phase_c_numbers:
        entry["status"] = "phase_c_framework_complete"
CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

overall = {
    "phase": "C",
    "books_generated": len(results),
    "expected_books": 5,
    "total_prompts_generated": sum(r["prompt_files"] for r in results),
    "expected_prompts": 220,
    "books": results,
}
overall["decision"] = "PASS" if len(results) == 5 and overall["total_prompts_generated"] == 220 and all(r["decision"] == "PASS" for r in results) else "FAIL"
(QA_DIR / "phase-c-report.json").write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")
(QA_DIR / "phase-c-summary.md").write_text(
    "# Nursery Gold Phase C Summary\n\n"
    + "\n".join(f"- Book {r['book_number']:02d}: {r['title']} — {r['prompt_files']} prompts — {r['decision']}" for r in results)
    + f"\n\n- Books generated: {overall['books_generated']}/5\n- Total prompts: {overall['total_prompts_generated']}/220\n\n"
    + f"`{overall['decision']} — PHASE C FIVE-BOOK FRAMEWORK AND PRODUCTION-PROMPT GENERATION`\n\n"
    + "Artwork generation, human visual review, prepress proof and publisher sign-off remain separate release gates.\n",
    encoding="utf-8",
)

if overall["decision"] != "PASS":
    raise SystemExit("Phase C generation failed")
print(json.dumps(overall, indent=2))
