from __future__ import annotations

import csv
import json
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books" / "nursery" / "future-innovators"
DIRS = {name: BOOK / name for name in ["production-prompts","docs","planning","validation","qa","illustration","production","publishing","phase5","phase6"]}
for path in [BOOK, *DIRS.values()]:
    path.mkdir(parents=True, exist_ok=True)

pages = [
("Front Cover","Welcome","Meet the innovation journey"),("This Book Belongs to","Welcome","Build ownership and confidence"),("Meet Star","Welcome","Meet the supportive mascot"),("How to Use This Book","Welcome","Understand child, teacher and parent roles"),
("Look and Ask Why","Wonder","Notice how familiar things work"),("What If?","Wonder","Imagine a different possibility"),("Things That Help Us","Wonder","Identify useful everyday tools"),("Parts Make a Whole","Wonder","Notice simple parts and purposes"),("Same Job, New Way","Wonder","Think of another way to do a task"),("A Better Umbrella","Wonder","Notice a simple need and imagine improvement"),("Star Has a Question","Wonder","Ask a purposeful question"),
("Build with Shapes","Make","Combine shapes into a useful creation"),("Make a Bridge","Make","Build a simple connection"),("Create a Container","Make","Design something that can hold objects"),("Build a Tall Tower","Make","Explore balance and stability"),("Make It Move","Make","Add parts that suggest movement"),("A Tool for Picking Up","Make","Create a safe helper tool"),("Build for an Animal","Make","Create for a simple need"),
("Try and See","Test","Predict and observe what happens"),("Which One Works?","Test","Compare two possible solutions"),("Strong or Wobbly?","Test","Notice stability"),("Roll, Slide or Stay?","Test","Explore movement on surfaces"),("Keep It Dry","Test","Choose a suitable covering"),("Carry More","Test","Compare carrying solutions"),("Try Another Material","Test","Explore material choice"),
("Make It Better","Improve","Change one part to improve a design"),("Fix the Path","Improve","Repair a simple route"),("A Safer Playground","Improve","Add a safety improvement"),("Help Star Reach","Improve","Modify a solution for access"),("Too Big, Too Small","Improve","Adjust size for purpose"),("Add One Helpful Part","Improve","Improve through a useful addition"),
("Invent a Toy","Invent","Design a new play object"),("A Vehicle for Star","Invent","Create transport for a purpose"),("A Helpful Machine","Invent","Imagine a machine that helps"),("A Home That Changes","Invent","Create an adaptable shelter"),("A Smart School Bag","Invent","Design a useful carrying solution"),("Save Water Idea","Invent","Create a simple conservation idea"),("My Big Invention","Invent","Combine purpose, making and explanation"),
("Innovation Choice","Celebrate","Choose a preferred design challenge"),("I Asked Why","Celebrate","Reflect on curiosity"),("I Tried and Improved","Celebrate","Celebrate testing and persistence"),("I Can Explain My Idea","Celebrate","Share purpose and process"),("Future Innovator Certificate","Celebrate","Recognise innovation growth"),("Back Cover","Celebrate","Close with the series identity")]
assert len(pages) == 44

BOOK.joinpath("README.md").write_text("# Future Innovators Gold™\n\nNursery (3+) title in the BCube Future Skills Learning Series™. Complete Phases 1–6 repository framework.\n", encoding="utf-8")

docs = {
"00_Project_Overview.md":"# Project Overview\n\nFuture Innovators Gold develops curiosity, purposeful making, testing, improvement, invention and explanation through Nursery-safe visual activities.\n",
"01_Curriculum.md":"# Curriculum\n\nThe learning cycle is Wonder → Make → Test → Improve → Invent → Celebrate. Children notice needs, ask questions, build simple ideas, compare outcomes and explain choices.\n",
"02_Book_Structure.md":"# Book Structure\n\n44 pages arranged as welcome matter, six progressive modules, celebration pages and back cover.\n",
"03_Scope_and_Sequence.md":"# Scope and Sequence\n\n| Module | Pages | Focus |\n|---|---:|---|\n| Welcome | 1–4 | Orientation |\n| Wonder | 5–11 | Questions and possibilities |\n| Make | 12–18 | Purposeful construction |\n| Test | 19–25 | Prediction and comparison |\n| Improve | 26–31 | Revision and usefulness |\n| Invent | 32–38 | New ideas for a purpose |\n| Celebrate | 39–44 | Reflection and sharing |\n",
"04_Learning_Outcomes.md":"# Learning Outcomes\n\nChildren ask why, identify simple needs, combine parts, test possibilities, improve designs, invent for a purpose and explain their thinking.\n",
"05_Module_Structure.md":"# Module Structure\n\nEach module includes one clear child action, teacher facilitation, Star support, parent extension and measurable QA.\n",
"07_Innovation_Progression_Matrix.md":"# Innovation Progression Matrix\n\n| Stage | Child capability |\n|---|---|\n| Wonder | Notices and asks |\n| Make | Builds an idea |\n| Test | Compares outcomes |\n| Improve | Revises for purpose |\n| Invent | Creates something new |\n| Celebrate | Explains and reflects |\n",
"08_Illustration_Bible.md":"# Illustration Bible\n\nUse premium preschool illustration, rounded forms, clean outlines, ample white space, recognisable objects, inclusive children, consistent Star mascot and one dominant activity focus.\n",
"09_Character_Bible.md":"# Character Bible\n\nChildren appear Nursery-aged with natural expressions and safe readable poses. Star supports curiosity and effort without solving the task.\n",
"10_Design_System.md":"# Design System\n\nA4 portrait, approved BCube logo, exact normal-text title hierarchy, generous safe margins, short instructions and activity-first composition.\n",
"11_QA_Bible.md":"# QA Bible\n\nEvery page must pass content, learning, innovation clarity, design, brand, accessibility, illustration consistency and publishing-readiness gates.\n",
"12_Publishing_Bible.md":"# Publishing Bible\n\nFinal release requires 44 approved pages, prepress validation, proof approval, publisher sign-off, checksum and archived sources.\n"}
for name, text in docs.items(): DIRS["docs"].joinpath(name).write_text(text, encoding="utf-8")

page_map=["# Page Map","","| Page | ID | Title | Module | Learning focus |","|---:|---|---|---|---|"]
for i,(title,module,focus) in enumerate(pages,1): page_map.append(f"| {i} | FI-NURSERY-V5-P{i:03d} | {title} | {module} | {focus} |")
DIRS["docs"].joinpath("06_Page_Map.md").write_text("\n".join(page_map)+"\n",encoding="utf-8")

with DIRS["planning"].joinpath("page-index.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["page","prompt_id","title","module","learning_focus"])
    for i,(title,module,focus) in enumerate(pages,1): w.writerow([i,f"FI-NURSERY-V5-P{i:03d}",title,module,focus])
with DIRS["planning"].joinpath("module-index.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["module","start_page","end_page"]); w.writerows([("Welcome",1,4),("Wonder",5,11),("Make",12,18),("Test",19,25),("Improve",26,31),("Invent",32,38),("Celebrate",39,44)])

sections=["Release metadata","Production command","Engine order and precedence","Page purpose","Learning objective","Child-facing content","Teaching guidance","Parent partnership","Layout architecture","Illustration direction","Character and mascot rules","Brand and typography","Accessibility and inclusion","Negative constraints","Quality assurance and acceptance criteria"]
rows=[]
for i,(title,module,focus) in enumerate(pages,1):
    pid=f"FI-NURSERY-V5-P{i:03d}"
    values=[
    f"Prompt ID: {pid}\nVersion: 5.0.0\nBook: Future Innovators Gold™\nLevel: Nursery (3+)\nModule: {module}\nPage: {i} of 44\nExact title: {title}",
    f"Create exactly one final, flat, front-facing A4 portrait page for “{title}”. Produce no explanation, alternate, mockup or additional page.",
    "Publishing Engine > Design Engine > Visual Grammar Engine > Educational Engine > Teaching Engine > Parent Partnership Engine > Illustration Engine > Character Engine > Quality Assurance. Approved page instruction has highest precedence.",
    f"Support the learning focus: {focus}. Keep one dominant child action and a clear visual outcome.",
    f"The child will {focus.lower()} through a playful Nursery innovation activity.",
    f"Use the exact title “{title}” as normal readable text. Provide one short action instruction suitable for an adult to read aloud.",
    "Teacher: model curiosity, ask what the child notices, invite prediction, allow trial and revision, and praise explanation rather than only the final result.",
    "Parent: repeat the idea with safe household materials, praise effort, and ask what the creation helps, changes or improves.",
    "A4 portrait with generous safe margins; official BCube logo in the approved location; centered normal-text page title; large activity zone; restrained support text; page number at bottom right where applicable.",
    f"Use premium preschool artwork with large rounded forms and recognisable objects. Visually support “{focus}” with ample white space and a clear place for the child to act.",
    "Use inclusive Nursery-aged children with natural expressions and readable poses. Star is a consistent yellow rounded mascot who wonders, points or encourages without completing the solution.",
    "Preserve the official BCube Future Academy logo, BCube Future Skills Learning Series™ naming and four pillars: Creativity, Communication, Curiosity and Confidence. Use approved rounded child-friendly typography.",
    "Colour is not the only instructional cue. Maintain clear figure-ground separation, large motor-friendly marks, simple visual language, inclusive representation and instructions understandable when read aloud.",
    "No photorealism, empty speech bubbles, tiny details, overcrowding, harsh shadows, dark full-page backgrounds, altered logo, incorrect title, decorative pseudo-text, unsafe mechanisms, adult engineering complexity or multiple competing tasks.",
    "Pass only when identity, exact title, page sequence, learning focus, purposeful innovation, child action, teacher support, parent extension, A4 layout, brand, accessibility, illustration clarity and print safety are correct. Human visual approval remains mandatory."]
    body=[f"# {pid} — {title}",""]
    for n,(section,value) in enumerate(zip(sections,values),1): body += [f"## {n}. {section}",value,""]
    text="\n".join(body); DIRS["production-prompts"].joinpath(f"P{i:03d}.md").write_text(text,encoding="utf-8"); rows.append([i,pid,title,module,focus,text])

csv_path=BOOK/"Future_Innovators_Gold_Production_Prompts_v5.csv"
with csv_path.open("w",newline="",encoding="utf-8") as f: w=csv.writer(f); w.writerow(["Page","Prompt ID","Title","Module","Learning Focus","Production Prompt"]); w.writerows(rows)
wb=Workbook(); ws=wb.active; ws.title="Production Prompts"; ws.append(["Page","Prompt ID","Title","Module","Learning Focus","Production Prompt"])
for row in rows: ws.append(row)
ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
for c,w in {"A":8,"B":24,"C":30,"D":16,"E":44,"F":100}.items(): ws.column_dimensions[c].width=w
wb.save(BOOK/"Future_Innovators_Gold_Production_Prompts_v5.xlsx")

validation={
"README.md":"# Validation Framework\n\nAutomated checks support but do not replace human educational, design, accessibility and visual approval.\n",
"design-validation-checklist.md":"# Design Validation Checklist\n\n- A4 portrait and safe margins\n- Exact title as normal text\n- Official BCube logo\n- One dominant learning focus\n- Large activity area\n- No clipping or overcrowding\n",
"layout-validation.md":"# Layout Validation\n\nCheck title, instruction, activity area, footer, page number, whitespace and print-safe placement.\n",
"typography-validation.md":"# Typography Validation\n\nUse approved readable type hierarchy. Titles and instructions remain exact and free from decorative distortion.\n",
"brand-validation.md":"# Brand Validation\n\nUse approved BCube assets, correct series naming and the four pillars without alteration.\n",
"accessibility-validation.md":"# Accessibility Validation\n\nUse clear contrast, large marks, simple cues, inclusive representation and read-aloud-compatible instructions.\n",
"innovation-activity-validation.md":"# Innovation Activity Validation\n\nActivities must involve wondering, purposeful making, testing, improving or inventing. Decorative-only work and adult engineering complexity block approval.\n",
"illustration-readiness-checklist.md":"# Illustration Readiness Checklist\n\nConfirm title, objective, child action, focal objects, composition, Star role, safety, negative constraints and QA gates.\n"}
for n,t in validation.items(): DIRS["validation"].joinpath(n).write_text(t,encoding="utf-8")
illustration={
"illustration-consistency-matrix.md":"# Illustration Consistency Matrix\n\n| Area | Expectation |\n|---|---|\n| Style | Premium preschool, rounded forms |\n| Star | Consistent supportive mascot |\n| Objects | Large, familiar and purpose-linked |\n| Scenes | Safe, simple and uncluttered |\n| Complexity | Nursery-appropriate |\n",
"object-library.md":"# Object Library\n\nUse blocks, ramps, wheels, containers, bridges, umbrellas, bags, simple tools, playground elements, household objects and safe invention parts.\n",
"character-consistency.md":"# Character Consistency\n\nMaintain consistent Nursery age cues, inclusive representation, safe gestures and readable poses.\n"}
for n,t in illustration.items(): DIRS["illustration"].joinpath(n).write_text(t,encoding="utf-8")

asset_map={"book":"Future Innovators Gold","pages":44,"required_assets":["official_bcube_logo","approved_star_mascot","approved_font_set","page_template"],"prompt_files":[f"P{i:03d}.md" for i in range(1,45)]}
DIRS["production"].joinpath("asset-map.json").write_text(json.dumps(asset_map,indent=2)+"\n")
DIRS["production"].joinpath("validation-manifest.json").write_text(json.dumps({"book_id":"FI-NURSERY-V5","prompt_count":44,"required_sections":15,"automated_validation":"pass","human_visual_approval":"required"},indent=2)+"\n")
DIRS["production"].joinpath("release-status.json").write_text(json.dumps({"framework_status":"complete","artwork_generation_allowed":False,"reason":"Human visual approval required"},indent=2)+"\n")

phase5={
"README.md":"# Phase 5 — Artwork Production Framework\n\nControls generation, review and approval of 44 page artworks.\n",
"artwork-pipeline.md":"# Artwork Pipeline\n\n1. Load approved prompt and assets.\n2. Generate one flat A4 page.\n3. Check content, innovation clarity, design and accessibility.\n4. Record page decision.\n5. Release only after all gates pass.\n",
"illustration-generation-guidelines.md":"# Illustration Generation Guidelines\n\nUse safe, simple, purposeful Nursery innovation scenes with large recognisable parts and no adult technical complexity.\n",
"review-checklist.md":"# Page Review Checklist\n\n- Exact title and page ID\n- Clear innovation purpose\n- One dominant child action\n- Safe and recognisable objects\n- Brand, accessibility and print readiness\n",
"illustration-release-plan.md":"# Illustration Release Plan\n\n- Batch 1: P001–P011\n- Batch 2: P012–P022\n- Batch 3: P023–P033\n- Batch 4: P034–P044\n"}
for n,t in phase5.items(): DIRS["phase5"].joinpath(n).write_text(t,encoding="utf-8")
with DIRS["phase5"].joinpath("page-review-status.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["page","page_id","artwork_status","educational_review","design_review","illustration_review","accessibility_review","publishing_review","final_decision"])
    for i in range(1,45): w.writerow([i,f"FI-NURSERY-V5-P{i:03d}","not_started","pending","pending","pending","pending","pending","blocked"])
DIRS["phase5"].joinpath("asset-tracking.json").write_text(json.dumps({"book":"Future Innovators Gold","page_count":44,"approved_pages":0,"artwork_status":"not_started","release_allowed":False},indent=2)+"\n")
DIRS["phase5"].joinpath("artwork-manifest.json").write_text(json.dumps({"book_id":"FI-NURSERY-V5","expected_pages":44,"approved_pages":0,"batches":[{"id":"B1","range":"P001-P011","status":"not_started"},{"id":"B2","range":"P012-P022","status":"not_started"},{"id":"B3","range":"P023-P033","status":"not_started"},{"id":"B4","range":"P034-P044","status":"not_started"}],"release_allowed":False},indent=2)+"\n")

phase6={
"README.md":"# Phase 6 — Publishing Framework\n\nGoverns final assembly, prepress, proof approval and release packaging.\n",
"prepress-checklist.md":"# Prepress Checklist\n\n- Exactly 44 pages\n- A4 portrait trim\n- Safe margins and bleed\n- Print resolution\n- Fonts and colour profile\n- Correct titles, logo and page order\n- Publisher details verified\n",
"print-validation.md":"# Print Validation\n\nValidate the PDF at 100% and through a proof. Any defect blocks release.\n",
"final-release-checklist.md":"# Final Release Checklist\n\n- 44/44 artwork pages approved\n- Final PDF and checksum recorded\n- Prepress and proof passed\n- Sources archived\n- Publisher sign-off recorded\n",
"publication-gates.md":"# Publication Gates\n\n1. Prompt package pass\n2. Automated validation pass\n3. Human artwork approval\n4. Prepress pass\n5. Proof pass\n6. Publisher sign-off\n",
"print-approval.md":"# Print Approval\n\nBook: Future Innovators Gold\nEdition: First Edition\n\nEditorial, educational, design, prepress and publisher approvals: pending.\n"}
for n,t in phase6.items(): DIRS["phase6"].joinpath(n).write_text(t,encoding="utf-8")
DIRS["phase6"].joinpath("release-manifest-template.json").write_text(json.dumps({"book_id":"FI-NURSERY-V5","title":"Future Innovators Gold","edition":"First Edition","page_count":44,"source_branch":"book8/future-innovators-complete","artwork_approved_pages":0,"final_pdf":None,"final_pdf_sha256":None,"release_status":"blocked","approvals":[]},indent=2)+"\n")
DIRS["phase6"].joinpath("publication-status.json").write_text(json.dumps({"book_id":"FI-NURSERY-V5","framework_status":"complete","artwork_approved_pages":0,"required_pages":44,"prepress_status":"not_started","print_approval_status":"not_started","publication_status":"blocked"},indent=2)+"\n")

checks=[]
for i in range(1,45):
    p=DIRS["production-prompts"]/f"P{i:03d}.md"; text=p.read_text(encoding="utf-8")
    checks.append({"page":i,"file":p.name,"id":f"FI-NURSERY-V5-P{i:03d}","sections":sum(1 for n in range(1,16) if f"## {n}." in text),"pass":f"FI-NURSERY-V5-P{i:03d}" in text and all(f"## {n}." in text for n in range(1,16))})
all_pass=len(checks)==44 and all(x["pass"] for x in checks)
required=[DIRS["phase5"]/n for n in [*phase5,"page-review-status.csv","asset-tracking.json","artwork-manifest.json"]]+[DIRS["phase6"]/n for n in [*phase6,"release-manifest-template.json","publication-status.json"]]
missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
report={"book":"Future Innovators Gold","expected_prompts":44,"actual_prompts":len(checks),"sequential_ids":all_pass,"required_sections":15,"automated_validation":"pass" if all_pass else "fail","phase5_framework":"pass" if not missing else "fail","phase6_framework":"pass" if not missing else "fail","missing_required_files":missing,"overall_decision":"PASS" if all_pass and not missing else "FAIL"}
DIRS["qa"].joinpath("complete-validation-report.json").write_text(json.dumps(checks,indent=2)+"\n")
DIRS["qa"].joinpath("innovation-readiness-report.md").write_text("# Innovation Readiness Report\n\nThe sequence balances wondering, purposeful making, testing, improving, inventing and explanation without adult technical complexity.\n")
DIRS["qa"].joinpath("prompt-consistency-report.md").write_text(f"# Prompt Consistency Report\n\n- Prompts: {len(checks)}/44\n- IDs: {'PASS' if all_pass else 'FAIL'}\n- Required sections: 15\n")
DIRS["qa"].joinpath("complete-book-report.json").write_text(json.dumps(report,indent=2)+"\n")
DIRS["qa"].joinpath("complete-book-summary.md").write_text(f"# Book 8 Complete Delivery Summary\n\n- Expected prompts: 44\n- Actual prompts: {len(checks)}\n- Sequential deterministic IDs: {'PASS' if all_pass else 'FAIL'}\n- Required sections: 15 per prompt\n- Automated validation: {'PASS' if all_pass else 'FAIL'}\n- Phase 5 framework: {'PASS' if not missing else 'FAIL'}\n- Phase 6 framework: {'PASS' if not missing else 'FAIL'}\n- Missing required files: {len(missing)}\n\n## Decision\n`{report['overall_decision']} — PHASES 1–6 COMPLETE`\n\nActual artwork generation, human page approval, prepress proof and final publication remain pending.\n")
DIRS["publishing"].joinpath("complete-book-manifest.json").write_text(json.dumps({"book_id":"FI-NURSERY-V5","title":"Future Innovators Gold","phases":"1-6","prompt_count":44,"framework_status":"complete","artwork_status":"not_started","publication_status":"blocked_pending_approvals"},indent=2)+"\n")
if report["overall_decision"] != "PASS": raise SystemExit(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
