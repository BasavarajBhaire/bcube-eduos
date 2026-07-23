#!/usr/bin/env python3
"""Generate BCube cover illustrations directly from the prompt workbook.

This pipeline has no OpenAI dependency. It supports manual prompt export,
an arbitrary local command, a local ComfyUI server, and a mock CI provider.
It writes individual PNGs, QA reports, a batch manifest, and ZIP packages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def column_index(reference: str) -> int:
    letters = "".join(ch for ch in reference if ch.isalpha())
    value = 0
    for ch in letters.upper():
        value = value * 26 + ord(ch) - 64
    return value - 1


def resolve_sheet_path(archive: zipfile.ZipFile, target: str) -> str:
    clean = target.replace("\\", "/").lstrip("/")
    candidates = [clean]
    if not clean.startswith("xl/"):
        candidates.insert(0, "xl/" + clean)
    for candidate in candidates:
        if candidate in archive.namelist():
            return candidate
    raise ValueError(f"Worksheet XML target not found in workbook: {target}")


def read_xlsx_table(path: Path, sheet_name: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", NS):
                shared.append("".join(node.text or "" for node in item.iterfind(".//m:t", NS)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
        target = None
        for sheet in workbook.find("m:sheets", NS) or []:
            if sheet.attrib.get("name") == sheet_name:
                rel_id = sheet.attrib.get(f"{{{NS['r']}}}id")
                target = rel_map.get(rel_id or "")
                break
        if not target:
            raise ValueError(f"Worksheet {sheet_name!r} not found")
        root = ET.fromstring(archive.read(resolve_sheet_path(archive, target)))
        rows: list[list[str]] = []
        for row in root.findall(".//m:sheetData/m:row", NS):
            values: dict[int, str] = {}
            for cell in row.findall("m:c", NS):
                idx = column_index(cell.attrib.get("r", "A1"))
                cell_type = cell.attrib.get("t")
                value_node = cell.find("m:v", NS)
                inline = cell.find("m:is", NS)
                value = ""
                if cell_type == "s" and value_node is not None:
                    value = shared[int(value_node.text or "0")]
                elif cell_type == "inlineStr" and inline is not None:
                    value = "".join(node.text or "" for node in inline.iterfind(".//m:t", NS))
                elif value_node is not None:
                    value = value_node.text or ""
                values[idx] = value
            if values:
                rows.append([values.get(i, "") for i in range(max(values) + 1)])
    if not rows:
        return []
    headers = [str(value).strip() for value in rows[0]]
    result: list[dict[str, str]] = []
    for raw in rows[1:]:
        padded = raw + [""] * (len(headers) - len(raw))
        item = {headers[i]: str(padded[i]).strip() for i in range(len(headers)) if headers[i]}
        if any(item.values()):
            result.append(item)
    return result


def validate_image(path: Path, min_occupancy: float) -> dict[str, Any]:
    defects: list[str] = []
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            rgba = image.convert("RGBA")
            width, height = rgba.size
            if width < 1024 or height < 1024:
                defects.append("IMAGE_TOO_SMALL")
            if abs(width - height) > max(width, height) * 0.02:
                defects.append("NOT_SQUARE")
            rgb = Image.new("RGB", rgba.size, "white")
            rgb.paste(rgba, mask=rgba.getchannel("A"))
            diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
            bbox = diff.point(lambda p: 255 if p > 18 else 0).getbbox()
            occupancy = 0.0
            if bbox:
                occupancy = ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / (width * height)
            if occupancy < min_occupancy:
                defects.append("LOW_OCCUPANCY")
            border = max(4, int(min(width, height) * 0.02))
            strips = [
                rgb.crop((0, 0, width, border)),
                rgb.crop((0, height - border, width, height)),
                rgb.crop((0, 0, border, height)),
                rgb.crop((width - border, 0, width, height)),
            ]
            border_mean = sum(sum(ImageStat.Stat(strip).mean) / 3 for strip in strips) / len(strips)
            if border_mean < 235:
                defects.append("BORDER_NOT_WHITE")
            dpi = image.info.get("dpi", (0, 0))[0]
            return {
                "status": "PASS" if not defects else "FAIL",
                "path": str(path),
                "size": [width, height],
                "dpi": dpi,
                "occupancy": round(occupancy, 4),
                "border_mean": round(border_mean, 2),
                "sha256": sha256(path),
                "defects": defects,
            }
    except Exception as exc:
        return {"status": "FAIL", "path": str(path), "defects": [f"UNREADABLE_IMAGE: {exc}"]}


def generate_mock(output: Path, seed_text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    colour = tuple(70 + value % 150 for value in digest[:3])
    image = Image.new("RGB", (1254, 1254), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((75, 75, 1179, 1179), radius=110, fill=colour)
    draw.ellipse((300, 260, 954, 914), fill=(255, 255, 255))
    draw.rounded_rectangle(
        (420, 480, 834, 1000),
        radius=70,
        fill=tuple(min(255, channel + 35) for channel in colour),
    )
    image.save(output, "PNG", dpi=(300, 300))


def generate_command(command: str, prompt: str, output: Path, page_id: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({"BCUBE_PROMPT": prompt, "BCUBE_OUTPUT": str(output), "BCUBE_PAGE_ID": page_id})
    rendered = command.format(prompt=prompt, output=str(output), page_id=page_id)
    subprocess.run(rendered, shell=True, cwd=ROOT, env=env, check=True)
    if not output.is_file():
        raise FileNotFoundError(f"Local generator did not create {output}")


def generate_comfyui(
    server: str,
    workflow_path: Path,
    prompt: str,
    output: Path,
    page_id: str,
    timeout: int,
) -> None:
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    raw = json.dumps(workflow).replace("{{BCUBE_PROMPT}}", prompt).replace("{{BCUBE_PAGE_ID}}", page_id)
    payload = json.dumps({"prompt": json.loads(raw)}).encode("utf-8")
    request = urllib.request.Request(
        server.rstrip("/") + "/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        prompt_id = json.loads(response.read().decode("utf-8"))["prompt_id"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(server.rstrip("/") + f"/history/{prompt_id}", timeout=30) as response:
            history = json.loads(response.read().decode("utf-8"))
        entry = history.get(prompt_id)
        if entry:
            for node in entry.get("outputs", {}).values():
                for image in node.get("images", []):
                    params = urllib.parse.urlencode(
                        {
                            "filename": image["filename"],
                            "subfolder": image.get("subfolder", ""),
                            "type": image.get("type", "output"),
                        }
                    )
                    output.parent.mkdir(parents=True, exist_ok=True)
                    urllib.request.urlretrieve(server.rstrip("/") + "/view?" + params, output)
                    return
        time.sleep(2)
    raise TimeoutError(f"ComfyUI generation timed out for {page_id}")


def write_zip(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file() and path != target:
                archive.write(path, path.relative_to(source))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--sheet", default="Complete Book List")
    parser.add_argument("--level", choices=["all", "nursery", "lkg", "ukg"], default="all")
    parser.add_argument("--provider", choices=["manual", "command", "comfyui", "mock"], default="manual")
    parser.add_argument("--command")
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--comfyui-server", default="http://127.0.0.1:8188")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--min-occupancy", type=float, default=0.55)
    parser.add_argument("--output-root", type=Path, default=ROOT / "production-renders/illustration-batches")
    parser.add_argument("--batch-name")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    if args.provider == "command" and not args.command:
        raise ValueError("--command is required for provider=command")
    if args.provider == "comfyui" and not args.workflow:
        raise ValueError("--workflow is required for provider=comfyui")

    records = read_xlsx_table(args.workbook, args.sheet)
    required = {"Level", "Book Slug", "Cover Page ID", "Full Cover Illustration Prompt"}
    if not records or not required.issubset(records[0]):
        raise ValueError(f"Workbook must contain columns: {sorted(required)}")
    selected = [row for row in records if args.level == "all" or row["Level"].lower() == args.level]
    if not selected:
        raise ValueError("No workbook rows matched the selected level")

    batch_name = args.batch_name or args.workbook.stem.replace(" ", "_")
    batch_root = args.output_root / batch_name
    images_root = batch_root / "images"
    prompts_root = batch_root / "prompts"
    reports_root = batch_root / "reports"
    results: list[dict[str, Any]] = []

    for row in selected:
        level = row["Level"].lower()
        slug = row["Book Slug"]
        page_id = row["Cover Page ID"]
        prompt = row["Full Cover Illustration Prompt"]
        output = images_root / level / slug / f"{page_id}.png"
        prompt_file = prompts_root / level / slug / f"{page_id}.txt"
        report_file = reports_root / level / slug / f"{page_id}.json"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt + "\n", encoding="utf-8")

        if args.resume and output.is_file():
            qa = validate_image(output, args.min_occupancy)
            if qa["status"] == "PASS":
                results.append(
                    {
                        "level": level,
                        "book": slug,
                        "page_id": page_id,
                        "state": "SKIPPED_APPROVED",
                        "qa": qa,
                    }
                )
                continue

        if args.provider == "manual":
            item = {
                "level": level,
                "book": slug,
                "page_id": page_id,
                "state": "MANUAL_REQUIRED",
                "prompt": str(prompt_file),
                "expected_output": str(output),
            }
            report_file.parent.mkdir(parents=True, exist_ok=True)
            report_file.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
            results.append(item)
            continue

        item = None
        error = None
        for attempt in range(1, args.max_retries + 2):
            try:
                if args.provider == "mock":
                    generate_mock(output, page_id + prompt)
                elif args.provider == "command":
                    generate_command(args.command or "", prompt, output, page_id)
                else:
                    generate_comfyui(
                        args.comfyui_server,
                        args.workflow or Path(),
                        prompt,
                        output,
                        page_id,
                        args.timeout,
                    )
                qa = validate_image(output, args.min_occupancy)
                state = "APPROVED" if qa["status"] == "PASS" else "REJECTED"
                item = {
                    "level": level,
                    "book": slug,
                    "page_id": page_id,
                    "state": state,
                    "attempt": attempt,
                    "qa": qa,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                }
                if state == "APPROVED":
                    break
                error = ", ".join(qa.get("defects", []))
            except Exception as exc:
                error = str(exc)
                item = {
                    "level": level,
                    "book": slug,
                    "page_id": page_id,
                    "state": "FAILED",
                    "attempt": attempt,
                    "error": error,
                }
        assert item is not None
        item["error"] = error
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
        results.append(item)
        if item["state"] not in {"APPROVED", "SKIPPED_APPROVED"} and not args.continue_on_error:
            break

    approved = sum(item["state"] in {"APPROVED", "SKIPPED_APPROVED"} for item in results)
    manual = sum(item["state"] == "MANUAL_REQUIRED" for item in results)
    failed = sum(item["state"] in {"FAILED", "REJECTED"} for item in results)
    summary = {
        "phase": "7",
        "workbook": str(args.workbook),
        "provider": args.provider,
        "selected": len(selected),
        "processed": len(results),
        "approved": approved,
        "manual_required": manual,
        "failed": failed,
        "complete": approved == len(selected),
        "results": results,
    }
    manifest = batch_root / "batch-manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    prompt_zip = batch_root / f"{batch_name}-PROMPTS.zip"
    write_zip(prompts_root, prompt_zip)
    images_zip = None
    if images_root.exists():
        images_zip = batch_root / f"{batch_name}-ILLUSTRATIONS.zip"
        write_zip(images_root, images_zip)

    status = "PASS" if failed == 0 and (not args.require_complete or summary["complete"]) else "FAIL"
    print(
        json.dumps(
            {
                "status": status,
                "batch_root": str(batch_root),
                "manifest": str(manifest),
                "prompt_zip": str(prompt_zip),
                "illustration_zip": str(images_zip) if images_zip else None,
                "selected": len(selected),
                "approved": approved,
                "manual_required": manual,
                "failed": failed,
            },
            indent=2,
        )
    )
    if failed or (args.require_complete and not summary["complete"]):
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        ValueError,
        FileNotFoundError,
        subprocess.CalledProcessError,
        TimeoutError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"BCube Excel illustration automation ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
