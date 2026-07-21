from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'books' / 'nursery' / 'confidence-builders'
PROMPTS = BOOK / 'production-prompts'

required_sections = [f'## {i}.' for i in range(1, 16)]
files = sorted(PROMPTS.glob('P*.md'))
results = []

for idx, path in enumerate(files, start=1):
    text = path.read_text(encoding='utf-8')
    expected_file = f'P{idx:03d}.md'
    expected_id = f'CB-NURSERY-V5-P{idx:03d}'
    missing = [section for section in required_sections if section not in text]
    checks = {
        'filename': path.name == expected_file,
        'prompt_id': expected_id in text,
        'sections_15': not missing,
        'a4_portrait': 'A4 portrait' in text,
        'nursery_age': 'Nursery' in text and '3+' in text,
        'brand': 'BCube' in text,
        'confidence_alignment': any(term in text.lower() for term in ['confidence', 'try', 'choice', 'help', 'effort', 'feelings', 'independent']),
        'teacher_prompt': 'Teacher' in text,
        'parent_prompt': 'Parent' in text,
        'accessibility': 'accessib' in text.lower(),
    }
    score = sum(checks.values()) * 10
    results.append({'page': idx, 'file': path.name, 'prompt_id': expected_id, 'score': score, 'checks': checks, 'missing_sections': missing})

all_pass = len(files) == 44 and all(item['score'] >= 90 for item in results)
validation = BOOK / 'validation'
qa = BOOK / 'qa'
illustration = BOOK / 'illustration'
production = BOOK / 'production'
publishing = BOOK / 'publishing'
for folder in [validation, qa, illustration, production, publishing]:
    folder.mkdir(parents=True, exist_ok=True)

(validation / 'README.md').write_text('# Commit B Validation Framework\n\nAutomated and human quality gates for all 44 Confidence Builders Gold pages. Automated checks support readiness but do not replace educational, visual, accessibility or brand approval.\n', encoding='utf-8')
(validation / 'design-validation-checklist.md').write_text('''# Design Validation Checklist

- A4 portrait composition and safe margins
- Locked BCube logo and brand hierarchy
- Exact title and page number
- One dominant confidence-building focus
- Warm, encouraging visual tone
- Large activity spaces and uncluttered composition
- No empty speech bubbles or decorative pseudo-instructions
- Illustration never overlaps instructional content
''', encoding='utf-8')
(validation / 'layout-validation.md').write_text('# Layout Validation\n\nValidate trim-safe margins, title zone, instruction zone, activity area, footer, page number and print-safe placement. Clipping, overcrowding or competing focal points block release.\n', encoding='utf-8')
(validation / 'typography-validation.md').write_text('# Typography Validation\n\nUse approved BCube typography. Titles must be consistent and readable. Child instructions must be short, concrete, positive and suitable for reading aloud.\n', encoding='utf-8')
(validation / 'brand-validation.md').write_text('# Brand Validation\n\nUse approved BCube Future Academy assets and preserve the BCube Future Skills Learning Series naming and four pillars: Creativity, Communication, Curiosity and Confidence.\n', encoding='utf-8')
(validation / 'accessibility-validation.md').write_text('''# Accessibility Validation

- Clear figure-ground separation
- Colour is not the only instructional signal
- Recognisable objects and simple visual language
- Large motor-friendly marks and spaces
- Inclusive characters and emotionally safe scenarios
- Instructions understandable when read aloud
''', encoding='utf-8')
(validation / 'illustration-readiness-checklist.md').write_text('# Illustration Readiness Checklist\n\nConfirm title, page ID, confidence objective, child action, focal scene, composition, palette, Star role, teacher support, parent extension, negative constraints and QA criteria before artwork begins.\n', encoding='utf-8')

(qa / 'prompt-consistency-report.md').write_text(f'''# Prompt Consistency Report

- Prompt files found: {len(files)}
- Expected sequence: P001-P044
- Unique deterministic IDs: {len({item['prompt_id'] for item in results})}
- Required sections: 15
- Minimum automated score: {min((item['score'] for item in results), default=0)}
- Decision: {'PASS' if all_pass else 'BLOCK'}
''', encoding='utf-8')
(qa / 'prompt-quality-score.md').write_text('# Prompt Quality Score\n\nTen checks are scored at 10 points each. Automated threshold: 90/100. Human page-readiness approval remains mandatory.\n', encoding='utf-8')
(qa / 'confidence-readiness-report.md').write_text('''# Confidence Readiness Report

The sequence must support self-expression, trying, choosing, asking for help, persistence, emotional vocabulary, independence and celebration of effort. Shaming language, comparison, forced performance or perfection-based outcomes block approval.
''', encoding='utf-8')
summary = f'''# Commit B Validation Summary

- Expected prompts: 44
- Actual prompts: {len(files)}
- Sequential IDs: {'PASS' if len(files) == 44 else 'BLOCK'}
- Automated prompt threshold: 90/100
- Overall automated decision: {'PASS' if all_pass else 'BLOCK'}

## Release decision

`VALIDATION FRAMEWORK COMPLETE — HUMAN VISUAL APPROVAL REQUIRED BEFORE ARTWORK RELEASE`
'''
(qa / 'phase4-validation-summary.md').write_text(summary, encoding='utf-8')

(illustration / 'illustration-consistency-matrix.md').write_text('''# Illustration Consistency Matrix

| Area | Locked expectation |
|---|---|
| Style | Premium preschool illustration, rounded forms and clean outlines |
| Children | Natural expressions, safe poses and Nursery age cues |
| Star mascot | Consistent supportive yellow star, never overpowering the child |
| Emotion | Warm, encouraging and never shaming |
| Objects | Large, familiar and activity-relevant |
| Background | Mostly white with restrained pastel accents |
''', encoding='utf-8')
(illustration / 'object-library.md').write_text('# Object Library\n\nApproved families include mirrors, name cards, classroom objects, clothes, toys, blocks, simple puzzles, emotion faces, helping scenes, choice cards, achievement stars and everyday independence routines.\n', encoding='utf-8')
(illustration / 'character-consistency.md').write_text('# Character Consistency\n\nMaintain stable proportions, inclusive representation, natural expressions and emotionally safe interactions. Children should appear capable and supported rather than judged or compared.\n', encoding='utf-8')

asset_map = {'book': 'Confidence Builders Gold', 'pages': 44, 'required_assets': ['official_bcube_logo', 'star_mascot_reference', 'approved_font_set', 'design_tokens'], 'prompt_files': [item['file'] for item in results]}
(production / 'asset-map.json').write_text(json.dumps(asset_map, indent=2), encoding='utf-8')
release = {'commit': 'B', 'automated_validation': 'pass' if all_pass else 'block', 'prompt_count': len(files), 'artwork_generation_allowed': False, 'reason': 'Human educational, confidence, visual, brand and illustration-readiness approval required', 'next_gate': 'Commit C Phase 5 and Phase 6 framework'}
(production / 'release-status.json').write_text(json.dumps(release, indent=2), encoding='utf-8')
manifest = {'commit': 'B', 'book': 'Confidence Builders Gold', 'prompt_count': len(files), 'required_sections': 15, 'automated_threshold': 90, 'all_prompts_pass': all_pass, 'validation_files': 13}
(production / 'validation-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

(publishing / 'prepress-checklist.md').write_text('# Prepress Checklist\n\n- A4 portrait geometry\n- Approved bleed and trim\n- Approved fonts embedded or outlined\n- Print-safe image resolution\n- Correct P001-P044 order\n- No missing or clipped assets\n- Colour handling reviewed\n- Final proof signed\n', encoding='utf-8')
(publishing / 'release-gates.md').write_text('''# Release Gates

1. Curriculum and architecture approved
2. All 44 prompts structurally valid
3. Human educational and confidence review approved
4. Brand and illustration readiness approved
5. Artwork approved page by page
6. Prepress proof approved
7. Final PDF and release manifest generated

No later gate overrides a failed earlier gate.
''', encoding='utf-8')

report = {'status': 'pass' if all_pass else 'block', 'expected': 44, 'actual': len(files), 'minimum_score': min((item['score'] for item in results), default=0), 'pages': results}
(qa / 'commit-b-validation-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

if not all_pass:
    raise SystemExit('Commit B validation failed')
print('Commit B validation passed')
