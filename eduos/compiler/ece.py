from __future__ import annotations

from typing import Any

from eduos.compiler.page_object import Geometry, PageComponent, PageObject, PageObjectError
from eduos.compiler.parser import PageUnit
from eduos.compiler.planner import CompilationPlan


class EducationalCompilationError(ValueError):
    """Raised when a validated compilation plan cannot become a Page Object."""


_REGION_KIND = {
    "logo": "asset",
    "title": "text",
    "subtitle": "text",
    "hero": "asset",
    "illustration": "asset",
    "activity": "activity",
    "instruction": "text",
    "footer": "text",
    "page_number": "page_number",
}


def _payload_for_region(region_name: str, unit: PageUnit) -> dict[str, Any]:
    manifest = unit.raw_manifest
    page = manifest["page"]
    assets = manifest["assets"]

    if region_name == "logo":
        return {"asset_id": assets["logo"], "fit": "contain"}
    if region_name in {"hero", "illustration"}:
        return {"asset_id": assets["illustration"], "fit": "contain"}
    if region_name == "title":
        return {"text": unit.title, "role": "page_title"}
    if region_name == "subtitle":
        visible_text = page.get("visible_text", [])
        return {"items": visible_text[1:] if visible_text else [], "role": "supporting_text"}
    if region_name == "page_number":
        return {
            "value": page.get("number"),
            "visible": bool(page.get("show_page_number", True)),
        }
    if region_name == "footer":
        return {"items": page.get("footer_text", []), "role": "footer"}
    if region_name == "instruction":
        return {"items": page.get("visible_text", []), "role": "instruction"}
    if region_name == "activity":
        return {"activity": page.get("activity"), "role": "activity"}
    return {"role": region_name}


def build_page_object(
    unit: PageUnit,
    plan: CompilationPlan,
    resolved_template: dict[str, Any],
) -> PageObject:
    canvas = resolved_template.get("canvas", {})
    try:
        canvas_width = canvas["width_px"]
        canvas_height = canvas["height_px"]
        dpi = canvas["dpi"]
    except KeyError as exc:
        raise EducationalCompilationError(f"template canvas is incomplete: {exc}") from exc

    components: list[PageComponent] = []
    for layer in plan.layers:
        region_name = layer["region"]
        try:
            geometry = Geometry.from_region(layer["geometry"])
        except PageObjectError as exc:
            raise EducationalCompilationError(f"invalid region {region_name}: {exc}") from exc

        if geometry.x + geometry.width > canvas_width or geometry.y + geometry.height > canvas_height:
            raise EducationalCompilationError(f"region exceeds canvas: {region_name}")

        payload = _payload_for_region(region_name, unit)
        kind = _REGION_KIND.get(region_name, "container")
        component = PageComponent(
            component_id=f"{unit.prompt_id}:{region_name}",
            kind=kind,
            region=region_name,
            geometry=geometry,
            payload=payload,
        )
        components.append(component)

    component_ids = [component.component_id for component in components]
    if len(component_ids) != len(set(component_ids)):
        raise EducationalCompilationError("duplicate page component ID")

    if unit.page_type == "cover":
        page_number_components = [component for component in components if component.region == "page_number"]
        if page_number_components and any(component.payload.get("visible") for component in page_number_components):
            raise EducationalCompilationError("cover page cannot display a page number")

    return PageObject(
        prompt_id=unit.prompt_id,
        book=unit.book,
        level=unit.level,
        page_type=unit.page_type,
        template_id=unit.template_id,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        dpi=dpi,
        components=tuple(components),
        output_stem=plan.output_stem,
    )
