#!/usr/bin/env python3
from pathlib import Path

files = [
    Path('BCube_Gold_Production_v4/scripts/build-lkg-v4-prompts.py'),
    Path('BCube_Gold_Production_v4/scripts/prepare-lkg-v4-book.py'),
]

for path in files:
    text = path.read_text(encoding='utf-8')
    old_entry = '''                    "question": "How will you show confidence and kindness?",
                    "home": "Practise the chosen confident or kind action during one familiar family routine.",'''
    new_entry = '''                    "question": "How will you show confidence and kindness?",
                    "teacher": "Model one confident or kind action, invite a child response, and affirm effort.",
                    "home": "Practise the chosen confident or kind action during one familiar family routine.",'''
    if old_entry in text:
        text = text.replace(old_entry, new_entry, 1)
    elif new_entry not in text:
        raise SystemExit(f'Unable to patch confidence teacher entry in {path}')

    old_mapping = '''                    "evidence": correction["evidence"],
                    "questions": [correction["question"]],'''
    new_mapping = '''                    "evidence": correction["evidence"],
                    "teacher": correction.get("teacher", fields.get("teacher", "")),
                    "questions": [correction["question"]],'''
    if old_mapping in text:
        text = text.replace(old_mapping, new_mapping, 1)
    elif new_mapping not in text:
        raise SystemExit(f'Unable to patch correction mapping in {path}')

    path.write_text(text, encoding='utf-8')
