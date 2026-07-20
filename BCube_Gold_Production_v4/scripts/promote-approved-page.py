#!/usr/bin/env python3
"""Promote one human-reviewed page candidate into immutable approved-assets storage."""
import argparse, datetime, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
V4=ROOT/"BCube_Gold_Production_v4"
DEFAULT_MANIFEST=V4/"manifests/nursery/communication-champions.release-v4.json"
DEFAULT_LOCK=V4/"approved-assets/nursery/communication-champions/asset-lock.json"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def norm(s): return re.sub(r"[^a-z0-9]+","",s.lower())

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prompt_id")
    ap.add_argument("candidate",type=Path)
    ap.add_argument("--reviewer",required=True)
    ap.add_argument("--source-package-version",required=True)
    ap.add_argument("--qa-record",required=True,type=Path,help="Signed JSON QA record for this exact candidate")
    ap.add_argument("--founder-approved",action="store_true",help="Required explicit approval gate")
    ap.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    ap.add_argument("--asset-lock",type=Path,default=DEFAULT_LOCK)
    args=ap.parse_args()
    if not args.founder_approved:
        print("REJECTED: explicit --founder-approved flag is required",file=sys.stderr); return 2
    manifest=json.loads(args.manifest.read_text()); jobs={j["prompt_id"]:j for j in manifest["jobs"]}
    if args.prompt_id not in jobs: print("REJECTED: prompt id is not in canonical manifest",file=sys.stderr); return 2
    if not args.candidate.is_file(): print("REJECTED: candidate file missing",file=sys.stderr); return 2
    try:
        with Image.open(args.candidate) as im:
            if im.format!="PNG" or im.size!=(2480,3508):
                print(f"REJECTED: candidate must be 2480x3508 PNG; found {im.format} {im.size}",file=sys.stderr); return 1
            im.verify()
    except Exception as e: print(f"REJECTED: unreadable image: {e}",file=sys.stderr); return 1
    job=jobs[args.prompt_id]
    try:
        ocr=subprocess.run(["tesseract",str(args.candidate),"stdout","--psm","6"],capture_output=True,text=True,check=True).stdout
    except Exception as e: print(f"REJECTED: OCR validation unavailable: {e}",file=sys.stderr); return 1
    if norm(job["title"]) not in norm(ocr):
        print(f"REJECTED: exact canonical title was not detected: {job['title']}",file=sys.stderr); return 1
    digest=sha(args.candidate)
    try: qa=json.loads(args.qa_record.read_text())
    except Exception as e: print(f"REJECTED: unreadable QA record: {e}",file=sys.stderr); return 1
    required_checks={
      "canonical_identity","exact_visible_text","required_scene","required_activity",
      "no_crop_or_overlap","official_logo","official_mascot","safe_margins","individual_page"
    }
    if qa.get("prompt_id")!=args.prompt_id or qa.get("candidate_sha256")!=digest:
        print("REJECTED: QA record does not identify this exact prompt and candidate hash",file=sys.stderr); return 1
    if qa.get("reviewer")!=args.reviewer or qa.get("score",0)<95 or qa.get("critical_defects")!=0:
        print("REJECTED: QA record must match reviewer, score at least 95, and contain zero critical defects",file=sys.stderr); return 1
    checks=qa.get("checks",{})
    if set(checks)!=required_checks or not all(checks.values()):
        print("REJECTED: every required semantic and visual QA check must be explicitly true",file=sys.stderr); return 1
    book_slug=args.manifest.name.removesuffix(".release-v4.json")
    dest_dir=V4/"approved-assets/nursery"/book_slug/"pages"/args.prompt_id
    dest_dir.mkdir(parents=True,exist_ok=True)
    dest=dest_dir/f"{args.prompt_id}-{digest[:12]}.png"
    if not dest.exists(): shutil.copy2(args.candidate,dest)
    lock=json.loads(args.asset_lock.read_text()); previous=lock["page_assets"][args.prompt_id]
    if previous.get("status")=="approved" and previous.get("sha256")!=digest:
        print("REJECTED: an approved version already exists; retire it explicitly before promoting a replacement",file=sys.stderr); return 1
    lock["page_assets"][args.prompt_id]={
      "status":"approved","file":str(dest.relative_to(ROOT)),"sha256":digest,"approved_by":args.reviewer,
      "approved_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "source_package_version":args.source_package_version,
      "qa_record":str(args.qa_record.resolve().relative_to(ROOT)) if args.qa_record.resolve().is_relative_to(ROOT) else str(args.qa_record.resolve()),
      "notes":"Human-reviewed golden page. Release assembly must copy this file unchanged."
    }
    args.asset_lock.write_text(json.dumps(lock,indent=2)+"\n")
    print(dest); print(digest)
    return 0

if __name__=="__main__": sys.exit(main())
