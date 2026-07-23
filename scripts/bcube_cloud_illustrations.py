#!/usr/bin/env python3
"""Generate BCube illustrations through RunPod Serverless and package QA evidence."""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import hashlib
import html
import importlib.util
import json
import os
import threading
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def workbook_rows(path: Path, sheet: str) -> List[Dict[str, str]]:
    reader = ROOT / "scripts" / "bcube_generate_from_excel.py"
    spec = importlib.util.spec_from_file_location("bcube_generate_from_excel", reader)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Phase 7 workbook reader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.read_xlsx_table(path, sheet)


def validate_image(path: Path, minimum: float) -> Dict[str, Any]:
    defects: List[str] = []
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
            difference = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
            box = difference.point(lambda value: 255 if value > 18 else 0).getbbox()
            occupancy = 0.0 if not box else ((box[2] - box[0]) * (box[3] - box[1])) / float(width * height)
            if occupancy < minimum:
                defects.append("LOW_OCCUPANCY")
            border = max(4, int(min(width, height) * 0.02))
            strips = [rgb.crop((0, 0, width, border)), rgb.crop((0, height - border, width, height)), rgb.crop((0, 0, border, height)), rgb.crop((width - border, 0, width, height))]
            border_mean = sum(sum(ImageStat.Stat(strip).mean) / 3.0 for strip in strips) / len(strips)
            if border_mean < 235:
                defects.append("BORDER_NOT_WHITE")
            return {"status": "PASS" if not defects else "FAIL", "path": str(path), "size": [width, height], "dpi": image.info.get("dpi", (0, 0))[0], "occupancy": round(occupancy, 4), "border_mean": round(border_mean, 2), "sha256": file_hash(path), "defects": defects}
    except Exception as exc:
        return {"status": "FAIL", "path": str(path), "defects": ["UNREADABLE_IMAGE: %s" % exc]}


def repaired_prompt(prompt: str, defects: Iterable[str], attempt: int) -> str:
    defect_set = set(defects)
    additions: List[str] = []
    if "LOW_OCCUPANCY" in defect_set:
        additions.append("Make the complete subject occupy 88–92% of the square canvas with only a narrow white safety margin.")
    if "BORDER_NOT_WHITE" in defect_set:
        additions.append("Keep all artwork fully inside the canvas and preserve a clean pure-white outer border on every edge.")
    if "NOT_SQUARE" in defect_set:
        additions.append("Generate an exactly square image.")
    if "IMAGE_TOO_SMALL" in defect_set:
        additions.append("Generate at least 1254 by 1254 pixels.")
    additions.append("Do not include text, letters, numbers, logos, badges, watermarks, borders, page layouts, or the BCube Star mascot.")
    return prompt + "\n\nAUTOMATIC QA REPAIR — ATTEMPT %d\n%s" % (attempt, " ".join(additions))


class Provider:
    name = "provider"

    def generate(self, prompt: str, page_id: str, output: Path) -> Dict[str, Any]:
        raise NotImplementedError


class MockProvider(Provider):
    name = "mock"

    def generate(self, prompt: str, page_id: str, output: Path) -> Dict[str, Any]:
        started = time.time()
        output.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256((page_id + prompt).encode("utf-8")).digest()
        colour = tuple(70 + value % 150 for value in digest[:3])
        image = Image.new("RGB", (1254, 1254), "white")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((75, 75, 1179, 1179), radius=120, fill=colour)
        draw.ellipse((270, 250, 984, 964), fill="white")
        draw.rounded_rectangle((380, 430, 874, 1050), radius=80, fill=tuple(min(255, value + 30) for value in colour))
        image.save(output, "PNG", dpi=(300, 300))
        return {"provider": self.name, "elapsed_seconds": round(time.time() - started, 3), "estimated_cost_usd": 0.0}


class RunPodProvider(Provider):
    name = "runpod"

    def __init__(self, endpoint: str, key: str, timeout: int, interval: float, workflow: Optional[Dict[str, Any]], rate: float):
        self.base = "https://api.runpod.ai/v2/%s" % endpoint
        self.key = key
        self.timeout = timeout
        self.interval = interval
        self.workflow = workflow
        self.rate = rate

    def request(self, url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def image_value(value: Any) -> Tuple[str, str]:
        if isinstance(value, dict):
            for name in ("image_url", "output_url", "url"):
                if isinstance(value.get(name), str):
                    return "url", value[name]
            for name in ("image_base64", "base64", "image"):
                candidate = value.get(name)
                if isinstance(candidate, str) and len(candidate) > 100:
                    return "base64", candidate
            for name in ("images", "output", "result"):
                if name in value:
                    try:
                        return RunPodProvider.image_value(value[name])
                    except ValueError:
                        pass
        if isinstance(value, list):
            for item in value:
                try:
                    return RunPodProvider.image_value(item)
                except ValueError:
                    continue
        if isinstance(value, str):
            if value.startswith(("http://", "https://")):
                return "url", value
            if len(value) > 100:
                return "base64", value
        raise ValueError("RunPod output did not contain an image URL or base64 image")

    def generate(self, prompt: str, page_id: str, output: Path) -> Dict[str, Any]:
        started = time.time()
        endpoint_input: Dict[str, Any] = {"prompt": prompt, "page_id": page_id, "width": 1254, "height": 1254}
        if self.workflow is not None:
            endpoint_input["workflow"] = self.workflow
        submission = self.request(self.base + "/run", {"input": endpoint_input})
        job = submission.get("id")
        if not job:
            raise RuntimeError("RunPod did not return a job id")
        deadline = time.time() + self.timeout
        completed: Optional[Dict[str, Any]] = None
        while time.time() < deadline:
            status = self.request(self.base + "/status/" + str(job))
            state = str(status.get("status", "")).upper()
            if state == "COMPLETED":
                completed = status
                break
            if state in {"FAILED", "CANCELLED", "TIMED_OUT"}:
                raise RuntimeError("RunPod job %s ended with %s: %s" % (job, state, status.get("error")))
            time.sleep(self.interval)
        if completed is None:
            raise TimeoutError("RunPod job %s timed out" % job)
        kind, value = self.image_value(completed.get("output"))
        output.parent.mkdir(parents=True, exist_ok=True)
        if kind == "url":
            urllib.request.urlretrieve(value, output)
        else:
            if value.lstrip().startswith("data:") and "," in value:
                value = value.split(",", 1)[1]
            output.write_bytes(base64.b64decode(value))
        elapsed = time.time() - started
        execution = completed.get("executionTime") or completed.get("execution_time")
        billed = float(execution) / 1000.0 if isinstance(execution, (int, float)) else elapsed
        return {"provider": self.name, "job_id": job, "elapsed_seconds": round(elapsed, 3), "billed_seconds": round(billed, 3), "estimated_cost_usd": round(billed * self.rate, 4)}


@dataclass
class WorkItem:
    level: str
    book: str
    title: str
    page_id: str
    prompt: str


def zip_directory(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for item in sorted(source.rglob("*")):
            if item.is_file():
                archive.write(item, item.relative_to(source))


def html_report(path: Path, results: List[Dict[str, Any]], root: Path) -> None:
    cards: List[str] = []
    for item in results:
        image_path = Path(str(item.get("image", "")))
        source = ""
        if image_path.is_file():
            try:
                source = image_path.relative_to(root).as_posix()
            except ValueError:
                source = image_path.as_posix()
        qa = item.get("qa", {})
        image = "" if not source else '<img src="{}" alt="{}">'.format(html.escape(source), html.escape(str(item.get("page_id", ""))))
        cards.append('<article class="card"><h2>{}</h2><p><strong>{}</strong><br>{} / {}</p>{}<p class="state {}">{}</p><p>Attempts: {}<br>Time: {}s<br>Estimated cost: ${:.4f}<br>Occupancy: {}</p><details><summary>Prompt and QA</summary><pre>{}</pre><pre>{}</pre></details></article>'.format(html.escape(str(item.get("page_id", ""))), html.escape(str(item.get("title", ""))), html.escape(str(item.get("level", ""))), html.escape(str(item.get("book", ""))), image, html.escape(str(item.get("state", "UNKNOWN"))), html.escape(str(item.get("state", "UNKNOWN"))), item.get("attempts", 0), round(float(item.get("elapsed_seconds", 0.0)), 2), float(item.get("estimated_cost_usd", 0.0)), qa.get("occupancy", "n/a"), html.escape(str(item.get("final_prompt", ""))), html.escape(json.dumps(qa, indent=2))))
    template = '''<!doctype html><html><head><meta charset="utf-8"><title>BCube Illustration Review</title><style>body{font-family:Arial,sans-serif;margin:24px;background:#f7f7fb;color:#24243a}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}.card{background:white;border-radius:16px;padding:16px;box-shadow:0 2px 12px #0001}.card img{width:100%;border-radius:12px;border:1px solid #ddd}.state{font-weight:bold}.APPROVED,.SKIPPED_APPROVED{color:#087f23}.FAILED,.REJECTED{color:#b42318}pre{white-space:pre-wrap;font-size:11px;background:#f3f3f6;padding:10px;border-radius:8px}</style></head><body><h1>BCube Cloud Illustration Review</h1><p>Review every image visually before publishing. Automated QA does not replace human approval.</p><div class="grid">__BCUBE_CARDS__</div></body></html>'''
    path.write_text(template.replace("__BCUBE_CARDS__", "\n".join(cards)), encoding="utf-8")


def process(item: WorkItem, provider: Provider, root: Path, retries: int, minimum: float, resume: bool, print_lock: threading.Lock) -> Dict[str, Any]:
    image = root / "images" / item.level / item.book / (item.page_id + ".png")
    report = root / "reports" / item.level / item.book / (item.page_id + ".json")
    prompt_file = root / "prompts" / item.level / item.book / (item.page_id + ".txt")
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(item.prompt + "\n", encoding="utf-8")
    if resume and image.is_file():
        qa = validate_image(image, minimum)
        if qa["status"] == "PASS":
            result = {"level": item.level, "book": item.book, "title": item.title, "page_id": item.page_id, "state": "SKIPPED_APPROVED", "attempts": 0, "image": str(image), "qa": qa, "elapsed_seconds": 0.0, "estimated_cost_usd": 0.0, "final_prompt": item.prompt}
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            return result
    prompt = item.prompt
    total_time = 0.0
    total_cost = 0.0
    result: Dict[str, Any] = {}
    for attempt in range(1, retries + 2):
        try:
            metadata = provider.generate(prompt, item.page_id, image)
            total_time += float(metadata.get("elapsed_seconds", 0.0))
            total_cost += float(metadata.get("estimated_cost_usd", 0.0))
            qa = validate_image(image, minimum)
            state = "APPROVED" if qa["status"] == "PASS" else "REJECTED"
            result = {"level": item.level, "book": item.book, "title": item.title, "page_id": item.page_id, "state": state, "attempts": attempt, "image": str(image), "qa": qa, "provider": metadata, "elapsed_seconds": round(total_time, 3), "estimated_cost_usd": round(total_cost, 4), "final_prompt": prompt}
            if state == "APPROVED":
                break
            prompt = repaired_prompt(item.prompt, qa.get("defects", []), attempt + 1)
        except Exception as exc:
            result = {"level": item.level, "book": item.book, "title": item.title, "page_id": item.page_id, "state": "FAILED", "attempts": attempt, "image": str(image), "error": str(exc), "elapsed_seconds": round(total_time, 3), "estimated_cost_usd": round(total_cost, 4), "final_prompt": prompt}
            prompt = repaired_prompt(item.prompt, ["PROVIDER_FAILURE"], attempt + 1)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with print_lock:
        print("[%s] %s attempt=%s" % (result.get("state"), item.page_id, result.get("attempts")), flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--sheet", default="Complete Book List")
    parser.add_argument("--level", choices=["all", "nursery", "lkg", "ukg"], default="all")
    parser.add_argument("--provider", choices=["runpod", "mock"], default="runpod")
    parser.add_argument("--endpoint-id", default=os.environ.get("RUNPOD_ENDPOINT_ID"))
    parser.add_argument("--api-key", default=os.environ.get("RUNPOD_API_KEY"))
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--cost-per-second", type=float, default=0.0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--min-occupancy", type=float, default=0.55)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--output-root", type=Path, default=ROOT / "production-renders" / "cloud-illustration-batches")
    parser.add_argument("--batch-name")
    args = parser.parse_args()

    workflow = json.loads(args.workflow.read_text(encoding="utf-8")) if args.workflow else None
    if args.provider == "runpod":
        if not args.endpoint_id or not args.api_key:
            raise ValueError("RunPod requires --endpoint-id/RUNPOD_ENDPOINT_ID and --api-key/RUNPOD_API_KEY")
        provider: Provider = RunPodProvider(args.endpoint_id, args.api_key, args.timeout, args.poll_interval, workflow, args.cost_per_second)
    else:
        provider = MockProvider()

    rows = workbook_rows(args.workbook, args.sheet)
    required = {"Level", "Book Slug", "Book Title", "Cover Page ID", "Full Cover Illustration Prompt"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Workbook must contain columns: %s" % sorted(required))
    selected = [WorkItem(row["Level"].lower(), row["Book Slug"], row["Book Title"], row["Cover Page ID"], row["Full Cover Illustration Prompt"]) for row in rows if args.level == "all" or row["Level"].lower() == args.level]
    if not selected:
        raise ValueError("No workbook rows matched the selected level")

    name = args.batch_name or (args.workbook.stem.replace(" ", "_") + "-" + args.provider)
    root = args.output_root / name
    root.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    results: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(process, item, provider, root, args.max_retries, args.min_occupancy, args.resume, lock) for item in selected]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: (item.get("level", ""), item.get("book", ""), item.get("page_id", "")))

    approved = sum(item.get("state") in {"APPROVED", "SKIPPED_APPROVED"} for item in results)
    failed = len(results) - approved
    cost = round(sum(float(item.get("estimated_cost_usd", 0.0)) for item in results), 4)
    elapsed = round(sum(float(item.get("elapsed_seconds", 0.0)) for item in results), 3)
    summary = {"phase": "6.5", "provider": args.provider, "workbook": str(args.workbook), "selected": len(selected), "approved": approved, "failed": failed, "complete": approved == len(selected), "total_elapsed_seconds": elapsed, "estimated_cost_usd": cost, "results": results}
    manifest = root / "batch-manifest.json"
    manifest.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    gallery = root / "illustration-review.html"
    html_report(gallery, results, root)
    images_zip = root / (name + "-ILLUSTRATIONS.zip")
    prompts_zip = root / (name + "-PROMPTS.zip")
    zip_directory(root / "images", images_zip)
    zip_directory(root / "prompts", prompts_zip)
    status = "PASS" if failed == 0 and (not args.require_complete or approved == len(selected)) else "FAIL"
    print(json.dumps({"status": status, "batch_root": str(root), "manifest": str(manifest), "html_report": str(gallery), "illustrations_zip": str(images_zip), "prompts_zip": str(prompts_zip), "selected": len(selected), "approved": approved, "failed": failed, "estimated_cost_usd": cost}, indent=2))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, TimeoutError, urllib.error.URLError, zipfile.BadZipFile) as exc:
        print("BCube cloud illustration ERROR: %s" % exc, file=os.sys.stderr)
        raise SystemExit(2)
