#!/usr/bin/env python3
"""Assemble a byte-reproducible release from approved full-page assets only."""
import argparse, hashlib, json, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V4=ROOT/"BCube_Gold_Production_v4"
MANIFEST=V4/"manifests/nursery/communication-champions.release-v4.json"
LOCK=V4/"approved-assets/nursery/communication-champions/asset-lock.json"
VALIDATOR=V4/"scripts/validate-deterministic-release.py"

def sha(p):
    h=hashlib.sha256(p.read_bytes()).hexdigest(); return h

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--release-id",required=True,help="New immutable release id, for example 4.1.0-rc1")
    args=ap.parse_args()
    check=subprocess.run([sys.executable,str(VALIDATOR),"--mode","release"])
    if check.returncode: print("Build stopped: deterministic preflight failed.",file=sys.stderr); return check.returncode
    manifest=json.loads(MANIFEST.read_text()); lock=json.loads(LOCK.read_text())
    out=V4/"releases/nursery/communication-champions"/args.release_id
    if out.exists(): print("Build stopped: release id already exists; releases are immutable.",file=sys.stderr); return 2
    pages=out/"individual-pages"; pages.mkdir(parents=True)
    checks=[]
    for job in manifest["jobs"]:
        entry=lock["page_assets"][job["asset_lock_id"]]; src=ROOT/entry["file"]; dst=pages/job["output_file"]
        shutil.copyfile(src,dst)
        if sha(dst)!=entry["sha256"]: print(f"Build stopped: copy hash mismatch for {job['prompt_id']}",file=sys.stderr); return 1
        checks.append(f"{entry['sha256']}  {job['output_file']}")
    (out/"SHA256SUMS.txt").write_text("\n".join(checks)+"\n")
    (out/"release-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    zpath=out/f"Communication_Champions_Nursery_{args.release_id}_43_Individual_Pages.zip"
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(pages.glob("*.png")):
            info=zipfile.ZipInfo(p.name,date_time=(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16; z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(out); print(zpath); print("release_sha256",sha(zpath)); return 0

if __name__=="__main__": sys.exit(main())
