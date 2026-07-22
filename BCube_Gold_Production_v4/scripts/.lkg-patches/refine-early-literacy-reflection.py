#!/usr/bin/env python3
"""Refine the audited Early Literacy closing reflection correction in the reusable LKG compiler."""
from pathlib import Path

path = Path("BCube_Gold_Production_v4/scripts/build-lkg-v4-prompts.py")
text = path.read_text(encoding="utf-8")
old = '''                fields.update({
                    "title": "My Literacy Celebration",
                    "page_type": "reflection",
                    "objective": "Reflect on and celebrate literacy learning.",
                    "scene": "Teacher-led literacy celebration with six expressive LKG children and approved Star; each child shares one short literacy reflection.",
                    "focal": "Children confidently sharing one reading or literacy achievement with their teacher and classmates.",
                })
'''
new = '''                fields.update({
                    "title": "My Literacy Celebration",
                    "page_type": "reflection",
                    "objective": "Reflect on and celebrate literacy learning.",
                    "instruction": "Share one literacy skill you learned. Complete one short speaking, reflection, or independent practice response.",
                    "evidence": "I am proud that I can ______.",
                    "questions": ["What literacy skill are you proud of?"],
                    "home": "Invite the child to choose a favourite letter, word, or story and explain why.",
                    "conversation": "I am proud that I can ______.",
                    "scene": "Teacher-led literacy celebration with six expressive LKG children and approved Star; each child shares one short literacy reflection.",
                    "focal": "Children confidently sharing one reading or literacy achievement with their teacher and classmates.",
                })
'''
if old not in text:
    if new in text:
        raise SystemExit(0)
    raise RuntimeError("Early Literacy correction block not found")
text = text.replace(old, new, 1)
text = text.replace(
    "preserve its activity, evidence, facilitation, parent connection, illustration intent, and source lineage.",
    "preserve its reflection intent, facilitation, illustration intent, and source lineage while replacing contradictory placeholder wording with an exact literacy reflection response.",
    1,
)
path.write_text(text, encoding="utf-8")
