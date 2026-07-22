#!/usr/bin/env python3
from pathlib import Path

path = Path('BCube_Gold_Production_v4/scripts/prepare-lkg-v4-book.py')
text = path.read_text(encoding='utf-8')
old = "    correction_block = '''            # V4 controlled closing-source correction registry"
new = "    correction_block = r'''            # V4 controlled closing-source correction registry"
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('Unable to locate correction_block string declaration')
path.write_text(text, encoding='utf-8')
