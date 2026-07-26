from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationReport:
    page_id: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "page_id": self.page_id,
            "status": "PASS" if self.passed else "FAIL",
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_page_contract(page: dict[str, Any], registered_renderers: set[str]) -> ValidationReport:
    page_id = str(page.get("identity", {}).get("page_id", "UNKNOWN"))
    report = ValidationReport(page_id)

    validation = page.get("validation", {})
    if validation.get("status") != "READY":
        report.errors.append("Page status is not READY")
    if validation.get("allow_fallback") is not False:
        report.errors.append("allow_fallback must be false")
    if validation.get("illustration_contract_aligned") is not True:
        report.errors.append("illustration_contract_aligned must be true")

    activity = page.get("activity", {})
    render_kind = activity.get("render_kind")
    if not render_kind:
        report.errors.append("activity.render_kind is required")
    elif render_kind not in registered_renderers:
        report.errors.append(f"No renderer registered for {render_kind}")

    illustration = page.get("illustration", {})
    assets = illustration.get("assets", [])
    crops = illustration.get("asset_crops", {})
    if not assets:
        report.errors.append("illustration.assets is empty")
    if set(assets) != set(crops):
        report.errors.append("illustration.assets must exactly match asset_crops keys")

    mechanics = activity.get("mechanics")
    if not isinstance(mechanics, dict) or not mechanics:
        report.errors.append("activity.mechanics must be a non-empty object")

    layout = page.get("layout", {})
    for key in ("parent_panel", "home_connection", "generic_response_panel"):
        if layout.get(key) is not False:
            report.errors.append(f"layout.{key} must be false")

    cue = page.get("guidance", {}).get("teacher_cue", "")
    if not str(cue).strip():
        report.errors.append("guidance.teacher_cue is required")

    return report
