from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eduos.compiler.parser import PageUnit, parse_manifest
from eduos.compiler.planner import CompilationPlan, build_compilation_plan
from eduos.src.asset_registry import AssetRegistryError, resolve_asset
from eduos.src.template_registry import TemplateRegistry, TemplateRegistryError


class CompilationError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompilationResult:
    status: str
    unit: PageUnit
    plan: CompilationPlan
    verified_assets: tuple[str, ...]


class EducationalCompiler:
    def __init__(
        self,
        repository_root: Path,
        template_registry_path: Path | None = None,
        asset_registry_path: Path | None = None,
    ) -> None:
        self.repository_root = repository_root
        self.template_registry_path = template_registry_path or repository_root / "eduos/registries/template-registry.json"
        self.asset_registry_path = asset_registry_path or repository_root / "eduos/registries/asset-registry.json"

    def compile(self, manifest_path: Path) -> CompilationResult:
        unit = parse_manifest(manifest_path)

        try:
            template = TemplateRegistry(self.template_registry_path).resolve(unit.template_id)
        except TemplateRegistryError as exc:
            raise CompilationError(str(exc)) from exc

        verified_assets: list[str] = []
        try:
            for asset_id in unit.asset_ids:
                resolve_asset(asset_id, self.asset_registry_path, self.repository_root)
                verified_assets.append(asset_id)
        except AssetRegistryError as exc:
            raise CompilationError(str(exc)) from exc

        try:
            plan = build_compilation_plan(unit, template)
        except ValueError as exc:
            raise CompilationError(str(exc)) from exc

        return CompilationResult(
            status="COMPILED",
            unit=unit,
            plan=plan,
            verified_assets=tuple(verified_assets),
        )
