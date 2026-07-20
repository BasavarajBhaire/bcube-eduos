#!/usr/bin/env python3
"""Create fail-closed brand/page lock registries without approving page artwork."""
import hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V4=ROOT/"BCube_Gold_Production_v4"
MANIFEST=V4/"manifests/nursery/communication-champions.release-v4.json"
BRAND_DIR=V4/"approved-assets/brand"
PAGE_DIR=V4/"approved-assets/nursery/communication-champions/pages"
SOURCE_LOGO=V4/"assets/nursery/communication-champions/P006/bcube-academy-logo.png"
LOGO=BRAND_DIR/"Official_BCube_Logo-v1.png"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

BRAND_DIR.mkdir(parents=True,exist_ok=True); PAGE_DIR.mkdir(parents=True,exist_ok=True)
if not LOGO.exists(): shutil.copy2(SOURCE_LOGO,LOGO)
brand={
 "lock_version":"1.0.0",
 "assets":{
  "official_logo":{"status":"approved","file":str(LOGO.relative_to(ROOT)),"sha256":sha(LOGO),"approved_by":"repository-migration","approved_at":"2026-07-20T00:00:00+05:30"},
  "star_mascot":{"status":"missing","file":None,"sha256":None,"approved_by":None,"approved_at":None,"requirements":"Transparent PNG; bright-yellow rounded five-point Star; expressive face; blue shoes; small blue cape."}
 }
}
brand_path=BRAND_DIR/"asset-lock.json"
if brand_path.exists():
    existing_brand=json.loads(brand_path.read_text())
    brand=existing_brand
else:
    brand_path.write_text(json.dumps(brand,indent=2)+"\n")

manifest=json.loads(MANIFEST.read_text())
page_assets={}
for job in manifest["jobs"]:
    page_assets[job["asset_lock_id"]]={
      "status":"missing","file":None,"sha256":None,"approved_by":None,"approved_at":None,
      "source_package_version":None,
      "notes":"Must be explicitly promoted from a reviewed candidate; release builds may not generate or substitute this page."
    }
lock={"lock_version":"1.0.0","book_id":manifest["book_id"],"brand_assets":brand["assets"],"page_assets":page_assets}
lock_path=V4/"approved-assets/nursery/communication-champions/asset-lock.json"
lock_path.parent.mkdir(parents=True,exist_ok=True)
if lock_path.exists():
    existing=json.loads(lock_path.read_text())
    changed=False
    for pid,entry in page_assets.items():
        if pid not in existing["page_assets"]:
            existing["page_assets"][pid]=entry; changed=True
    if changed:
        lock_path.write_text(json.dumps(existing,indent=2)+"\n")
        print(f"Extended existing lock without changing approvals: {lock_path}")
    else:
        print(f"Preserved existing lock: {lock_path}")
else:
    lock_path.write_text(json.dumps(lock,indent=2)+"\n")
print(lock_path)
