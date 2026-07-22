from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []

for path in sorted(ROOT.rglob("*.json")):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")

for path in sorted(ROOT.rglob("*.yaml")):
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")

registry = yaml.safe_load((ROOT / "rules/master-rule-registry.yaml").read_text(encoding="utf-8"))
ids = [r["id"] for r in registry["rules"]]
if len(ids) != len(set(ids)):
    errors.append("Duplicate rule identifiers")
if not ids:
    errors.append("Rule registry is empty")

master = ROOT / "docs/BCube_Prompt_Engine_v3/BCube_Prompt_Engine_v3.md"
if not master.exists() or master.stat().st_size < 10000:
    errors.append("Master standard is missing or incomplete")

for path in ROOT.rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    for link in re.findall(r"\[[^]]+\]\((?!https?://|#)([^)]+)\)", text):
        target = (path.parent / link).resolve()
        if not target.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link {link}")

# Global publishing fail-closed policy.
production_lock = ROOT / "BCube_Gold_Production_v4/GLOBAL_PAGE_PRODUCTION_LOCK.md"
production_policy = ROOT / "rules/global-page-production-lock.json"

if not production_lock.is_file():
    errors.append("Global page production lock is missing")
else:
    lock_text = production_lock.read_text(encoding="utf-8")
    required_lock_tokens = [
        "MANDATORY — FAIL CLOSED",
        "Communication Champions",
        "official BCube logo",
        "approved Star",
        "Generate or source only the illustration layer",
        "deterministic editable text layers",
        "one flat, front-facing print page",
        "No book may opt out",
    ]
    for token in required_lock_tokens:
        if token not in lock_text:
            errors.append(f"Global page production lock is missing required rule: {token}")

if not production_policy.is_file():
    errors.append("Machine-readable global page production policy is missing")
else:
    try:
        policy = json.loads(production_policy.read_text(encoding="utf-8"))
        if policy.get("status") != "MANDATORY_FAIL_CLOSED":
            errors.append("Global page production policy is not fail-closed")
        if policy.get("approved_baseline") != "Communication Champions finalized production method plus merged V4 page architecture":
            errors.append("Global page production policy baseline changed")
        if policy.get("asset_locks", {}).get("official_logo", {}).get("generation_allowed") is not False:
            errors.append("Official logo generation must remain prohibited")
        if policy.get("asset_locks", {}).get("approved_star", {}).get("generation_allowed") is not False:
            errors.append("Approved Star generation must remain prohibited")
        if policy.get("typography_lock", {}).get("image_model_text_allowed") is not False:
            errors.append("Image-model page typography must remain prohibited")
        if policy.get("publishing_lock", {}).get("one_physical_page_per_output") is not True:
            errors.append("One physical page per output must remain mandatory")
        if policy.get("publishing_lock", {}).get("poster_or_infographic_substitution_allowed") is not False:
            errors.append("Poster or infographic substitution must remain prohibited")
        if policy.get("acceptance", {}).get("critical_defects") != 0:
            errors.append("Global page production acceptance must require zero critical defects")
    except Exception as exc:
        errors.append(f"Global page production policy cannot be validated: {exc}")

if errors:
    print("\n".join(f"ERROR: {e}" for e in errors))
    sys.exit(1)
print(
    f"Validation passed: {len(ids)} rules; JSON, YAML, Markdown links, master source, "
    "and global page production lock verified."
)
