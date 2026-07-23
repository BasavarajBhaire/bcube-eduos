#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
runner = ROOT / "scripts/run_bcube_cover_pipeline.py"
text = runner.read_text(encoding="utf-8")
old = 'COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_nursery_cover.py"'
new = 'COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_nursery_cover_strict.py"'
if old not in text and new not in text:
    raise SystemExit("Expected COMPOSER declaration not found")
runner.write_text(text.replace(old, new), encoding="utf-8")

template_path = ROOT / "bcube-publishing-sdk/templates/nursery-cover-v1.json"
template = json.loads(template_path.read_text(encoding="utf-8"))
template["template_id"] = "BCUBE-NURSERY-COVER-V1.3"
template.setdefault("rules", {})["illustration_safe_inset"] = 20
template["rules"]["illustration_min_occupancy_ratio"] = 0.70
template["rules"]["illustration_vertical_align"] = "bottom"
template["rules"]["illustration_trim_near_white"] = True
template_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
