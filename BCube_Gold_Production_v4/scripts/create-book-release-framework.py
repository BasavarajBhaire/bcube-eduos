#!/usr/bin/env python3
"""Create a deterministic 44-page V4 framework from 41 certified V3 packages."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / "BCube_Gold_Production_v4"


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_sources(source_dir, prefix):
    records = {}
    for path in sorted(source_dir.glob(f"{prefix}-NURSERY-V3-P*.json")):
        match = re.search(r"-P(\d{3})-", path.name)
        if not match:
            continue
        position = int(match.group(1))
        data = json.loads(path.read_text())
        records[position] = {
            "json": path,
            "md": path.with_suffix(".md"),
            "title": data["page_data"]["title"],
            "page_type": data["page_data"].get("page_type", "activity_page"),
        }
    if set(records) != set(range(1, 42)):
        missing = sorted(set(range(1, 42)) - set(records))
        raise SystemExit(f"Expected 41 source packages; missing: {missing}")
    return records


def rel(path):
    return str(path.relative_to(ROOT))


def template_for(source_position, page_type):
    if source_position == 1:
        return "cover"
    if source_position == 2:
        return "copyright"
    if source_position == 3:
        return "contents"
    if source_position == 4:
        return "welcome"
    if source_position == 40 or page_type == "certificate":
        return "certificate"
    if source_position == 41:
        return "completion"
    return "illustrated-activity"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--about-copy", required=True)
    parser.add_argument("--skills-summary", required=True)
    parser.add_argument("--force", action="store_true", help="Explicitly replace an existing generated framework")
    args = parser.parse_args()

    manifest_path = V4 / "manifests" / "nursery" / f"{args.slug}.release-v4.json"
    if manifest_path.exists() and not args.force:
        raise SystemExit(f"Framework already exists: {manifest_path}. Use --force only for an intentional replacement.")

    source_dir = ROOT / "production-prompts" / args.slug / "nursery" / "v3" / "pages"
    sources = load_sources(source_dir, args.prefix)
    production_pages = V4 / "production" / "nursery" / args.slug / "pages"
    approved = V4 / "approved-assets" / "nursery" / args.slug
    for directory in (production_pages, approved / "pages", approved / "illustrations", approved / "qa"):
        directory.mkdir(parents=True, exist_ok=True)
    for directory in (approved / "pages", approved / "illustrations", approved / "qa"):
        (directory / ".gitkeep").touch()

    book_id = f"{args.slug.replace('-', '_').upper()}_NURSERY"
    v4_prefix = f"{args.prefix}-NURSERY-V4"
    about_id = f"{v4_prefix}-P002"
    back_id = f"{v4_prefix}-P044"

    about_json = {
        "prompt_id": about_id,
        "version": "4.1.0",
        "page_data": {
            "page_id": about_id, "book_id": book_id, "page_number": 1,
            "page_type": "front_matter", "title": "About This Book", "age_level": "Nursery (3+)",
            "visible_text": args.about_copy,
            "illustration": {"scene": "Adult-facing overview with restrained use of the approved Star mascot."},
            "individual_specification": {"response_space": "None", "page_specific_prohibition": "No child worksheet, score, or printed page number."}
        }
    }
    back_json = {
        "prompt_id": back_id,
        "version": "4.1.0",
        "page_data": {
            "page_id": back_id, "book_id": book_id, "page_number": None,
            "page_type": "back_cover", "title": "Back Cover", "age_level": "Nursery (3+)",
            "visible_text": [args.title, "Nursery (3+)", args.skills_summary, "BCube Future Academy", "BCube Future Skills Learning Series™", "bcubefutureacademy.in", "info@bcubefutureacademy.in"],
            "illustration": {"scene": "Restrained confidence-themed decoration with official locked logo and approved Star mascot."},
            "individual_specification": {"response_space": "None", "page_specific_prohibition": "No printed page number, invented ISBN, barcode, QR code, contact detail, logo, or mascot."}
        }
    }
    (production_pages / f"{about_id}-about-this-book.json").write_text(json.dumps(about_json, indent=2, ensure_ascii=False) + "\n")
    (production_pages / f"{back_id}-back-cover.json").write_text(json.dumps(back_json, indent=2, ensure_ascii=False) + "\n")
    (production_pages / f"{about_id}-about-this-book.md").write_text(f"# {args.title} — About This Book\n\n{args.about_copy}\n\nNo printed page number. Use only locked brand assets.\n")
    (production_pages / f"{back_id}-back-cover.md").write_text(f"# {args.title} — Back Cover\n\n- {args.skills_summary}\n- BCube Future Academy\n- bcubefutureacademy.in\n- info@bcubefutureacademy.in\n\nNo printed page number. No invented publication details.\n")

    jobs = []
    for position in range(1, 45):
        prompt_id = f"{v4_prefix}-P{position:03d}"
        if position == 1:
            src_pos, role, logical, visible = 1, "cover", None, False
            title, out_slug = sources[1]["title"], "cover-page"
        elif position == 2:
            src_pos, role, logical, visible = None, "about_this_book", 1, False
            title, out_slug = "About This Book", "about-this-book"
        elif position == 3:
            src_pos, role, logical, visible = 2, "copyright", 2, False
            title, out_slug = sources[2]["title"], slugify(sources[2]["title"])
        elif position in (4, 5):
            src_pos, role, logical, visible = 3, f"contents_part_{position-3}", position-1, False
            title, out_slug = f"Contents — Part {position-3}", f"contents-part-{position-3}"
        elif position == 44:
            src_pos, role, logical, visible = None, "back_cover", None, False
            title, out_slug = "Back Cover", "back-cover"
        else:
            src_pos, logical, visible = position - 2, position - 1, True
            role = "welcome" if position == 6 else "certificate" if src_pos == 40 else "completion" if src_pos == 41 else "learning_page"
            title, out_slug = sources[src_pos]["title"], slugify(sources[src_pos]["title"])

        if src_pos is None:
            source_id = None
            source_json = production_pages / f"{prompt_id}-{out_slug}.json"
            source_md = production_pages / f"{prompt_id}-{out_slug}.md"
            template = "about_this_book" if position == 2 else "back_cover"
        else:
            source_id = f"{args.prefix}-NURSERY-V3-P{src_pos:03d}"
            source_json, source_md = sources[src_pos]["json"], sources[src_pos]["md"]
            template = template_for(src_pos, sources[src_pos]["page_type"])
        jobs.append({
            "production_position": position, "prompt_id": prompt_id, "source_prompt_id": source_id,
            "title": title, "slug": out_slug, "page_role": role, "logical_page_number": logical,
            "printed_number_visible": visible, "source_markdown": rel(source_md), "source_json": rel(source_json),
            "template_id": template, "asset_lock_id": prompt_id, "output_file": f"{prompt_id}-{out_slug}.png"
        })

    manifest = {
        "manifest_version": "4.1.0", "book_id": book_id, "book": args.title, "level": "Nursery",
        "release_mode": "approved-assets-only", "total_packages": 44,
        "brand_lock": "BCube_Gold_Production_v4/approved-assets/brand/asset-lock.json", "jobs": jobs
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    missing = {
        "status": "missing", "file": None, "sha256": None, "approved_by": None,
        "approved_at": None, "source_package_version": None,
        "notes": "Promote only after exact-page human QA; release builds may not generate or substitute this page."
    }
    lock = {"lock_version": "1.0.0", "book_id": book_id, "brand_lock": manifest["brand_lock"],
            "page_assets": {job["prompt_id"]: dict(missing) for job in jobs}}
    (approved / "asset-lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    (approved / "README.md").write_text(
        f"# Approved assets — {args.title} / Nursery\n\n"
        "Only founder-approved golden assets belong here. Rejected candidates and ZIP files are prohibited.\n\n"
        "- `pages/`: 44 individually approved page PNGs\n"
        "- `illustrations/`: approved reusable source illustrations only\n"
        "- `qa/`: signed QA records tied to exact SHA-256 hashes\n"
        "- `asset-lock.json`: immutable release inputs\n"
    )
    print(manifest_path)
    print(approved / "asset-lock.json")


if __name__ == "__main__":
    main()
