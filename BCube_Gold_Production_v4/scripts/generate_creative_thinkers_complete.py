from __future__ import annotations

import csv
import json
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books" / "nursery" / "creative-thinkers"
PROMPTS = BOOK / "production-prompts"
DOCS = BOOK / "docs"
PLANNING = BOOK / "planning"
VALIDATION = BOOK / "validation"
QA = BOOK / "qa"
ILLUSTRATION = BOOK / "illustration"
PRODUCTION = BOOK / "production"
PUBLISHING = BOOK / "publishing"
PHASE5 = BOOK / "phase5"
PHASE6 = BOOK / "phase6"

for directory in (BOOK, PROMPTS, DOCS, PLANNING, VALIDATION, QA, ILLUSTRATION, PRODUCTION, PUBLISHING, PHASE5, PHASE6):
    directory.mkdir(parents=True, exist_ok=True)

pages = [
    ("Front Cover", "Welcome", "Meet the creative-thinking journey"),
    ("This Book Belongs to", "Welcome", "Build ownership and confidence"),
    ("Meet Star", "Welcome", "Meet the supportive mascot"),
    ("How to Use This Book", "Welcome", "Understand child, teacher and parent roles"),
    ("Look and Wonder", "Imagine", "Notice details and ask what could happen"),
    ("What Could It Be?", "Imagine", "Interpret an open shape in different ways"),
    ("Cloud Pictures", "Imagine", "Imagine familiar forms in clouds"),
    ("Finish the Doodle", "Imagine", "Transform a simple mark into an idea"),
    ("A New Animal", "Imagine", "Combine familiar animal features"),
    ("Funny Faces", "Imagine", "Explore expressive facial combinations"),
    ("My Magic Box", "Imagine", "Imagine what a special box may contain"),
    ("Shape Builder", "Create", "Build a picture from simple shapes"),
    ("Make a Pattern", "Create", "Create a repeating visual sequence"),
    ("Complete the Picture", "Create", "Add meaningful missing parts"),
    ("Build a Robot", "Create", "Assemble a friendly robot from parts"),
    ("Design a Kite", "Create", "Choose shapes and marks for a kite"),
    ("My Little House", "Create", "Design a simple home scene"),
    ("Create a Garden", "Create", "Arrange plants and garden objects"),
    ("Try Another Way", "Explore", "Find more than one possible response"),
    ("Mix and Match", "Explore", "Combine parts into new outcomes"),
    ("Change the Shape", "Explore", "Transform one shape into another idea"),
    ("What Comes Next?", "Explore", "Extend an open-ended visual sequence"),
    ("Move the Pieces", "Explore", "Rearrange parts to make a new design"),
    ("Big, Small, Different", "Explore", "Vary size and placement creatively"),
    ("Choose Your Tools", "Explore", "Select suitable creative materials"),
    ("Tell a Picture Story", "Express", "Create a simple visual narrative"),
    ("Star Has an Idea", "Express", "Explain an imagined solution"),
    ("My Happy Place", "Express", "Represent a personally meaningful place"),
    ("A Gift for Someone", "Express", "Design with another person in mind"),
    ("Show How You Feel", "Express", "Express emotion through marks and colour"),
    ("My Favourite Thing", "Express", "Communicate a personal preference"),
    ("Invent a Toy", "Invent", "Design a new play object"),
    ("A Vehicle for Star", "Invent", "Create imaginative transport"),
    ("Build a Playground", "Invent", "Plan a playful environment"),
    ("A Helpful Machine", "Invent", "Imagine a machine that helps"),
    ("New Shoes", "Invent", "Design footwear for a special purpose"),
    ("A Home for an Animal", "Invent", "Create a suitable animal shelter"),
    ("My Big Idea", "Invent", "Combine imagination, creation and explanation"),
    ("Creative Choice", "Celebrate", "Choose a preferred creative challenge"),
    ("I Tried Something New", "Celebrate", "Reflect on exploration and effort"),
    ("I Can Share Ideas", "Celebrate", "Celebrate communication of ideas"),
    ("Creative Thinker Certificate", "Celebrate", "Recognise creative growth"),
    ("Parent Partnership", "Celebrate", "Extend creativity through home play"),
    ("Back Cover", "Celebrate", "Close the book with the series identity"),
]

assert len(pages) == 44

BOOK.joinpath("README.md").write_text(
    "# Creative Thinkers Gold™\n\nNursery (3+) title in the BCube Future Skills Learning Series™. "
    "This complete repository package covers curriculum, architecture, deterministic production prompts, validation, artwork governance and publishing controls.\n",
    encoding="utf-8",
)

docs = {
    "00_Project_Overview.md": "# Project Overview\n\nCreative Thinkers Gold develops imagination, experimentation, creation, invention and expression through age-appropriate visual activities.\n",
    "01_Curriculum.md": "# Curriculum\n\nThe learning cycle is Imagine → Create → Explore → Express → Invent → Celebrate. Activities value originality, choice, playful experimentation and communication rather than one decorative answer.\n",
    "02_Book_Structure.md": "# Book Structure\n\n44 pages arranged as welcome matter, six progressive learning modules, celebration pages and back cover.\n",
    "03_Scope_and_Sequence.md": "# Scope and Sequence\n\n| Module | Pages | Focus |\n|---|---:|---|\n| Welcome | 1–4 | Orientation and ownership |\n| Imagine | 5–11 | Possibility and visual imagination |\n| Create | 12–18 | Constructing original pictures |\n| Explore | 19–25 | Variation and multiple approaches |\n| Express | 26–31 | Story, emotion and personal voice |\n| Invent | 32–38 | Purposeful new ideas |\n| Celebrate | 39–44 | Choice, reflection and partnership |\n",
    "04_Learning_Outcomes.md": "# Learning Outcomes\n\nChildren notice possibilities, generate ideas, transform shapes, make choices, try alternatives, express preferences, invent simple solutions and discuss their creative process.\n",
    "05_Module_Structure.md": "# Module Structure\n\nEach module uses a clear learning focus, large child action, teacher facilitation, Star support, parent extension and measurable page-level QA.\n",
    "07_Creative_Thinking_Progression_Matrix.md": "# Creative Thinking Progression Matrix\n\n| Stage | Child capability |\n|---|---|\n| Imagine | Sees possibilities |\n| Create | Makes an original response |\n| Explore | Tries alternatives |\n| Express | Communicates meaning |\n| Invent | Designs for a purpose |\n| Celebrate | Reflects and shares |\n",
    "08_Illustration_Bible.md": "# Illustration Bible\n\nUse premium preschool illustration, rounded forms, clean outlines, white space, recognisable objects, inclusive children, consistent Star mascot and one dominant activity focus.\n",
    "09_Character_Bible.md": "# Character Bible\n\nChildren appear Nursery-aged with natural expressions and safe readable poses. Star remains a friendly yellow rounded mascot who supports rather than completes the task.\n",
    "10_Design_System.md": "# Design System\n\nA4 portrait, approved BCube logo, exact title hierarchy, generous safe margins, short child instructions, activity-first composition and consistent footer/page numbering.\n",
    "11_QA_Bible.md": "# QA Bible\n\nEvery page must pass content, learning, design, brand, accessibility, illustration consistency and publishing-readiness gates.\n",
    "12_Publishing_Bible.md": "# Publishing Bible\n\nFinal release requires 44 approved pages, prepress validation, print proof, publisher sign-off, checksum and archived sources.\n",
}
for name, content in docs.items():
    DOCS.joinpath(name).write_text(content, encoding="utf-8")

page_map = ["# Page Map", "", "| Page | ID | Title | Module | Learning focus |", "|---:|---|---|---|---|"]
for i, (title, module, focus) in enumerate(pages, start=1):
    page_map.append(f"| {i} | CT-NURSERY-V5-P{i:03d} | {title} | {module} | {focus} |")
DOCS.joinpath("06_Page_Map.md").write_text("\n".join(page_map) + "\n", encoding="utf-8")

with PLANNING.joinpath("page-index.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["page", "prompt_id", "title", "module", "learning_focus"])
    for i, (title, module, focus) in enumerate(pages, start=1):
        writer.writerow([i, f"CT-NURSERY-V5-P{i:03d}", title, module, focus])

module_ranges = [("Welcome",1,4),("Imagine",5,11),("Create",12,18),("Explore",19,25),("Express",26,31),("Invent",32,38),("Celebrate",39,44)]
with PLANNING.joinpath("module-index.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["module", "start_page", "end_page"])
    writer.writerows(module_ranges)

sections = [
    "Release metadata", "Production command", "Engine order and precedence", "Page purpose",
    "Learning objective", "Child-facing content", "Teaching guidance", "Parent partnership",
    "Layout architecture", "Illustration direction", "Character and mascot rules", "Brand and typography",
    "Accessibility and inclusion", "Negative constraints", "Quality assurance and acceptance criteria",
]

rows = []
for i, (title, module, focus) in enumerate(pages, start=1):
    pid = f"CT-NURSERY-V5-P{i:03d}"
    body = [f"# {pid} — {title}", ""]
    values = [
        f"Prompt ID: {pid}\nVersion: 5.0.0\nBook: Creative Thinkers Gold™\nLevel: Nursery (3+)\nModule: {module}\nPage: {i} of 44\nExact title: {title}",
        f"Create exactly one final, flat, front-facing A4 portrait page for “{title}”. Produce no explanation, alternate, mockup or additional page.",
        "Publishing Engine > Design Engine > Visual Grammar Engine > Educational Engine > Teaching Engine > Parent Partnership Engine > Illustration Engine > Character Engine > Quality Assurance. Approved page instruction has highest precedence.",
        f"Support the learning focus: {focus}. Keep one dominant child action and a clear visual outcome.",
        f"The child will {focus.lower()} through a playful, open-ended Nursery activity that permits meaningful choice.",
        f"Use the exact title “{title}” as normal readable text. Provide one short action instruction suitable for an adult to read aloud. Do not embed essential instructions inside decorative artwork.",
        "Teacher: model curiosity, ask one open question, allow wait time, accept more than one reasonable response and invite the child to describe a choice without correcting originality.",
        "Parent: repeat the idea with safe household materials, praise effort and experimentation, and ask the child to explain what they made or imagined.",
        "A4 portrait with generous safe margins; official BCube logo in the approved location; centered normal-text page title; large activity zone; restrained support text; page number at bottom right where applicable.",
        f"Use premium preschool artwork with large rounded forms and recognisable objects. The composition must visually support “{focus}” with ample white space and a clear place for the child to act.",
        "Use inclusive Nursery-aged children with natural expressions and readable poses. Star is a consistent yellow rounded mascot and must support, point, wonder or encourage without completing the child’s work.",
        "Preserve the official BCube Future Academy logo, BCube Future Skills Learning Series™ naming and four pillars: Creativity, Communication, Curiosity and Confidence. Use approved rounded child-friendly typography.",
        "Colour is not the only instructional cue. Maintain clear figure-ground separation, large motor-friendly marks, simple visual language, culturally inclusive representation and instructions understandable when read aloud.",
        "No photorealism, empty speech bubbles, tiny details, overcrowding, harsh shadows, dark full-page backgrounds, altered logo, incorrect title, decorative pseudo-text, unsafe objects, multiple competing tasks or one rigid model answer.",
        "Pass only when identity, exact title, page sequence, learning focus, open-ended creativity, child action, teacher support, parent extension, A4 layout, brand, accessibility, illustration clarity and print safety are all correct. Human visual approval remains mandatory.",
    ]
    for n, (section, value) in enumerate(zip(sections, values), start=1):
        body.extend([f"## {n}. {section}", value, ""])
    text = "\n".join(body)
    PROMPTS.joinpath(f"P{i:03d}.md").write_text(text, encoding="utf-8")
    rows.append([i, pid, title, module, focus, text])

csv_path = BOOK / "Creative_Thinkers_Gold_Production_Prompts_v5.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Page", "Prompt ID", "Title", "Module", "Learning Focus", "Production Prompt"])
    writer.writerows(rows)

wb = Workbook()
ws = wb.active
ws.title = "Production Prompts"
ws.append(["Page", "Prompt ID", "Title", "Module", "Learning Focus", "Production Prompt"])
for row in rows:
    ws.append(row)
ws.freeze_panes = "A2"
ws.auto_filter.ref = ws.dimensions
ws.column_dimensions["A"].width = 8
ws.column_dimensions["B"].width = 24
ws.column_dimensions["C"].width = 30
ws.column_dimensions["D"].width = 16
ws.column_dimensions["E"].width = 44
ws.column_dimensions["F"].width = 100
wb.save(BOOK / "Creative_Thinkers_Gold_Production_Prompts_v5.xlsx")

validation_files = {
    "README.md": "# Validation Framework\n\nAutomated checks support, but do not replace, human educational, design, accessibility and visual approval for all 44 pages.\n",
    "design-validation-checklist.md": "# Design Validation Checklist\n\n- A4 portrait and safe margins\n- Exact title as normal text\n- Official BCube logo\n- One dominant learning focus\n- Large activity area\n- No clipping, overlap or overcrowding\n",
    "layout-validation.md": "# Layout Validation\n\nCheck title zone, instruction zone, activity area, footer, page number, whitespace, binding clearance and print-safe placement.\n",
    "typography-validation.md": "# Typography Validation\n\nUse approved readable type hierarchy. Titles and instructions must remain exact, large and free from decorative distortion.\n",
    "brand-validation.md": "# Brand Validation\n\nUse approved BCube assets, correct series naming and the four pillars without alteration.\n",
    "accessibility-validation.md": "# Accessibility Validation\n\nUse clear contrast, large marks, simple visual cues, inclusive representation and instructions that work when read aloud.\n",
    "creative-thinking-activity-validation.md": "# Creative Thinking Activity Validation\n\nActivities must permit meaningful choice, imagination, experimentation or invention. Repetitive colouring-only work and one predetermined decorative answer block approval.\n",
    "illustration-readiness-checklist.md": "# Illustration Readiness Checklist\n\nConfirm title, objective, child action, focal objects, composition, Star role, negative constraints and QA gates before artwork generation.\n",
}
for name, content in validation_files.items():
    VALIDATION.joinpath(name).write_text(content, encoding="utf-8")

illustration_files = {
    "illustration-consistency-matrix.md": "# Illustration Consistency Matrix\n\n| Area | Locked expectation |\n|---|---|\n| Style | Premium preschool, rounded forms, clean outlines |\n| Star | Consistent yellow rounded mascot |\n| Children | Nursery-aged, inclusive, natural expressions |\n| Objects | Large, recognisable, low-detail |\n| Background | Mostly white with restrained pastel accents |\n| Complexity | One dominant focus |\n",
    "object-library.md": "# Object Library\n\nApproved families include shapes, drawing tools, blocks, toys, robots, vehicles, houses, gardens, playground objects, friendly animals, simple machines and safe household materials.\n",
    "character-consistency.md": "# Character Consistency\n\nMaintain stable age cues, proportions, safe gestures and expression language. Star supports the child and never replaces the child’s creative action.\n",
}
for name, content in illustration_files.items():
    ILLUSTRATION.joinpath(name).write_text(content, encoding="utf-8")

required_sections = [f"## {i}." for i in range(1, 16)]
results = []
for i in range(1, 45):
    path = PROMPTS / f"P{i:03d}.md"
    text = path.read_text(encoding="utf-8")
    checks = {
        "filename": path.name == f"P{i:03d}.md",
        "prompt_id": f"CT-NURSERY-V5-P{i:03d}" in text,
        "sections_15": all(s in text for s in required_sections),
        "a4_portrait": "A4 portrait" in text,
        "nursery_age": "Nursery (3+)" in text,
        "brand": "BCube" in text,
        "creative_alignment": any(word in text for word in ("Imagine", "Create", "Explore", "Express", "Invent", "Celebrate")),
        "teacher": "Teacher:" in text,
        "parent": "Parent:" in text,
        "accessibility": "Accessibility" in text,
    }
    score = sum(checks.values()) * 10
    results.append({"page": i, "file": path.name, "score": score, "checks": checks})

all_pass = len(results) == 44 and all(item["score"] >= 90 for item in results)

PRODUCTION.joinpath("asset-map.json").write_text(json.dumps({
    "book": "Creative Thinkers Gold", "pages": 44,
    "required_assets": ["official_bcube_logo", "approved_star_mascot", "approved_font_set", "page_template"],
    "prompt_files": [f"P{i:03d}.md" for i in range(1,45)]
}, indent=2) + "\n", encoding="utf-8")
PRODUCTION.joinpath("validation-manifest.json").write_text(json.dumps({
    "delivery": "complete", "book": "Creative Thinkers Gold", "prompt_count": 44,
    "required_sections": 15, "automated_threshold": 90, "all_prompts_pass": all_pass
}, indent=2) + "\n", encoding="utf-8")
PRODUCTION.joinpath("release-status.json").write_text(json.dumps({
    "framework_status": "complete", "automated_validation": "pass" if all_pass else "block",
    "artwork_approved_pages": 0, "artwork_release_allowed": False,
    "reason": "Human visual and educational approval required"
}, indent=2) + "\n", encoding="utf-8")

QA.joinpath("complete-validation-report.json").write_text(json.dumps({
    "status": "pass" if all_pass else "block", "expected": 44, "actual": len(results),
    "minimum_score": min(item["score"] for item in results), "pages": results
}, indent=2) + "\n", encoding="utf-8")
QA.joinpath("prompt-consistency-report.md").write_text(f"# Prompt Consistency Report\n\n- Prompt files: {len(results)}\n- Sequential IDs: PASS\n- Required sections: 15\n- Minimum score: {min(item['score'] for item in results)}\n- Decision: {'PASS' if all_pass else 'BLOCK'}\n", encoding="utf-8")
QA.joinpath("creative-thinking-readiness-report.md").write_text("# Creative Thinking Readiness Report\n\nThe sequence balances imagination, creation, exploration, expression, invention and reflection. Human review must confirm genuine choice and avoid repetitive one-answer activities.\n", encoding="utf-8")

phase5_files = {
    "README.md": "# Phase 5 — Artwork Production Framework\n\nFramework complete; actual artwork remains not started and is governed page by page.\n",
    "artwork-pipeline.md": "# Artwork Pipeline\n\n1. Load approved prompt and assets.\n2. Generate one flat A4 page.\n3. Check exact content and hierarchy.\n4. Review learning clarity and open-ended creativity.\n5. Review brand, accessibility and consistency.\n6. Record decision.\n7. Release only after all gates pass.\n",
    "illustration-generation-guidelines.md": "# Illustration Generation Guidelines\n\nUse large recognisable objects, rounded forms, clean outlines, restrained detail and one dominant activity. Creative tasks must invite child choice and must not show one finished answer as compulsory.\n",
    "review-checklist.md": "# Page Review Checklist\n\n- Exact title and instruction\n- Activity matches objective\n- Meaningful creative choice\n- Correct logo and page architecture\n- Readable typography\n- Consistent Star and children\n- Accessible visual cues\n- Print-safe composition\n",
    "illustration-release-plan.md": "# Illustration Release Plan\n\n- Batch 1: P001–P011\n- Batch 2: P012–P022\n- Batch 3: P023–P033\n- Batch 4: P034–P044\n\nEach batch requires prompt-to-page, consistency and publishing approval.\n",
}
for name, content in phase5_files.items():
    PHASE5.joinpath(name).write_text(content, encoding="utf-8")
with PHASE5.joinpath("page-review-status.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["page","page_id","artwork_status","educational_review","design_review","illustration_review","accessibility_review","publishing_review","final_decision"])
    for i in range(1,45):
        writer.writerow([i,f"CT-NURSERY-V5-P{i:03d}","not_started","pending","pending","pending","pending","pending","blocked"])
PHASE5.joinpath("asset-tracking.json").write_text(json.dumps({
    "book":"Creative Thinkers Gold","page_count":44,"approved_pages":0,"artwork_status":"not_started",
    "required_assets":["official_bcube_logo","approved_star_mascot","locked_font_family","page_template"],"release_allowed":False
}, indent=2) + "\n", encoding="utf-8")
PHASE5.joinpath("artwork-manifest.json").write_text(json.dumps({
    "schema_version":"1.0.0","book_id":"CT-NURSERY-V5","expected_pages":44,"approved_pages":0,
    "batches":[{"id":"B1","range":"P001-P011","status":"not_started"},{"id":"B2","range":"P012-P022","status":"not_started"},{"id":"B3","range":"P023-P033","status":"not_started"},{"id":"B4","range":"P034-P044","status":"not_started"}],"release_allowed":False
}, indent=2) + "\n", encoding="utf-8")

phase6_files = {
    "README.md": "# Phase 6 — Publishing Framework\n\nFramework complete. Publication remains blocked until all 44 artworks and prepress gates are approved.\n",
    "prepress-checklist.md": "# Prepress Checklist\n\n- Exactly 44 pages\n- A4 portrait trim and bleed\n- Print resolution\n- Embedded approved fonts\n- Correct page order\n- No clipped, blank or duplicate pages\n- Publisher details verified\n",
    "print-validation.md": "# Print Validation\n\nReview final PDF at 100% and through a physical or certified proof for line weight, colour, legibility, trim safety, binding clearance and activity usability.\n",
    "final-release-checklist.md": "# Final Release Checklist\n\n- 44/44 artwork approvals\n- Final PDF and checksum\n- Prepress pass\n- Proof approval\n- Completed release manifest\n- Archived source and outputs\n- Publisher sign-off\n",
    "publication-gates.md": "# Publication Gates\n\n1. Prompt package pass\n2. Automated validation pass\n3. Human artwork approval 44/44\n4. Prepress pass\n5. Print proof pass\n6. Publisher sign-off\n",
    "print-approval.md": "# Print Approval\n\nBook: Creative Thinkers Gold\nEdition: First Edition\n\n- Editorial: pending\n- Educational: pending\n- Design: pending\n- Prepress: pending\n- Publisher: pending\n",
}
for name, content in phase6_files.items():
    PHASE6.joinpath(name).write_text(content, encoding="utf-8")
PHASE6.joinpath("release-manifest-template.json").write_text(json.dumps({
    "schema_version":"1.0.0","book_id":"CT-NURSERY-V5","title":"Creative Thinkers Gold","edition":"First Edition",
    "page_count":44,"source_branch":"book7/creative-thinkers-complete","artwork_approved_pages":0,
    "final_pdf":None,"final_pdf_sha256":None,"release_zip":None,"release_status":"blocked","approvals":[]
}, indent=2) + "\n", encoding="utf-8")
PHASE6.joinpath("publication-status.json").write_text(json.dumps({
    "book_id":"CT-NURSERY-V5","framework_status":"complete","artwork_approved_pages":0,"required_pages":44,
    "prepress_status":"not_started","print_approval_status":"not_started","publication_status":"blocked"
}, indent=2) + "\n", encoding="utf-8")

PUBLISHING.joinpath("complete-book-manifest.json").write_text(json.dumps({
    "book_id":"CT-NURSERY-V5","title":"Creative Thinkers Gold","delivery":"phases_1_to_6",
    "prompt_count":44,"csv_workbook":csv_path.name,"xlsx_workbook":"Creative_Thinkers_Gold_Production_Prompts_v5.xlsx",
    "automated_validation":"pass" if all_pass else "block","framework_status":"complete","artwork_status":"not_started","publication_status":"blocked"
}, indent=2) + "\n", encoding="utf-8")

required = [
    BOOK / "README.md", csv_path, BOOK / "Creative_Thinkers_Gold_Production_Prompts_v5.xlsx",
    *(PROMPTS / f"P{i:03d}.md" for i in range(1,45)),
    *(VALIDATION / name for name in validation_files), *(ILLUSTRATION / name for name in illustration_files),
    *(PHASE5 / name for name in phase5_files), PHASE5 / "page-review-status.csv", PHASE5 / "asset-tracking.json", PHASE5 / "artwork-manifest.json",
    *(PHASE6 / name for name in phase6_files), PHASE6 / "release-manifest-template.json", PHASE6 / "publication-status.json",
]
missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
overall = all_pass and not missing
summary = {
    "book":"Creative Thinkers Gold","delivery":"complete_phases_1_to_6","expected_prompts":44,"actual_prompts":len(results),
    "sequential_ids":True,"required_sections":15,"automated_validation":"pass" if all_pass else "block",
    "phase5_framework":"pass" if not missing else "fail","phase6_framework":"pass" if not missing else "fail",
    "missing_files":missing,"overall_decision":"PASS" if overall else "BLOCK"
}
QA.joinpath("complete-book-report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
QA.joinpath("complete-book-summary.md").write_text(
    "# Book 7 Complete Delivery Summary\n\n"
    f"- Expected prompts: 44\n- Actual prompts: {len(results)}\n- Sequential deterministic IDs: PASS\n"
    f"- Required sections: 15 per prompt\n- Automated validation: {'PASS' if all_pass else 'BLOCK'}\n"
    f"- Phase 5 framework: {'PASS' if not missing else 'FAIL'}\n- Phase 6 framework: {'PASS' if not missing else 'FAIL'}\n"
    f"- Missing required files: {len(missing)}\n\n## Decision\n`{'PASS — PHASES 1–6 COMPLETE' if overall else 'BLOCK — CORRECTIONS REQUIRED'}`\n\n"
    "Actual artwork generation, human page approval, prepress proof and final publication remain pending.\n",
    encoding="utf-8",
)

if not overall:
    raise SystemExit("Book 7 complete delivery validation failed")
print(json.dumps(summary, indent=2))
