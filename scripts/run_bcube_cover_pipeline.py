#!/usr/bin/env python3
"""Run the deterministic BCube Nursery cover pipeline.

Smart mode builds page data from the book registry. Candidate composition is
separate from final approval and evidence-based QA.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_nursery_cover.py"
FINALIZER = ROOT / "bcube-publishing-sdk/composer/finalize_cover_evidence.py"
VALIDATOR = ROOT / "scripts/validate_rendered_page.py"
BOOKS = ROOT / "bcube-publishing-sdk/books/nursery-books.json"


def run(command: list[str]) -> None:
    print("+", " ".join(command)); subprocess.run(command, cwd=ROOT, check=True)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict): raise ValueError(f"{path} must contain a JSON object")
    return value


def valid_image(path: Path) -> bool:
    if not path.is_file(): return False
    try:
        with Image.open(path) as image: image.verify()
        return True
    except Exception: return False


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try: return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc: raise ValueError(f"Input must be inside the repository after staging: {resolved}") from exc


def find_asset(candidates: list[str], label: str) -> Path:
    attempted=[]
    for candidate in candidates:
        path=ROOT/candidate; attempted.append(candidate)
        if valid_image(path): return path
    raise FileNotFoundError(f"No valid {label} asset was found. Checked:\n  - " + "\n  - ".join(attempted))


def validate_star_crop(path: Path, crop: list[int]) -> None:
    if len(crop) != 4: raise ValueError("official_star_crop must contain four integers")
    with Image.open(path) as image:
        if crop[0] < 0 or crop[1] < 0 or crop[2] > image.width or crop[3] > image.height or crop[2] <= crop[0] or crop[3] <= crop[1]:
            raise ValueError(f"Registered Star crop {crop} is outside approved source {path} sized {image.size}")
        crop_ratio=(crop[2]-crop[0])/(crop[3]-crop[1])
        if not 0.65 <= crop_ratio <= 1.55:
            raise ValueError(f"Registered Star crop has unexpected aspect ratio: {crop_ratio:.2f}")


def stage_illustration(source: Path, page_id: str) -> Path:
    source=source.expanduser().resolve()
    if not valid_image(source): raise FileNotFoundError(f"Illustration is missing or unreadable: {source}")
    destination=ROOT/"production-renders/illustrations"/f"{page_id}.png"; destination.parent.mkdir(parents=True,exist_ok=True)
    with Image.open(source) as image:
        if image.width < 768 or image.height < 768: raise ValueError(f"Illustration too small: {image.size}")
        image.convert("RGB").save(destination,"PNG",dpi=(300,300))
    return destination


def build_smart_data(args: argparse.Namespace) -> tuple[Path,Path,Path,Path]:
    registry=load_json(BOOKS); defaults=registry.get("defaults",{}); books=registry.get("books",{})
    if args.book not in books: raise ValueError(f"Unknown Nursery book {args.book!r}. Available: {', '.join(sorted(books))}")
    if not args.illustration: raise ValueError("--illustration is required with --book")
    if not args.confirm_clean_illustration:
        raise ValueError("Inspect the image and rerun with --confirm-clean-illustration only when it has no text, logo, mascot, badge, embedded page, or page layout.")
    book=books[args.book]; page_id=str(book["page_id"]); illustration=stage_illustration(args.illustration,page_id)
    logo=find_asset(list(defaults.get("official_logo_candidates",[])),"official BCube logo")
    star=find_asset(list(defaults.get("official_star_candidates",[])),"official Star source")
    star_crop=list(defaults.get("official_star_crop",[])); validate_star_crop(star,star_crop)
    output=args.output or ROOT/"production-renders/pages"/f"{page_id}.png"
    evidence=args.evidence or ROOT/"production-renders/qa-manifests"/f"{page_id}.json"
    report=args.report or ROOT/"validation/rendered-pages"/f"{page_id}.render-report.json"
    data_path=ROOT/"production-renders/page-data"/f"{page_id}.json"
    if args.approve and (not args.reviewer or len(args.reviewer.strip())<3): raise ValueError("--reviewer with at least three characters is required with --approve")
    human={"reviewer":args.reviewer.strip() if args.reviewer else "Pending Review","approved_on":date.today().isoformat(),"status":"APPROVED" if args.approve else "PENDING","artifact_sha256":"0"*64,"notes":"Approved after reviewing deterministic candidate." if args.approve else "Candidate awaiting visual approval."}
    page_data={
        "page_id":page_id,"book_key":book["book_key"],"title_lines":book["title_lines"],"tagline":book["tagline"],
        "level":defaults["level"],"age":defaults["age"],"skills":book["skills"],"skill_icon_keys":book["skill_icon_keys"],
        "pillars":defaults["pillars"],"pillar_icon_keys":defaults["pillar_icon_keys"],"footer_keywords":book["footer_keywords"],
        "illustration_path":repo_relative(illustration),"official_logo_path":repo_relative(logo),"official_star_path":repo_relative(star),"official_star_crop":star_crop,
        "illustration_evidence":{"contains_text":False,"contains_logo":False,"contains_mascot":False,"contains_badge":False,"contains_page_layout":False,"contains_embedded_page":False},
        "text_evidence":{"detector":{"name":"bcube-composer-known-text","version":"1.1"},"detected_text":book["required_detected_text"]},
        "human_approval":human
    }
    data_path.parent.mkdir(parents=True,exist_ok=True); data_path.write_text(json.dumps(page_data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return data_path,output,evidence,report


def parse_args() -> argparse.Namespace:
    parser=argparse.ArgumentParser(); mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--data",type=Path); mode.add_argument("--book")
    parser.add_argument("--illustration",type=Path); parser.add_argument("--confirm-clean-illustration",action="store_true")
    parser.add_argument("--approve",action="store_true"); parser.add_argument("--reviewer"); parser.add_argument("--output",type=Path); parser.add_argument("--evidence",type=Path); parser.add_argument("--report",type=Path)
    return parser.parse_args()


def main() -> int:
    args=parse_args()
    if args.book: data,output,evidence,report=build_smart_data(args)
    else:
        if not args.output or not args.evidence or not args.report: raise ValueError("Legacy --data mode requires --output, --evidence and --report")
        data,output,evidence,report=args.data,args.output,args.evidence,args.report
    for path in (output,evidence,report): path.parent.mkdir(parents=True,exist_ok=True)
    run([sys.executable,str(COMPOSER),"--data",str(data),"--output",str(output),"--evidence-output",str(evidence)])
    run([sys.executable,str(FINALIZER),"--evidence",str(evidence)])
    if args.book and not args.approve:
        print("\nBCube cover candidate COMPOSED (not production-approved)."); print(f"Review image: {output}"); return 0
    run([sys.executable,str(VALIDATOR),"--artifact",str(output),"--manifest",str(evidence),"--output",str(report)])
    print(f"BCube cover pipeline PASS: {output}"); return 0


if __name__=="__main__":
    try: raise SystemExit(main())
    except (ValueError,FileNotFoundError) as exc:
        print(f"BCube cover pipeline ERROR: {exc}",file=sys.stderr); raise SystemExit(2)
