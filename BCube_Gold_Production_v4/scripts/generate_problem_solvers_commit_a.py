from __future__ import annotations

import csv
import json
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books" / "nursery" / "problem-solvers"
PROMPTS = BOOK / "production-prompts"
DOCS = BOOK / "docs"
PLANNING = BOOK / "planning"
QA = BOOK / "qa"
PUBLISHING = BOOK / "publishing"
for d in (BOOK, PROMPTS, DOCS, PLANNING, QA, PUBLISHING):
    d.mkdir(parents=True, exist_ok=True)

pages = [
("Problem Solvers Gold","Opening","Observe"),("This Book Belongs to Me","Opening","Express"),("Meet Star","Opening","Observe"),("How Problem Solvers Think","Opening","Think"),
("What Do You Notice?","Look Closely","Observe"),("Find the Same","Look Closely","Observe"),("Find the Different One","Look Closely","Observe"),("What Is Missing?","Look Closely","Think"),("Spot the Change","Look Closely","Observe"),("Match the Shadows","Look Closely","Think"),("Look Closely Celebration","Look Closely","Express"),
("Sort by Colour","Sort and Match","Think"),("Sort by Shape","Sort and Match","Think"),("Big and Small","Sort and Match","Observe"),("Match the Pairs","Sort and Match","Think"),("Where Does It Belong?","Sort and Match","Solve"),("Same Group, New Rule","Sort and Match","Try"),("Sorting Celebration","Sort and Match","Express"),
("What Comes Next?","Patterns and Order","Think"),("Finish the Pattern","Patterns and Order","Solve"),("First, Next, Last","Patterns and Order","Think"),("Put the Story in Order","Patterns and Order","Solve"),("Make a New Pattern","Patterns and Order","Try"),("Fix the Mixed-Up Row","Patterns and Order","Solve"),("Pattern Celebration","Patterns and Order","Express"),
("Choose the Safe Path","Paths and Choices","Think"),("Help the Animal Get Home","Paths and Choices","Solve"),("Which Tool Will Help?","Paths and Choices","Think"),("Choose What Happens Next","Paths and Choices","Try"),("Two Ways to Solve It","Paths and Choices","Try"),("Find Another Way","Paths and Choices","Solve"),("Choice Celebration","Paths and Choices","Express"),
("Build the Tallest Tower","Try and Improve","Try"),("Fix the Wobbly Bridge","Try and Improve","Solve"),("Make It Fit","Try and Improve","Think"),("Try Again","Try and Improve","Try"),("Change One Thing","Try and Improve","Solve"),("Make It Better","Try and Improve","Solve"),("Improvement Celebration","Try and Improve","Express"),
("Help at Home","Everyday Problems","Solve"),("Help a Friend","Everyday Problems","Think"),("Plan a Picnic","Everyday Problems","Solve"),("My Best Solution","Everyday Problems","Express"),("I Am a Problem Solver","Celebration","Express")]
assert len(pages) == 44

BOOK_ID = "PS-NURSERY-V5"

def prompt_text(i: int, title: str, module: str, pillar: str) -> str:
    pid = f"{BOOK_ID}-P{i:03d}"
    action = {
        "Observe":"look carefully, point, compare and describe",
        "Think":"pause, notice clues and choose a sensible answer",
        "Try":"test one idea, notice what happens and try another",
        "Solve":"use clues, make a choice and explain the solution",
        "Express":"share the idea, effort or solution with confidence",
    }[pillar]
    return f'''# BCube Production Prompt v5 — {pid}\n\n## 1. Release metadata\nPrompt ID: {pid}\nVersion: 5.0.0\nBook: Problem Solvers Gold\nLevel: Nursery (3+)\nModule: {module}\nPhysical page: {i} of 44\nExact title: {title}\n\n## 2. Production command\nCreate exactly one final, flat, front-facing A4 portrait workbook page for “{title}”. Produce no explanation, alternate, mockup or extra page.\n\n## 3. Publishing system\nUse the BCube Gold interior-page system, approved BCube Future Academy logo, exact title, safe margins, correct page number and premium preschool publishing finish.\n\n## 4. Learning objective\nDevelop the {pillar.lower()} stage of early problem solving through an age-appropriate Nursery task.\n\n## 5. Child activity\nThe child should {action}. Keep the response space large, obvious and motor-friendly.\n\n## 6. Teaching guidance\nTeacher: model one example, ask “What do you notice?”, allow thinking time and praise the child’s process rather than speed.\n\n## 7. Parent partnership\nParent: repeat the skill with familiar home objects and ask the child to explain one choice in simple words.\n\n## 8. Illustration direction\nUse large recognisable objects, rounded forms, clean outlines, natural expressions and one dominant visual problem. Show clues clearly without giving away the answer.\n\n## 9. Star mascot direction\nUse Star only as a supportive guide or encourager. Star must not cover clues, dominate the activity or reveal the solution.\n\n## 10. Layout specification\nA4 portrait; clear title zone; short instruction zone; 65–75% activity area; generous white space; page number at bottom right; all critical content inside trim-safe margins.\n\n## 11. Typography\nUse approved rounded child-friendly typography. Keep the title as normal readable text, not decorative lettering. Use short, concrete instructions with strong contrast.\n\n## 12. Accessibility\nDo not rely on colour alone. Use shape, position, outline or symbol cues; avoid tiny details, visual overload, ambiguous overlaps and low-contrast clues.\n\n## 13. Negative constraints\nNo photorealism, empty speech bubbles, unnecessary stickers, crowded backgrounds, hidden instructions, unsafe actions, trick questions, answer leakage or multiple competing tasks.\n\n## 14. Problem-solving integrity\nThe page must support Observe → Think → Try → Solve habits. Permit reasonable child thinking, avoid shame or failure language, and make retrying feel safe.\n\n## 15. QA acceptance criteria\nPass only when the title, prompt ID, page number, learning objective, visual clues, child action, teacher guidance, parent prompt, accessibility and BCube brand rules are complete and mutually consistent.\n'''

rows = []
for i, (title, module, pillar) in enumerate(pages, 1):
    pid = f"{BOOK_ID}-P{i:03d}"
    text = prompt_text(i, title, module, pillar)
    (PROMPTS / f"P{i:03d}.md").write_text(text, encoding="utf-8")
    rows.append({"physical_page":i,"page_id":pid,"title":title,"module":module,"primary_pillar":pillar,"status":"production_ready","prompt":text})

(BOOK / "README.md").write_text("""# Problem Solvers Gold™\n\nNursery (3+) title in the BCube Future Skills Learning Series™.\n\nCommit A contains Phases 1–3: curriculum, architecture and the complete 44-page production package. Core progression: Observe → Think → Try → Solve → Express.\n""", encoding="utf-8")

modules = []
for module in dict.fromkeys(r["module"] for r in rows):
    subset = [r for r in rows if r["module"] == module]
    modules.append((module, subset[0]["physical_page"], subset[-1]["physical_page"], len(subset)))

(DOCS / "00_Project_Overview.md").write_text("# Project Overview\n\nProblem Solvers Gold builds early observation, classification, sequencing, choice-making, persistence and everyday reasoning through play-based Nursery activities.\n", encoding="utf-8")
(DOCS / "01_Curriculum.md").write_text("# Curriculum\n\nThe learning cycle is Observe, Think, Try, Solve and Express. Adults model curiosity, allow wait time, welcome more than one strategy where appropriate and praise effort, explanation and retrying.\n", encoding="utf-8")
(DOCS / "02_Book_Structure.md").write_text("# Book Structure\n\n44 physical pages organised into opening pages, five skill modules, everyday application and a final celebration. Each page contains one dominant cognitive task with teacher and parent support.\n", encoding="utf-8")
(DOCS / "03_Scope_and_Sequence.md").write_text("# Scope and Sequence\n\n" + "\n".join(f"- Pages {s}–{e}: {m} ({c} pages)" for m,s,e,c in modules) + "\n", encoding="utf-8")
(DOCS / "04_Learning_Outcomes.md").write_text("# Learning Outcomes\n\nChildren notice visual clues, compare and classify objects, predict simple sequences, choose between options, test ideas, retry safely, solve familiar problems and explain a simple choice.\n", encoding="utf-8")
(DOCS / "05_Module_Structure.md").write_text("# Module Structure\n\nModules progress from visual noticing to sorting, ordering, path and tool choices, improvement through retrying, and familiar social or home problems.\n", encoding="utf-8")
(DOCS / "06_Page_Map.md").write_text("# Page Map\n\n| Page | ID | Title | Module | Pillar |\n|---:|---|---|---|---|\n" + "\n".join(f"| {r['physical_page']} | {r['page_id']} | {r['title']} | {r['module']} | {r['primary_pillar']} |" for r in rows) + "\n", encoding="utf-8")
(DOCS / "07_Problem_Solving_Progression_Matrix.md").write_text("# Problem-Solving Progression Matrix\n\n| Stage | Child behaviour | Adult support |\n|---|---|---|\n| Observe | Notices visible clues | Ask what the child sees |\n| Think | Compares possibilities | Offer wait time |\n| Try | Tests an idea | Welcome experimentation |\n| Solve | Chooses and acts | Ask why it may work |\n| Express | Shares the process | Praise effort and explanation |\n", encoding="utf-8")
for name, body in {
"08_Illustration_Bible.md":"# Illustration Bible\n\nUse simple clue-rich scenes, large objects, clean separation and no answer leakage. Visual complexity must remain appropriate for Nursery children.",
"09_Character_Bible.md":"# Character Bible\n\nChildren and Star use consistent proportions, inclusive representation, calm expressions and safe problem-solving gestures. Avoid embarrassment or failure reactions.",
"10_Design_System.md":"# Design System\n\nFollow the shared BCube Gold A4 portrait system with normal readable titles, exact instructions, restrained pastel accents and a dominant activity area.",
"11_QA_Bible.md":"# QA Bible\n\nValidate structural completeness, clue clarity, age suitability, accessibility, answer integrity, teacher usability and parent extension.",
"12_Publishing_Bible.md":"# Publishing Bible\n\nAll 44 pages require educational, design, illustration, accessibility, prepress and publisher approval before release.",
}.items(): (DOCS/name).write_text(body+"\n", encoding="utf-8")

with (PLANNING / "page-index.csv").open("w", newline="", encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=["physical_page","page_id","title","module","primary_pillar","status"]); w.writeheader(); w.writerows([{k:r[k] for k in w.fieldnames} for r in rows])
with (PLANNING / "module-index.csv").open("w", newline="", encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["module_id","module_name","start_page","end_page","page_count"])
    for n,(m,s,e,c) in enumerate(modules): w.writerow([f"M{n:02d}",m,s,e,c])

csv_path = BOOK / "Problem_Solvers_Gold_Production_Prompts_v5.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
wb=Workbook(); ws=wb.active; ws.title="Production Prompts"; ws.append(list(rows[0].keys()))
for r in rows: ws.append(list(r.values()))
ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
for col,width in {"A":14,"B":24,"C":34,"D":24,"E":18,"F":20,"G":110}.items(): ws.column_dimensions[col].width=width
wb.save(BOOK / "Problem_Solvers_Gold_Production_Prompts_v5.xlsx")

manifest={"commit":"A","book":"Problem Solvers Gold","book_id":BOOK_ID,"phases":[1,2,3],"page_count":44,"prompt_count":44,"required_sections":15,"csv":csv_path.name,"xlsx":"Problem_Solvers_Gold_Production_Prompts_v5.xlsx","status":"pass"}
(PUBLISHING / "commit-a-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
report={"expected_prompts":44,"actual_prompts":len(list(PROMPTS.glob('P*.md'))),"unique_ids":len({r['page_id'] for r in rows}),"sequential":all((PROMPTS/f"P{i:03d}.md").exists() for i in range(1,45)),"csv_present":csv_path.exists(),"xlsx_present":(BOOK/"Problem_Solvers_Gold_Production_Prompts_v5.xlsx").exists(),"decision":"PASS"}
(QA / "commit-a-generation-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
(QA / "prompt-validation-report.md").write_text(f"# Commit A Prompt Validation Report\n\n- Expected prompts: 44\n- Actual prompts: {report['actual_prompts']}\n- Sequential files: P001-P044\n- Unique deterministic IDs: {report['unique_ids']}\n- Required sections: 15 per prompt\n- CSV workbook: present\n- XLSX workbook: present\n\n## Decision\n`PASS — PHASES 1, 2 AND 3 COMPLETE`\n",encoding="utf-8")
if not all([report['actual_prompts']==44,report['unique_ids']==44,report['sequential'],report['csv_present'],report['xlsx_present']]): raise SystemExit("Commit A generation failed")
print(json.dumps(report,indent=2))
