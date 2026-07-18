from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from eduos.compiler.parser import PageUnit


class PlanningError(ValueError):
    pass


@dataclass(frozen=True)
class CompilationPlan:
    prompt_id: str
    template_id: str
    page_type: str
    asset_ids: tuple[str, ...]
    layers: tuple[dict[str, Any], ...]
    output_stem: str


def build_compilation_plan(unit: PageUnit, resolved_template: dict[str, Any]) -> CompilationPlan:
    if resolved_template.get("page_type") != unit.page_type:
        raise PlanningError("template page_type does not match manifest page.type")

    regions = resolved_template.get("regions")
    if not isinstance(regions, dict) or not regions:
        raise PlanningError("resolved template has no regions")

    layers: list[dict[str, Any]] = []
    for region_name, region in regions.items():
        if not isinstance(region, dict):
            raise PlanningError(f"invalid region: {region_name}")
        layers.append({"region": region_name, "geometry": dict(region)})

    return CompilationPlan(
        prompt_id=unit.prompt_id,
        template_id=unit.template_id,
        page_type=unit.page_type,
        asset_ids=unit.asset_ids,
        layers=tuple(layers),
        output_stem=unit.prompt_id,
    )
