from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'books' / 'nursery' / 'creativity-creators'
PROMPTS = BOOK / 'production-prompts'

required_sections = [f'## {i}.' for i in range(1, 16)]
files = sorted(PROMPTS.glob('P*.md'))
results = []
for idx, path in enumerate(files, start=1):
    text = path.read_text(encoding='utf-8')
    expected_file = f'P{idx:03d}.md'
    expected_id = f'CC-NURSERY-V5-P{idx:03d}'
    missing = [s for s in required_sections if s not in text]
    checks = {
        'filename': path.name == expected_file,
        'prompt_id': expected_id in text,
        'sections_15': not missing,
        'a4_portrait': 'A4 portrait' in text,
        'nursery_age': 'Nursery' in text and '3+' in text,
        'brand': 'BCube' in text,
        'creativity_pillar': any(p in text for p in ['Imagine','Create','Experiment','Express']),
        'teacher_prompt': 'Teacher' in text,
        'parent_prompt': 'Parent' in text,
        'accessibility': 'accessib' in text.lower(),
    }
    score = sum(checks.values()) * 10
    results.append({'page': idx, 'file': path.name, 'prompt_id': expected_id, 'score': score, 'checks': checks, 'missing_sections': missing})

all_pass = len(files) == 44 and all(r['score'] >= 90 for r in results)

validation = BOOK / 'validation'
qa = BOOK / 'qa'
illustration = BOOK / 'illustration'
production = BOOK / 'production'
publishing = BOOK / 'publishing'
for d in [validation, qa, illustration, production, publishing]: d.mkdir(parents=True, exist_ok=True)

(validation / 'README.md').write_text('''# Commit C Validation Framework\n\nThis folder defines automated and human quality gates for all 44 Creativity Creators Gold pages. Automated checks support production readiness but never replace educational, design, accessibility or visual approval.\n''', encoding='utf-8')
(validation / 'design-validation-checklist.md').write_text('''# Design Validation Checklist\n\n- A4 portrait composition and safe margins\n- Locked BCube logo and brand hierarchy\n- Exact page title and page number\n- Nursery badge only where approved\n- One dominant learning focus\n- Large activity marks and uncluttered white space\n- No empty speech bubbles or decorative pseudo-instructions\n- Illustration does not overlap title, instruction or footer\n''', encoding='utf-8')
(validation / 'layout-validation.md').write_text('''# Layout Validation\n\nValidate trim-safe margins, title zone, instruction zone, dominant activity area, visual balance, footer placement, page-number accuracy, and print-safe object placement on every page. Any clipping, unsafe bleed, cramped activity area or competing focal point is a blocking defect.\n''', encoding='utf-8')
(validation / 'typography-validation.md').write_text('''# Typography Validation\n\nUse the approved BCube type hierarchy. Titles must be readable, correctly capitalised and consistent. Child instructions must be short, concrete and large enough for classroom use. Avoid condensed text, excessive weights, decorative fonts and text embedded inside complex artwork.\n''', encoding='utf-8')
(validation / 'brand-validation.md').write_text('''# Brand Validation\n\nUse only approved BCube Future Academy assets. Preserve official logo proportions, the BCube Future Skills Learning Series naming, and the four pillars: Creativity, Communication, Curiosity and Confidence. Unapproved redraws, altered marks or inconsistent naming block release.\n''', encoding='utf-8')
(validation / 'accessibility-validation.md').write_text('''# Accessibility Validation\n\n- Clear figure-ground separation\n- Colour is never the only instructional signal\n- Recognisable objects and simple visual language\n- Large motor-friendly marks and spaces\n- No overcrowding, harsh contrast or tiny details\n- Instructions understandable when read aloud\n''', encoding='utf-8')
(validation / 'illustration-readiness-checklist.md').write_text('''# Illustration Readiness Checklist\n\nBefore artwork begins, confirm exact title, page ID, learning objective, child action, focal objects, composition, palette intent, Star role, teacher facilitation, parent extension, negative constraints and QA criteria. Missing or conflicting directions block generation.\n''', encoding='utf-8')

(qa / 'prompt-consistency-report.md').write_text(f'''# Prompt Consistency Report\n\n- Prompt files found: {len(files)}\n- Expected sequence: P001-P044\n- Unique deterministic IDs: {len({r['prompt_id'] for r in results})}\n- Required section count: 15\n- Minimum automated score: {min((r['score'] for r in results), default=0)}\n- Decision: {'PASS' if all_pass else 'BLOCK'}\n''', encoding='utf-8')
(qa / 'prompt-quality-score.md').write_text('''# Prompt Quality Score\n\nScoring model: identity 10, structure 10, format 10, age suitability 10, brand 10, creativity-pillar alignment 10, teacher support 10, parent support 10, accessibility 10 and production completeness 10. Automated threshold: 90/100. Human page-readiness approval remains mandatory.\n''', encoding='utf-8')
(qa / 'creativity-readiness-report.md').write_text('''# Creativity Readiness Report\n\nThe book must balance Imagine, Create, Experiment and Express across the sequence. Pages should encourage choice, originality, exploration and communication rather than one predetermined decorative result. Repetitive colouring-only tasks or over-directed copying block creativity approval.\n''', encoding='utf-8')
summary = f'''# Commit C Validation Summary\n\n- Expected prompts: 44\n- Actual prompts: {len(files)}\n- Sequential IDs: {'PASS' if len(files)==44 else 'BLOCK'}\n- Automated prompt threshold: 90/100\n- Overall automated decision: {'PASS' if all_pass else 'BLOCK'}\n\n## Release decision\n\n`VALIDATION FRAMEWORK COMPLETE — HUMAN VISUAL APPROVAL REQUIRED BEFORE ARTWORK RELEASE`\n'''
(qa / 'phase4-validation-summary.md').write_text(summary, encoding='utf-8')

(illustration / 'illustration-consistency-matrix.md').write_text('''# Illustration Consistency Matrix\n\n| Area | Locked expectation |\n|---|---|\n| Style | Premium preschool illustration, rounded forms, clean outlines |\n| Characters | Stable proportions, expressions and clothing language |\n| Star mascot | Consistent yellow rounded star form and supportive role |\n| Objects | Large, recognisable, low-detail, activity-relevant |\n| Background | Mostly white with restrained pastel accents |\n| Complexity | One dominant learning focus, minimal decorative clutter |\n''', encoding='utf-8')
(illustration / 'object-library.md').write_text('''# Object Library\n\nApproved object families include drawing tools, simple shapes, blocks, toys, vehicles, playground elements, leaves, flowers, clouds, butterflies, friendly animals and simple invention parts. Objects must remain recognisable for Nursery children and use consistent visual grammar across pages.\n''', encoding='utf-8')
(illustration / 'character-consistency.md').write_text('''# Character Consistency\n\nMaintain consistent child age cues, friendly natural expressions, inclusive representation, safe gestures and readable poses. Star must never dominate the child activity unless the page specifically introduces the mascot. Character clothing and proportions should remain stable across related scenes.\n''', encoding='utf-8')

asset_map = {'book':'Creativity Creators Gold','pages':44,'required_assets':['official_bcube_logo','star_mascot_reference','approved_font_set','design_tokens'],'prompt_files':[r['file'] for r in results]}
(production / 'asset-map.json').write_text(json.dumps(asset_map, indent=2), encoding='utf-8')
release = {'commit':'C','automated_validation':'pass' if all_pass else 'block','prompt_count':len(files),'artwork_generation_allowed':False,'reason':'Human educational, visual, brand and illustration-readiness approval required','next_gate':'Commit D production and publishing framework'}
(production / 'release-status.json').write_text(json.dumps(release, indent=2), encoding='utf-8')
manifest = {'commit':'C','book':'Creativity Creators Gold','prompt_count':len(files),'required_sections':15,'automated_threshold':90,'all_prompts_pass':all_pass,'validation_files':13}
(production / 'validation-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

(publishing / 'prepress-checklist.md').write_text('''# Prepress Checklist\n\n- A4 portrait document geometry\n- Approved bleed and trim setup\n- Embedded or outlined approved fonts\n- Print-safe image resolution\n- Correct page order P001-P044\n- No missing, clipped or low-resolution assets\n- Colour and black handling reviewed\n- Final proof signed before release\n''', encoding='utf-8')
(publishing / 'release-gates.md').write_text('''# Release Gates\n\n1. Curriculum and architecture approved\n2. All 44 production prompts structurally valid\n3. Human educational and creativity review approved\n4. Brand and illustration-readiness approved\n5. Artwork review approved page by page\n6. Prepress proof approved\n7. Final PDF and release manifest generated\n\nNo later gate may override a failed earlier gate.\n''', encoding='utf-8')

report = {'status':'pass' if all_pass else 'block','expected':44,'actual':len(files),'minimum_score':min((r['score'] for r in results), default=0),'pages':results}
(qa / 'commit-c-validation-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

if not all_pass:
    raise SystemExit('Commit C validation failed')
print('Commit C validation passed')
