#!/usr/bin/env python3
"""Smoke tests for the fail-closed deterministic release framework."""
import json, subprocess, sys
from pathlib import Path

V4=Path(__file__).resolve().parents[1]
PY=sys.executable
def run(*args): return subprocess.run(args,cwd=V4,text=True,capture_output=True)

manifest=json.loads((V4/"manifests/nursery/communication-champions.release-v4.json").read_text())
assert manifest["total_packages"]==44
assert [j["production_position"] for j in manifest["jobs"]]==list(range(1,45))
assert [j["prompt_id"] for j in manifest["jobs"]]==[f"CC-NURSERY-V4-P{i:03d}" for i in range(1,45)]
assert manifest["jobs"][-1]["page_role"]=="back_cover"
assert manifest["jobs"][-1]["logical_page_number"] is None
assert manifest["jobs"][-1]["printed_number_visible"] is False

r=run(PY,"scripts/validate-deterministic-release.py","--mode","manifest")
assert r.returncode==0, r.stdout+r.stderr
r=run(PY,"scripts/validate-deterministic-release.py","--mode","release")
assert r.returncode!=0 and "REJECTED" in r.stdout, "incomplete approvals must fail closed"
r=run(PY,"scripts/build-deterministic-release.py","--release-id","SHOULD-NOT-BUILD")
assert r.returncode!=0, "builder must not bypass release validation"
print("PASS: canonical 44-page physical mapping; back cover unnumbered; incomplete assets fail closed; build cannot bypass validation")
