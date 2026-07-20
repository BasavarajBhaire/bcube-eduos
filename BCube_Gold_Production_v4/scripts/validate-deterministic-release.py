#!/usr/bin/env python3
"""Fail-closed validation for canonical identity, immutable assets, and release geometry."""
import argparse, hashlib, json, re, sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
V4=ROOT/"BCube_Gold_Production_v4"
DEFAULT_MANIFEST=V4/"manifests/nursery/communication-champions.release-v4.json"
DEFAULT_LOCK=V4/"approved-assets/nursery/communication-champions/asset-lock.json"
TEMPLATES=V4/"templates/template-registry.v1.json"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def fail(errors,msg): errors.append(msg)

def validate_manifest(manifest, errors):
    jobs=manifest.get("jobs",[])
    if manifest.get("release_mode")!="approved-assets-only": fail(errors,"release_mode must be approved-assets-only")
    if manifest.get("total_packages")!=44 or len(jobs)!=44: fail(errors,"manifest must contain exactly 44 packages")
    seen=set()
    templates=json.loads(TEMPLATES.read_text()).get("templates",{})
    for expected,job in enumerate(jobs,1):
        prefix=f"job P{expected:03d}"
        if job.get("production_position")!=expected: fail(errors,f"{prefix}: non-sequential production position")
        expected_id=f"CC-NURSERY-V4-P{expected:03d}"
        if job.get("prompt_id")!=expected_id: fail(errors,f"{prefix}: prompt id must be {expected_id}")
        if job.get("prompt_id") in seen: fail(errors,f"{prefix}: duplicate prompt id")
        seen.add(job.get("prompt_id"))
        is_cover=expected in (1,44)
        logical=None if is_cover else expected-1
        visible=6<=expected<=43
        if job.get("logical_page_number")!=logical: fail(errors,f"{prefix}: logical page must be {logical}")
        if job.get("printed_number_visible") is not visible: fail(errors,f"{prefix}: printed visibility must be {visible}")
        if job.get("template_id") not in templates: fail(errors,f"{prefix}: unknown template {job.get('template_id')}")
        for key in ("source_json","source_markdown"):
            p=ROOT/job.get(key,"")
            if not p.is_file(): fail(errors,f"{prefix}: missing {key} {p}")
        src=ROOT/job.get("source_json","")
        if src.is_file():
            data=json.loads(src.read_text())
            source_title=data.get("page_data",{}).get("title")
            if expected not in (4,5) and source_title!=job.get("title"):
                fail(errors,f"{prefix}: manifest title {job.get('title')!r} differs from canonical source {source_title!r}")
        if not re.fullmatch(rf"{re.escape(expected_id)}-[a-z0-9-]+\.png",job.get("output_file","")):
            fail(errors,f"{prefix}: output filename is not canonical")

def validate_brand(lock, errors, require_approved):
    brand=lock.get("brand_assets",{})
    for name in ("official_logo","star_mascot"):
        a=brand.get(name,{})
        if require_approved and a.get("status")!="approved": fail(errors,f"brand asset {name} is not approved")
        if a.get("status")=="approved":
            p=ROOT/(a.get("file") or "")
            if not p.is_file(): fail(errors,f"brand asset {name} file is missing")
            elif sha(p)!=a.get("sha256"): fail(errors,f"brand asset {name} hash mismatch")
            else:
                try:
                    with Image.open(p) as im: im.verify()
                except Exception as e: fail(errors,f"brand asset {name} is unreadable: {e}")

def validate_pages(manifest, lock, errors):
    expected_size=(2480,3508)
    pages=lock.get("page_assets",{})
    for job in manifest["jobs"]:
        pid=job["asset_lock_id"]; entry=pages.get(pid)
        if not entry: fail(errors,f"{pid}: no asset-lock entry"); continue
        if entry.get("status")!="approved": fail(errors,f"{pid}: asset status is {entry.get('status')}, not approved"); continue
        p=ROOT/(entry.get("file") or "")
        if not p.is_file(): fail(errors,f"{pid}: approved file missing"); continue
        if sha(p)!=entry.get("sha256"): fail(errors,f"{pid}: approved file hash mismatch"); continue
        try:
            with Image.open(p) as im:
                if im.format!="PNG": fail(errors,f"{pid}: approved page is not PNG")
                if im.size!=expected_size: fail(errors,f"{pid}: expected {expected_size[0]}x{expected_size[1]} at 300 DPI, found {im.size}")
                im.verify()
        except Exception as e: fail(errors,f"{pid}: unreadable approved page: {e}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    ap.add_argument("--asset-lock",type=Path,default=DEFAULT_LOCK)
    ap.add_argument("--mode",choices=("manifest","release"),default="release")
    args=ap.parse_args()
    manifest=json.loads(args.manifest.read_text()); lock=json.loads(args.asset_lock.read_text()); errors=[]
    validate_manifest(manifest,errors)
    validate_brand(lock,errors,args.mode=="release")
    if args.mode=="release": validate_pages(manifest,lock,errors)
    if errors:
        print("REJECTED")
        for e in errors: print("-",e)
        return 1
    print(f"PASS: {args.mode} validation; 44 canonical physical pages; immutable inputs verified")
    return 0

if __name__=="__main__": sys.exit(main())
