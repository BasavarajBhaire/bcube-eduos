#!/usr/bin/env python3
"""Apply audited, idempotent LKG V4 source-normalisation rules before compilation."""
from pathlib import Path

COMPILER = Path(__file__).with_name("build-lkg-v4-prompts.py")
text = COMPILER.read_text(encoding="utf-8")
changed = False

old_profile = '''    "stem-explorers": {
        "book": "STEM Explorers",
        "prefix": "SE",'''
new_profile = '''    "stem-explorers": {
        "book": "STEM Explorers",
        "prefix": "ST",'''
if old_profile in text:
    text = text.replace(old_profile, new_profile, 1)
    changed = True
elif new_profile not in text:
    raise SystemExit("Unable to resolve the canonical STEM prefix")

registry_marker = "# V4 controlled closing-source correction registry"
if registry_marker not in text:
    insertion_marker = '''            if physical == 1:
                fields["title"] = book
                fields["page_type"] = "cover"
'''
    if text.count(insertion_marker) != 1:
        raise SystemExit("Unable to locate the LKG compiler correction insertion point")

    correction_block = r'''            # V4 controlled closing-source correction registry
            closing_corrections = {
                ("stem-explorers", "ST-LKG-V3-P041"): {
                    "title": "My STEM Celebration",
                    "objective": "Reflect on and celebrate STEM learning.",
                    "instruction": "Share one observation, prediction, investigation, or solution from this book.",
                    "evidence": "I discovered that ______.",
                    "question": "What STEM discovery are you proud of?",
                    "home": "Safely demonstrate one favourite observation or investigation using familiar home materials.",
                    "conversation": "I discovered that ______.",
                    "scene": "Teacher-led STEM celebration where children share one observation, prediction, model, or solution.",
                    "focal": "Children confidently explaining one STEM discovery with simple evidence.",
                },
                ("creativity-challenges", "CR-LKG-V3-P041"): {
                    "title": "My Creative Celebration",
                    "objective": "Reflect on and celebrate original ideas and creative expression.",
                    "instruction": "Show or describe one idea, design, story, or artwork you created.",
                    "evidence": "I created ______ because ______.",
                    "question": "Which creative idea are you proud of?",
                    "home": "Choose one safe everyday material and create something new together.",
                    "conversation": "I created ______ because ______.",
                    "scene": "Teacher-led creativity celebration with children presenting different original ideas and artwork.",
                    "focal": "Every child confidently sharing one unique creative choice.",
                },
                ("my-world-general-awareness", "MW-LKG-V3-P041"): {
                    "title": "My World Celebration",
                    "objective": "Reflect on and celebrate learning about self, community, nature and the wider world.",
                    "instruction": "Choose one thing you learned about your world and explain it.",
                    "evidence": "I learned that ______.",
                    "question": "What new thing do you know about your world?",
                    "home": "Notice one person, place, plant, animal or community feature and talk about it together.",
                    "conversation": "I learned that ______.",
                    "scene": "Teacher-led world-awareness celebration with children sharing discoveries about people, places and nature.",
                    "focal": "Children connecting one clear discovery to their everyday world.",
                },
                ("healthy-habits-safety", "HH-LKG-V3-P041"): {
                    "title": "Healthy & Safe Celebration",
                    "objective": "Reflect on and celebrate healthy and safe choices.",
                    "instruction": "Show or explain one healthy or safe habit you can use every day.",
                    "evidence": "I stay healthy and safe when I ______.",
                    "question": "Which healthy or safe habit will you keep practising?",
                    "home": "Practise the chosen habit together during one familiar home routine.",
                    "conversation": "I stay healthy and safe when I ______.",
                    "scene": "Teacher-led celebration where children demonstrate simple hygiene, movement, nutrition and safety habits.",
                    "focal": "Children confidently demonstrating one practical healthy or safe behaviour.",
                },
                ("art-colour-fun", "AC-LKG-V3-P041"): {
                    "title": "My Art Celebration",
                    "objective": "Reflect on and celebrate artistic exploration and personal expression.",
                    "instruction": "Show or describe one artwork, colour choice, pattern or technique you enjoyed.",
                    "evidence": "My artwork shows ______.",
                    "question": "What do you like most about your artwork?",
                    "home": "Create together using safe art materials already available at home.",
                    "conversation": "My artwork shows ______.",
                    "scene": "Teacher-led gallery celebration with children presenting varied artwork and explaining one artistic choice.",
                    "focal": "Each child proudly explaining one personal art choice.",
                },
                ("confidence-social-skills", "CS-LKG-V3-P041"): {
                    "title": "I Am Confident and Kind",
                    "objective": "Reinforce confidence, kindness and positive social behaviour.",
                    "instruction": "Choose one confident or kind action you can use with others.",
                    "evidence": "I can ______ to be confident and kind.",
                    "question": "How will you show confidence and kindness?",
                    "home": "Practise the chosen confident or kind action during one familiar family routine.",
                    "conversation": "I can ______ to be confident and kind.",
                    "scene": "Teacher-led social-skills celebration with children demonstrating speaking up, helping, listening and respecting space.",
                    "focal": "Children confidently choosing and explaining one kind social action.",
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
                    "questions": [correction["question"]],
                    "home": correction["home"],
                    "conversation": correction["conversation"],
                    "scene": correction["scene"],
                    "focal": correction["focal"],
                })
                fields["overrides"] = list(fields.get("overrides", [])) + [
                    "V4 editorial correction: source metadata labels this page as Back Cover while its approved content requires a child response, teacher facilitation, evidence and parent extension. Render the source-backed celebration on printed page 42, preserve source lineage and educational intent, and keep physical page 44 as the only true back cover."
                ]
                fields["approved_source_instruction"] += (
                    "\n\nV4 EDITORIAL CORRECTION: Use the exact corrected celebration title and response defined by the controlled LKG correction registry. Preserve the source-backed educational intent, teacher and parent partnership, illustration constraints and complete lineage. Physical page 44 is the only true back cover."
                )
            if physical == 1:
                fields["title"] = book
                fields["page_type"] = "cover"
'''
    text = text.replace(insertion_marker, correction_block, 1)
    changed = True

if changed:
    COMPILER.write_text(text, encoding="utf-8")
print("LKG V4 preparation complete")
