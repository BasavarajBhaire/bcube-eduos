#!/usr/bin/env python3
"""Fail-closed validator for BCube rendered publishing pages.

The validator intentionally separates machine-verifiable artifact checks from
human/vision checks. A page cannot PASS unless every required visual check is
explicitly supplied as passed in a render manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "design-system/template-lock/reference-registry.json"


def read_png_metadata(path: Path) -> tuple[int, int, float, float]:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("artifact must be a PNG")
    pos = 8
    width = height = None
    dpi_x = dpi_y = 0.0
    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height = struct.unpack(">II", payload[:8])
        elif kind == b"pHYs" and len(payload) == 9:
            xppm, yppm, unit = struct.unpack(">IIB", payload)
            if unit == 1:
                dpi_x = xppm * 0.0254
                dpi_y = yppm * 0.0254
        elif kind == b"IEND":
            break
    if width is None or height is None:
        raise ValueError("PNG is missing IHDR")
    return width, height, dpi_x, dpi_y


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def check(checks: list[dict[str, Any]], ident: str, passed: bool, message: str, severity: str = "critical") -> None:
    checks.append({"id": ident, "passed": bool(passed), "severity": severity, "message": message})


def validate(artifact: Path, manifest_path: Path, output: Path) -> int:
    registry = load_json(REGISTRY)
    manifest = load_json(manifest_path)
    page_type = manifest.get("page_type")
    page_id = manifest.get("page_id")
    checks: list[dict[str, Any]] = []

    check(checks, "artifact.exists", artifact.is_file(), f"artifact exists: {artifact}")
    if not artifact.is_file():
        return write_report(output, page_id or "UNKNOWN", page_type or "UNKNOWN", artifact, checks)

    try:
        width, height, dpi_x, dpi_y = read_png_metadata(artifact)
        check(checks, "canvas.width", width == 2480, f"width is {width}px; required 2480px")
        check(checks, "canvas.height", height == 3508, f"height is {height}px; required 3508px")
        check(checks, "canvas.dpi_x", 299 <= dpi_x <= 301, f"horizontal DPI is {dpi_x:.2f}; required 300")
        check(checks, "canvas.dpi_y", 299 <= dpi_y <= 301, f"vertical DPI is {dpi_y:.2f}; required 300")
    except Exception as exc:
        width = height = 0
        dpi_x = dpi_y = 0.0
        check(checks, "artifact.png_metadata", False, str(exc))

    page_contract = registry.get("page_types", {}).get(page_type)
    check(checks, "contract.page_type", page_contract is not None, f"registered page type: {page_type}")

    visual = manifest.get("visual_checks")
    check(checks, "manifest.visual_checks", isinstance(visual, dict), "visual checks are explicitly declared")
    if isinstance(page_contract, dict) and isinstance(visual, dict):
        for component in page_contract.get("required_components", []):
            passed = visual.get(component) is True
            check(checks, f"required.{component}", passed, f"required component present and approved: {component}")
        for component in page_contract.get("prohibited_components", []):
            passed = visual.get(component) is False
            check(checks, f"prohibited.{component}", passed, f"prohibited component absent: {component}")

    universal = manifest.get("universal_checks", {})
    required_universal = [
        "single_flat_page",
        "official_logo_hash_match",
        "official_star_hash_match_or_not_required",
        "typography_composited",
        "no_duplicate_assets",
        "no_overlap",
        "safe_margins",
        "exact_page_content",
        "reference_geometry_match"
    ]
    for item in required_universal:
        check(checks, f"universal.{item}", universal.get(item) is True, f"universal render check passed: {item}")

    return write_report(output, str(page_id or "UNKNOWN"), str(page_type or "UNKNOWN"), artifact, checks, width, height, dpi_x, dpi_y)


def write_report(output: Path, page_id: str, page_type: str, artifact: Path, checks: list[dict[str, Any]], width: int = 0, height: int = 0, dpi_x: float = 0.0, dpi_y: float = 0.0) -> int:
    failures = [c for c in checks if not c["passed"]]
    critical = sum(1 for c in failures if c["severity"] == "critical")
    score = 100 if not failures else max(0, 100 - 10 * len(failures))
    report = {
        "page_id": page_id,
        "page_type": page_type,
        "artifact": {
            "path": str(artifact),
            "sha256": sha256(artifact) if artifact.is_file() else "0" * 64,
            "width_px": width,
            "height_px": height,
            "dpi_x": round(dpi_x, 2),
            "dpi_y": round(dpi_y, 2)
        },
        "checks": checks,
        "score": score,
        "critical_defects": critical,
        "status": "PASS" if score == 100 and critical == 0 else "FAIL"
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "score": score, "critical_defects": critical, "report": str(output)}))
    return 0 if report["status"] == "PASS" else 1


def self_test() -> int:
    registry = load_json(REGISTRY)
    expected = {"cover", "about", "publisher", "contents", "back_cover"}
    missing = expected - set(registry.get("page_types", {}))
    if missing:
        print(f"missing page contracts: {sorted(missing)}", file=sys.stderr)
        return 1
    print("render validator self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, default=Path("validation/rendered-pages/render-report.json"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.artifact or not args.manifest:
        parser.error("--artifact and --manifest are required unless --self-test is used")
    return validate(args.artifact, args.manifest, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
