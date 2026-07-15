from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []

for path in sorted(ROOT.rglob("*.json")):
    try: json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")

for path in sorted(ROOT.rglob("*.yaml")):
    try: yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")

registry = yaml.safe_load((ROOT / "rules/master-rule-registry.yaml").read_text(encoding="utf-8"))
ids = [r["id"] for r in registry["rules"]]
if len(ids) != len(set(ids)): errors.append("Duplicate rule identifiers")
if not ids: errors.append("Rule registry is empty")

master = ROOT / "docs/BCube_Prompt_Engine_v3/BCube_Prompt_Engine_v3.md"
if not master.exists() or master.stat().st_size < 10000: errors.append("Master standard is missing or incomplete")

for path in ROOT.rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    for link in re.findall(r"\[[^]]+\]\((?!https?://|#)([^)]+)\)", text):
        target = (path.parent / link).resolve()
        if not target.exists(): errors.append(f"{path.relative_to(ROOT)}: broken link {link}")

if errors:
    print("\n".join(f"ERROR: {e}" for e in errors))
    sys.exit(1)
print(f"Validation passed: {len(ids)} rules; JSON, YAML, Markdown links, and master source verified.")
