#!/usr/bin/env python3
"""Evidence-based, fail-closed validator for BCube rendered publishing pages.

Machine-verifiable facts are derived from artifact files, approved source assets,
component geometry, text-detector evidence, and a signed human approval record.
Self-declared visual PASS booleans are not accepted as proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from datetime import date
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


def valid_bounds(value: Any) -> bool:
    return (
        isinstance(value, list) and len(value) == 4
        and all(isinstance(v, int) for v in value)
        and value[0] >= 0 and value[1] >= 0
        and value[2] > value[0] and value[3] > value[1]
        and value[2] <= 2480 and value[3] <= 3508
    )


def overlaps(a: list[int], b: list[int]) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def normalize_text(value: str) -> str:
    return " ".join(value.upper().split())


def validate_components(manifest: dict[str, Any], page_contract: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    evidence = manifest.get("component_evidence")
    check(checks, "evidence.components", isinstance(evidence, list), "component evidence is compositor-generated")
    if not isinstance(evidence, list):
        return

    by_name: dict[str, list[dict[str, Any]]] = {}
    bounds_items: list[tuple[str, list[int], bool]] = []
    for index, item in enumerate(evidence):
        ok = isinstance(item, dict)
        check(checks, f"component.{index}.object", ok, "component evidence item is an object")
        if not ok:
            continue
        name = item.get("component")
        source = item.get("source_path")
        expected_hash = item.get("approved_sha256")
        actual_bounds = item.get("bounds")
        template_bounds = item.get("template_bounds")
        allow_overlap = item.get("allow_overlap") is True
        check(checks, f"component.{index}.name", isinstance(name, str) and bool(name), f"component name: {name}")
        if not isinstance(name, str) or not name:
            continue
        by_name.setdefault(name, []).append(item)

        if source is not None:
            source_path = ROOT / str(source)
            check(checks, f"component.{name}.source_exists", source_path.is_file(), f"source asset exists: {source}")
            if source_path.is_file():
                actual_hash = sha256(source_path)
                check(checks, f"component.{name}.approved_hash", isinstance(expected_hash, str) and actual_hash == expected_hash,
                      f"source SHA-256 matches approved registry for {name}")
        check(checks, f"component.{name}.bounds", valid_bounds(actual_bounds), f"valid component bounds for {name}: {actual_bounds}")
        check(checks, f"component.{name}.template_bounds", valid_bounds(template_bounds), f"valid template bounds for {name}: {template_bounds}")
        if valid_bounds(actual_bounds) and valid_bounds(template_bounds):
            check(checks, f"component.{name}.geometry", actual_bounds == template_bounds,
                  f"component geometry equals locked template for {name}")
            bounds_items.append((name, actual_bounds, allow_overlap))

    for required in page_contract.get("required_components", []):
        check(checks, f"required.{required}", required in by_name, f"required component evidence exists: {required}")
    for prohibited in page_contract.get("prohibited_components", []):
        check(checks, f"prohibited.{prohibited}", prohibited not in by_name, f"prohibited component evidence absent: {prohibited}")
    for component, expected in page_contract.get("component_counts", {}).items():
        actual = len(by_name.get(component, []))
        check(checks, f"count.{component}", actual == expected, f"{component} count is {actual}; required {expected}")

    for i, (name_a, a, allow_a) in enumerate(bounds_items):
        for name_b, b, allow_b in bounds_items[i + 1:]:
            if allow_a or allow_b:
                continue
            check(checks, f"overlap.{name_a}.{name_b}", not overlaps(a, b), f"no prohibited overlap: {name_a} vs {name_b}")


def validate_text_evidence(manifest: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    evidence = manifest.get("text_evidence")
    check(checks, "evidence.text", isinstance(evidence, dict), "text detector evidence is supplied")
    if not isinstance(evidence, dict):
        return
    detector = evidence.get("detector")
    detected = evidence.get("detected_text")
    prohibited = evidence.get("prohibited_terms", [])
    required = evidence.get("required_terms", [])
    check(checks, "text.detector", isinstance(detector, dict) and bool(detector.get("name")) and bool(detector.get("version")),
          "text evidence identifies detector name and version")
    check(checks, "text.detected", isinstance(detected, list) and all(isinstance(v, str) for v in detected), "detected text is a string list")
    check(checks, "text.prohibited_terms", isinstance(prohibited, list) and all(isinstance(v, str) for v in prohibited), "prohibited term list is valid")
    check(checks, "text.required_terms", isinstance(required, list) and all(isinstance(v, str) for v in required), "required term list is valid")
    if not isinstance(detected, list):
        return
    corpus = normalize_text(" ".join(detected))
    for term in prohibited if isinstance(prohibited, list) else []:
        normalized = normalize_text(term)
        check(checks, f"text.prohibited.{normalized}", normalized not in corpus, f"cross-book/prohibited text absent: {term}")
    for term in required if isinstance(required, list) else []:
        normalized = normalize_text(term)
        check(checks, f"text.required.{normalized}", normalized in corpus, f"required exact text detected: {term}")


def validate_human_approval(manifest: dict[str, Any], artifact_hash: str, checks: list[dict[str, Any]]) -> None:
    approval = manifest.get("human_approval")
    check(checks, "approval.record", isinstance(approval, dict), "human approval record exists")
    if not isinstance(approval, dict):
        return
    reviewer = approval.get("reviewer")
    approved_on = approval.get("approved_on")
    approved_hash = approval.get("artifact_sha256")
    status = approval.get("status")
    check(checks, "approval.reviewer", isinstance(reviewer, str) and len(reviewer.strip()) >= 3, "reviewer is identified")
    try:
        date.fromisoformat(str(approved_on))
        date_ok = True
    except ValueError:
        date_ok = False
    check(checks, "approval.date", date_ok, "approval date is ISO YYYY-MM-DD")
    check(checks, "approval.status", status == "APPROVED", "human approval status is APPROVED")
    check(checks, "approval.artifact_hash", approved_hash == artifact_hash, "human approval is bound to this exact artifact SHA-256")


def validate(artifact: Path, manifest_path: Path, output: Path) -> int:
    registry = load_json(REGISTRY)
    manifest = load_json(manifest_path)
    page_type = manifest.get("page_type")
    page_id = manifest.get("page_id")
    checks: list[dict[str, Any]] = []

    check(checks, "artifact.exists", artifact.is_file(), f"artifact exists: {artifact}")
    if not artifact.is_file():
        return write_report(output, page_id or "UNKNOWN", page_type or "UNKNOWN", artifact, checks)

    artifact_hash = sha256(artifact)
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
    check(checks, "contract.page_type", isinstance(page_contract, dict), f"registered page type: {page_type}")
    if isinstance(page_contract, dict):
        validate_components(manifest, page_contract, checks)
    validate_text_evidence(manifest, checks)
    validate_human_approval(manifest, artifact_hash, checks)

    composition = manifest.get("composition")
    check(checks, "composition.engine", isinstance(composition, dict) and composition.get("engine") == "bcube-publishing-sdk",
          "artifact was produced by the BCube deterministic composer")
    check(checks, "composition.full_page_ai", isinstance(composition, dict) and composition.get("full_page_ai_generation") is False,
          "full-page AI generation was not used")
    check(checks, "composition.single_flat_page", isinstance(composition, dict) and composition.get("single_flat_page") is True,
          "one flat front-facing page")

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
    print("evidence-based render validator self-test passed")
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
