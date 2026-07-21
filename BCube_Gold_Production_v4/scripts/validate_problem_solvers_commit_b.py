from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books" / "nursery" / "problem-solvers"
PROMPTS = BOOK / "production-prompts"

required_sections = [f"## {i}." for i in range(1, 16)]
files = sorted(PROMPTS.glob("P*.md"))
results = []

for index, path in enumerate(files, start=1):
    text = path.read_text(encoding="utf-8")
    expected_file = f"P{index:03d}.md"
    expected_id = f"PS-NURSERY-V5-P{index:03d}"
    missing = [section for section in required_sections if section not in text]
    checks = {
        "filename": path.name == expected_file,
        "prompt_id": expected_id in text,
        "sections_15": not missing,
        "a4_portrait": "A4 portrait" in text,
        "nursery_age": "Nursery" in text and "3+" in text,
        "brand": "BCube" in text,
        "problem_solving_pillar": any(word in text for word in ["Observe", "Think", "Try", "Solve", "Express"]),
        "teacher_prompt": "Teacher" in text,
        "parent_prompt": "Parent" in text,
        "accessibility": "accessib" in text.lower(),
    }
    score = sum(checks.values()) * 10
    results.append({
        "page": index,
        "file": path.name,
        "prompt_id": expected_id,
        "score": score,
        "checks": checks,
        "missing_sections": missing,
    })

all_pass = len(files) == 44 and all(item["score"] >= 90 for item in results)

validation = BOOK / "validation"
qa = BOOK / "qa"
illustration = BOOK / "illustration"
production = BOOK / "production"
publishing = BOOK / "publishing"
for directory in (validation, qa, illustration, production, publishing):
    directory.mkdir(parents=True, exist_ok=True)

(validation / "README.md").write_text(
    "# Commit B Validation Framework\n\nAutomated and human quality gates for all 44 Problem Solvers Gold pages. Automated checks support readiness but do not replace educational, visual, accessibility or publishing approval.\n",
    encoding="utf-8",
)
(validation / "design-validation-checklist.md").write_text(
    "# Design Validation Checklist\n\n- A4 portrait composition and safe margins\n- Exact title, page number and BCube hierarchy\n- One dominant problem-solving task\n- Large, uncluttered child activity area\n- No clipped, overlapping or decorative pseudo-instructions\n- Clear visual path from question to child action\n",
    encoding="utf-8",
)
(validation / "layout-validation.md").write_text(
    "# Layout Validation\n\nValidate title zone, instruction zone, problem area, answer/action area, visual sequence, safe margins and footer. Any ambiguity about where the child should look, think, mark or respond is a blocking defect.\n",
    encoding="utf-8",
)
(validation / "typography-validation.md").write_text(
    "# Typography Validation\n\nUse the approved BCube hierarchy. Child instructions must be brief, concrete and readable when spoken aloud. Avoid condensed text, decorative fonts, excessive weights and text embedded in complex artwork.\n",
    encoding="utf-8",
)
(validation / "brand-validation.md").write_text(
    "# Brand Validation\n\nUse approved BCube Future Academy assets and naming. Preserve the BCube Future Skills Learning Series and the four pillars: Creativity, Communication, Curiosity and Confidence. Altered marks or inconsistent naming block release.\n",
    encoding="utf-8",
)
(validation / "accessibility-validation.md").write_text(
    "# Accessibility Validation\n\n- Colour is never the only problem-solving signal\n- Objects are large and recognisable\n- Paths, matches and differences remain visually distinct\n- Instructions work when read aloud\n- No crowded scenes, tiny targets or misleading distractors\n- Motor actions are appropriate for Nursery children\n",
    encoding="utf-8",
)
(validation / "problem-solving-activity-validation.md").write_text(
    "# Problem-Solving Activity Validation\n\nEvery page must present one age-appropriate challenge with a visible Observe–Think–Try–Solve pathway. The task must allow success without reading independently, avoid trick questions, use fair distractors, and provide enough visual evidence for the child to reason.\n",
    encoding="utf-8",
)
(validation / "illustration-readiness-checklist.md").write_text(
    "# Illustration Readiness Checklist\n\nConfirm exact title, page ID, learning objective, child action, correct response logic, focal objects, distractors, composition, Star role, teacher facilitation, parent extension, negative constraints and QA criteria before artwork begins.\n",
    encoding="utf-8",
)

(qa / "prompt-consistency-report.md").write_text(
    f"# Prompt Consistency Report\n\n- Prompt files found: {len(files)}\n- Expected sequence: P001-P044\n- Unique deterministic IDs: {len({item['prompt_id'] for item in results})}\n- Required section count: 15\n- Minimum automated score: {min((item['score'] for item in results), default=0)}\n- Decision: {'PASS' if all_pass else 'BLOCK'}\n",
    encoding="utf-8",
)
(qa / "prompt-quality-score.md").write_text(
    "# Prompt Quality Score\n\nScoring covers identity, structure, page format, age suitability, brand, problem-solving alignment, teacher support, parent support, accessibility and production completeness. Automated threshold: 90/100. Human approval remains mandatory.\n",
    encoding="utf-8",
)
(qa / "problem-solving-readiness-report.md").write_text(
    "# Problem-Solving Readiness Report\n\nThe sequence must balance observing, matching, sorting, sequencing, path finding, comparison, cause and effect, simple planning and everyday decisions. Tasks must be fair, visually clear and solvable through evidence rather than guessing.\n",
    encoding="utf-8",
)
summary = (
    "# Commit B Validation Summary\n\n"
    f"- Expected prompts: 44\n- Actual prompts: {len(files)}\n"
    f"- Sequential IDs: {'PASS' if len(files) == 44 else 'BLOCK'}\n"
    "- Automated prompt threshold: 90/100\n"
    f"- Overall automated decision: {'PASS' if all_pass else 'BLOCK'}\n\n"
    "## Release decision\n\n"
    "`VALIDATION FRAMEWORK COMPLETE — HUMAN VISUAL APPROVAL REQUIRED BEFORE ARTWORK RELEASE`\n"
)
(qa / "phase4-validation-summary.md").write_text(summary, encoding="utf-8")

(illustration / "illustration-consistency-matrix.md").write_text(
    "# Illustration Consistency Matrix\n\n| Area | Locked expectation |\n|---|---|\n| Style | Premium preschool illustration, rounded forms, clean outlines |\n| Problem cues | Clear visual evidence and fair distractors |\n| Star mascot | Supportive guide, never revealing answers |\n| Objects | Large, recognisable and low-detail |\n| Background | Mostly white with restrained pastel accents |\n| Complexity | One dominant challenge with minimal clutter |\n",
    encoding="utf-8",
)
(illustration / "object-library.md").write_text(
    "# Object Library\n\nApproved families include toys, household objects, food, clothing, animals, vehicles, paths, blocks, shapes, patterns, containers, simple tools and classroom objects. All objects must be immediately recognisable to Nursery children.\n",
    encoding="utf-8",
)
(illustration / "character-consistency.md").write_text(
    "# Character Consistency\n\nMaintain stable child age cues, inclusive representation, safe gestures and readable poses. Star supports observation and effort but must not point directly to the correct answer unless the page explicitly teaches a worked example.\n",
    encoding="utf-8",
)

asset_map = {
    "book": "Problem Solvers Gold",
    "pages": 44,
    "required_assets": ["official_bcube_logo", "star_mascot_reference", "approved_font_set", "design_tokens"],
    "prompt_files": [item["file"] for item in results],
}
(production / "asset-map.json").write_text(json.dumps(asset_map, indent=2) + "\n", encoding="utf-8")
release = {
    "commit": "B",
    "automated_validation": "pass" if all_pass else "block",
    "prompt_count": len(files),
    "artwork_generation_allowed": False,
    "reason": "Human educational, visual, brand and illustration-readiness approval required",
    "next_gate": "Commit C production and publishing framework",
}
(production / "release-status.json").write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")
manifest = {
    "commit": "B",
    "book": "Problem Solvers Gold",
    "prompt_count": len(files),
    "required_sections": 15,
    "automated_threshold": 90,
    "all_prompts_pass": all_pass,
    "validation_files": 14,
}
(production / "validation-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

(publishing / "prepress-checklist.md").write_text(
    "# Prepress Checklist\n\n- A4 portrait geometry\n- Approved bleed and safe margins\n- Embedded or outlined approved fonts\n- Print-safe image resolution\n- Correct order P001-P044\n- No missing, duplicated, clipped or blank pages\n- Problem cues and answer spaces remain legible in print\n- Final proof signed before release\n",
    encoding="utf-8",
)
(publishing / "release-gates.md").write_text(
    "# Release Gates\n\n1. Curriculum and architecture approved\n2. All 44 prompts structurally valid\n3. Human educational and problem-solving review approved\n4. Brand, accessibility and illustration readiness approved\n5. Artwork approved page by page\n6. Prepress proof approved\n7. Final PDF and manifest generated\n\nNo later gate overrides an earlier failure.\n",
    encoding="utf-8",
)

report = {
    "status": "pass" if all_pass else "block",
    "expected": 44,
    "actual": len(files),
    "minimum_score": min((item["score"] for item in results), default=0),
    "pages": results,
}
(qa / "commit-b-validation-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

if not all_pass:
    raise SystemExit("Commit B validation failed")
print("Commit B validation passed")
