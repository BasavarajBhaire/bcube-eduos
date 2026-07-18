from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from eduos.kernel.event_bus import EventBus
from eduos.src.asset_registry import AssetRegistryError, resolve_asset
from eduos.src.page_composer import build_plan
from eduos.src.template_registry import TemplateRegistry, TemplateRegistryError


class RuntimeFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeResult:
    status: str
    prompt_id: str
    template_id: str
    assets: tuple[str, ...]
    plan: dict[str, Any]
    events: tuple[str, ...]


class EduOSRuntime:
    def __init__(
        self,
        repository_root: Path,
        template_registry_path: Path,
        asset_registry_path: Path,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository_root = repository_root
        self.template_registry = TemplateRegistry(template_registry_path)
        self.asset_registry_path = asset_registry_path
        self.event_bus = event_bus or EventBus()

    def preflight(self, manifest: dict[str, Any]) -> RuntimeResult:
        prompt_id = manifest.get("identity", {}).get("prompt_id")
        if not prompt_id:
            raise RuntimeFailure("manifest missing identity.prompt_id")

        self.event_bus.publish("manifest.loaded", {"prompt_id": prompt_id})

        template_id = manifest.get("composition", {}).get("template")
        if not template_id:
            raise RuntimeFailure("manifest missing composition.template")

        try:
            template = self.template_registry.resolve(template_id)
        except TemplateRegistryError as exc:
            self.event_bus.publish("runtime.failed", {"stage": "template", "error": str(exc)})
            raise RuntimeFailure(str(exc)) from exc
        self.event_bus.publish("template.resolved", {"template_id": template_id})

        asset_ids = self._collect_asset_ids(manifest)
        resolved_assets: list[str] = []
        try:
            for asset_id in asset_ids:
                resolve_asset(asset_id, self.asset_registry_path, self.repository_root)
                resolved_assets.append(asset_id)
        except AssetRegistryError as exc:
            self.event_bus.publish("runtime.failed", {"stage": "assets", "error": str(exc)})
            raise RuntimeFailure(str(exc)) from exc
        self.event_bus.publish("assets.verified", {"asset_ids": resolved_assets})

        if template.get("page_type") != manifest.get("page", {}).get("type"):
            error = "template page_type does not match manifest page.type"
            self.event_bus.publish("runtime.failed", {"stage": "policy", "error": error})
            raise RuntimeFailure(error)

        plan = build_plan(manifest)
        self.event_bus.publish("composition.preflight_passed", {"prompt_id": prompt_id})

        return RuntimeResult(
            status="PREFLIGHT_PASSED",
            prompt_id=prompt_id,
            template_id=template_id,
            assets=tuple(resolved_assets),
            plan=plan,
            events=tuple(event.name for event in self.event_bus.history),
        )

    @staticmethod
    def _collect_asset_ids(manifest: dict[str, Any]) -> list[str]:
        assets = manifest.get("assets", {})
        ordered: list[str] = []
        for key in ("logo", "illustration"):
            value = assets.get(key)
            if value:
                ordered.append(value)
        ordered.extend(assets.get("characters", []))
        if len(ordered) != len(set(ordered)):
            raise RuntimeFailure("duplicate asset reference in manifest")
        return ordered


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run BCube EduOS deterministic preflight")
    parser.add_argument("manifest")
    parser.add_argument("--root", default=".")
    parser.add_argument("--templates", default="eduos/registries/template-registry.json")
    parser.add_argument("--assets", default="eduos/registries/asset-registry.json")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    runtime = EduOSRuntime(
        Path(args.root),
        Path(args.templates),
        Path(args.assets),
    )
    result = runtime.preflight(manifest)
    print(json.dumps({
        "status": result.status,
        "prompt_id": result.prompt_id,
        "template_id": result.template_id,
        "assets": result.assets,
        "events": result.events,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
