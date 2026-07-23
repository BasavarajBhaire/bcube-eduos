#!/usr/bin/env python3
"""Generate BCube cover illustrations with the OpenAI Images API.

This provider reuses the Phase 6.5 workbook, QA, retry, HTML review and ZIP
machinery while replacing the cloud backend with the OpenAI Images API.
No endpoint id is required. Authentication uses OPENAI_API_KEY or --api-key.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import importlib.util
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CLOUD_SCRIPT = ROOT / "scripts" / "bcube_cloud_illustrations.py"


def load_cloud_module():
    module_name = "bcube_cloud_illustrations"
    spec = importlib.util.spec_from_file_location(module_name, CLOUD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load BCube cloud illustration engine")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


cloud = load_cloud_module()


class OpenAIImagesProvider(cloud.Provider):
    name = "openai"

    def __init__(self, api_key: str, model: str, quality: str, size: str, background: str, output_format: str, timeout: int, base_url: str, cost_per_image: float) -> None:
        self.api_key = api_key
        self.model = model
        self.quality = quality
        self.size = size
        self.background = background
        self.output_format = output_format
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self.cost_per_image = cost_per_image

    def generate(self, prompt: str, page_id: str, output: Path) -> Dict[str, Any]:
        started = time.time()
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": self.size,
            "quality": self.quality,
            "background": self.background,
            "output_format": self.output_format,
        }
        request = urllib.request.Request(
            self.base_url + "/images/generations",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
                request_id = response.headers.get("x-request-id")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError("OpenAI Images API HTTP %s: %s" % (exc.code, detail)) from exc

        data = body.get("data")
        if not isinstance(data, list) or not data:
            raise RuntimeError("OpenAI Images API returned no image data")
        first = data[0]
        output.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(first, dict) and isinstance(first.get("b64_json"), str):
            output.write_bytes(base64.b64decode(first["b64_json"]))
        elif isinstance(first, dict) and isinstance(first.get("url"), str):
            urllib.request.urlretrieve(first["url"], output)
        else:
            raise RuntimeError("OpenAI Images API response had neither b64_json nor url")

        elapsed = round(time.time() - started, 3)
        return {
            "provider": self.name,
            "model": self.model,
            "quality": self.quality,
            "size": self.size,
            "background": self.background,
            "output_format": self.output_format,
            "request_id": request_id,
            "elapsed_seconds": elapsed,
            "estimated_cost_usd": round(self.cost_per_image, 4),
            "usage": body.get("usage"),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate BCube illustrations with OpenAI Images")
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--sheet", default="Complete Book List")
    parser.add_argument("--level", choices=["all", "nursery", "lkg", "ukg"], default="all")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"))
    parser.add_argument("--model", default="gpt-image-1")
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"], default="medium")
    parser.add_argument("--size", choices=["1024x1024", "1024x1536", "1536x1024", "auto"], default="1024x1024")
    parser.add_argument("--background", choices=["opaque", "transparent", "auto"], default="opaque")
    parser.add_argument("--output-format", choices=["png", "jpeg", "webp"], default="png")
    parser.add_argument("--base-url", default="https://api.openai.com/v1")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--cost-per-image", type=float, default=0.0, help="Manual estimate used only for budget gating/reporting")
    parser.add_argument("--max-budget-usd", type=float, help="Reject the batch before any request if the estimated maximum exceeds this value")
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--min-occupancy", type=float, default=0.55)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--output-root", type=Path, default=ROOT / "production-renders" / "openai-illustration-batches")
    parser.add_argument("--batch-name")
    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("OpenAI generation requires OPENAI_API_KEY or --api-key")
    if args.workers < 1:
        raise ValueError("--workers must be at least 1")
    if args.cost_per_image < 0:
        raise ValueError("--cost-per-image cannot be negative")

    rows = cloud.workbook_rows(args.workbook, args.sheet)
    required = {"Level", "Book Slug", "Book Title", "Cover Page ID", "Full Cover Illustration Prompt"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Workbook must contain columns: %s" % sorted(required))
    selected = [cloud.WorkItem(row["Level"].lower(), row["Book Slug"], row["Book Title"], row["Cover Page ID"], row["Full Cover Illustration Prompt"]) for row in rows if args.level == "all" or row["Level"].lower() == args.level]
    if not selected:
        raise ValueError("No workbook rows matched the selected level")

    estimated_max = round(len(selected) * args.cost_per_image * (args.max_retries + 1), 4)
    if args.max_budget_usd is not None and estimated_max > args.max_budget_usd:
        raise ValueError("Estimated maximum cost $%.4f exceeds --max-budget-usd $%.4f; no API request was sent" % (estimated_max, args.max_budget_usd))

    provider = OpenAIImagesProvider(args.api_key, args.model, args.quality, args.size, args.background, args.output_format, args.timeout, args.base_url, args.cost_per_image)
    name = args.batch_name or (args.workbook.stem.replace(" ", "_") + "-openai")
    root = args.output_root / name
    root.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    results: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(cloud.process, item, provider, root, args.max_retries, args.min_occupancy, args.resume, lock) for item in selected]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: (item.get("level", ""), item.get("book", ""), item.get("page_id", "")))

    approved = sum(item.get("state") in {"APPROVED", "SKIPPED_APPROVED"} for item in results)
    failed = len(results) - approved
    actual_estimate = round(sum(float(item.get("estimated_cost_usd", 0.0)) for item in results), 4)
    elapsed = round(sum(float(item.get("elapsed_seconds", 0.0)) for item in results), 3)
    summary = {
        "phase": "6.6",
        "provider": "openai",
        "model": args.model,
        "quality": args.quality,
        "size": args.size,
        "workbook": str(args.workbook),
        "selected": len(selected),
        "approved": approved,
        "failed": failed,
        "complete": approved == len(selected),
        "estimated_maximum_cost_usd": estimated_max,
        "estimated_cost_usd": actual_estimate,
        "total_elapsed_seconds": elapsed,
        "results": results,
    }
    manifest = root / "batch-manifest.json"
    manifest.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    gallery = root / "illustration-review.html"
    cloud.html_report(gallery, results, root)
    images_zip = root / (name + "-ILLUSTRATIONS.zip")
    prompts_zip = root / (name + "-PROMPTS.zip")
    cloud.zip_directory(root / "images", images_zip)
    cloud.zip_directory(root / "prompts", prompts_zip)
    status = "PASS" if failed == 0 and (not args.require_complete or approved == len(selected)) else "FAIL"
    print(json.dumps({
        "status": status,
        "provider": "openai",
        "batch_root": str(root),
        "manifest": str(manifest),
        "html_report": str(gallery),
        "illustrations_zip": str(images_zip),
        "prompts_zip": str(prompts_zip),
        "selected": len(selected),
        "approved": approved,
        "failed": failed,
        "estimated_maximum_cost_usd": estimated_max,
        "estimated_cost_usd": actual_estimate,
    }, indent=2))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, TimeoutError, urllib.error.URLError) as exc:
        print("BCube OpenAI illustration ERROR: %s" % exc, file=os.sys.stderr)
        raise SystemExit(2)
