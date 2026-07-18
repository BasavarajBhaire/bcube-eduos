#!/usr/bin/env python3
"""Versioned production-template registry for BCube EduOS."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict

TEMPLATE_ID_RE = re.compile(r"^[A-Z_]+_V\d+\.\d+\.\d+$")


class TemplateRegistryError(ValueError):
    """Raised when a template registry or template reference is invalid."""


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class TemplateRegistry:
    def __init__(self, registry_path: str | Path) -> None:
        self.registry_path = Path(registry_path)
        with self.registry_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        self._validate_registry(payload)
        self.registry_version = payload["registry_version"]
        self.status = payload["status"]
        self.templates: Dict[str, Dict[str, Any]] = payload["templates"]

    @staticmethod
    def _validate_registry(payload: Dict[str, Any]) -> None:
        if payload.get("status") not in {"draft", "approved", "founder_locked"}:
            raise TemplateRegistryError("Invalid registry status")
        templates = payload.get("templates")
        if not isinstance(templates, dict) or not templates:
            raise TemplateRegistryError("Template registry must contain templates")
        for template_id, template in templates.items():
            if not TEMPLATE_ID_RE.fullmatch(template_id):
                raise TemplateRegistryError(f"Invalid template ID: {template_id}")
            if not isinstance(template, dict) or "page_type" not in template or "rules" not in template:
                raise TemplateRegistryError(f"Incomplete template: {template_id}")

    def resolve(self, template_id: str) -> Dict[str, Any]:
        if not TEMPLATE_ID_RE.fullmatch(template_id):
            raise TemplateRegistryError(f"Invalid template reference: {template_id}")
        return self._resolve(template_id, stack=[])

    def _resolve(self, template_id: str, stack: list[str]) -> Dict[str, Any]:
        if template_id not in self.templates:
            raise TemplateRegistryError(f"Unknown template: {template_id}")
        if template_id in stack:
            chain = " -> ".join(stack + [template_id])
            raise TemplateRegistryError(f"Template inheritance cycle: {chain}")

        template = copy.deepcopy(self.templates[template_id])
        parent_id = template.pop("extends", None)
        if parent_id:
            parent = self._resolve(parent_id, stack + [template_id])
            template = _deep_merge(parent, template)

        template["template_id"] = template_id
        template["registry_version"] = self.registry_version
        self._validate_resolved(template)
        return template

    @staticmethod
    def _validate_resolved(template: Dict[str, Any]) -> None:
        canvas = template.get("canvas")
        if canvas != {
            "width_px": 2480,
            "height_px": 3508,
            "dpi": 300,
            "orientation": "portrait",
        }:
            raise TemplateRegistryError("Resolved template must use locked A4 portrait geometry")

        regions = template.get("regions", {})
        for region_name, region in regions.items():
            x, y, width, height = (region.get(k) for k in ("x", "y", "w", "h"))
            if not all(isinstance(v, int) for v in (x, y, width, height)):
                raise TemplateRegistryError(f"Region {region_name} has non-integer geometry")
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                raise TemplateRegistryError(f"Region {region_name} has invalid geometry")
            if x + width > 2480 or y + height > 3508:
                raise TemplateRegistryError(f"Region {region_name} exceeds canvas")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Resolve a BCube EduOS versioned template")
    parser.add_argument("template_id")
    parser.add_argument(
        "--registry",
        default="eduos/registries/template-registry.json",
        help="Path to template registry JSON",
    )
    args = parser.parse_args()
    registry = TemplateRegistry(args.registry)
    print(json.dumps(registry.resolve(args.template_id), indent=2))


if __name__ == "__main__":
    main()
