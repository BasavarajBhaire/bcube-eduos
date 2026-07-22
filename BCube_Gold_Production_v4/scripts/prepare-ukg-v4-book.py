#!/usr/bin/env python3
"""Generate the UKG V4 compiler from the approved LKG compiler architecture.

The transformation is deterministic and idempotent. It keeps the proven 44-page
publishing, source-lineage, manifest and fail-closed QA framework while applying
the official UKG catalogue, UKG developmental rules and controlled closing-page
corrections.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "build-lkg-v4-prompts.py"
TARGET = HERE / "build-ukg-v4-prompts.py"

text = SOURCE.read_text(encoding="utf-8")

books_block = '''BOOKS = {
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
ORDER = list(BOOKS)'''

text, count = re.subn(
    r"BOOKS = \{.*?\n\}\nORDER = list\(BOOKS\)",
    books_block,
    text,
    count=1,
    flags=re.DOTALL,
)
if count != 1:
    raise SystemExit("Unable to replace the LKG catalogue with the UKG catalogue")

start_marker = '            if slug == "early-literacy-adventures"'
end_marker = '            if physical == 1:'
start = text.find(start_marker)
end = text.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("Unable to locate the LKG closing-correction block")

correction_block = r'''            # V4 controlled UKG closing-source correction registry
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
'''
text = text[:start] + correction_block + text[end:]

# Apply the UKG identity and repository paths.
text = text.replace("LKG", "UKG")
text = text.replace('"lkg"', '"ukg"')
text = text.replace("lkg-v4-prompts-validation.json", "ukg-v4-prompts-validation.json")

# Apply the UKG developmental and visual grammar rules.
text = text.replace("UKG (4+)", "UKG (5+)")
text = text.replace("60–70% visual", "55–65% visual")
text = text.replace("30–40% text/activity", "35–45% text/activity")
text = text.replace("generally 3–8 familiar words", "generally 4–10 familiar words")
text = text.replace(
    "Use short tracing/copying only; use adult support for personal or open responses.",
    "Use short independent reading/writing and simple sentences; provide adult support where the approved source requires it.",
)
text = text.replace(
    "short tracing/copying only; adult-supported open response",
    "short independent reading/writing; simple sentences; adult support where needed",
)
text = text.replace(
    "Progression: recognition and oral response → guided tracing/copying/sequencing → simple supported independent response.",
    "Progression: guided recall and oral explanation → short independent reading/writing/sequencing → simple reasoning, problem solving, and Grade 1-ready response.",
)
text = text.replace(
    "Story pages use only 3–4 clear picture steps unless the approved source explicitly requires otherwise.",
    "Story and sequence pages use 4–5 clear steps unless the approved source explicitly requires otherwise.",
)
text = text.replace("Lessons carried forward from Nursery", "Lessons carried forward from Nursery and LKG")

TARGET.write_text(text, encoding="utf-8")
print(f"Prepared {TARGET.relative_to(HERE.parents[2])}")
