from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class AssetRegistryError(RuntimeError):
    pass


@dataclass(frozen=True)
class ResolvedAsset:
    asset_id: str
    path: Path
    sha256: str
    mime_type: str | None


def load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assets = data.get("assets")
    if not isinstance(assets, list):
        raise AssetRegistryError("asset registry must contain an assets list")
    ids = [item.get("asset_id") for item in assets]
    if len(ids) != len(set(ids)):
        raise AssetRegistryError("duplicate asset_id found")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_asset(asset_id: str, registry_path: Path, repository_root: Path) -> ResolvedAsset:
    registry = load_registry(registry_path)
    matches = [asset for asset in registry["assets"] if asset.get("asset_id") == asset_id]
    if not matches:
        raise AssetRegistryError(f"unknown asset: {asset_id}")

    asset = matches[0]
    if asset.get("status") != "GOLD":
        raise AssetRegistryError(f"asset is not GOLD: {asset_id}")

    expected_hash = asset.get("sha256")
    if not expected_hash:
        raise AssetRegistryError(f"asset has no verified SHA-256: {asset_id}")

    path = repository_root / asset["path"]
    if not path.is_file():
        raise AssetRegistryError(f"asset file missing: {path}")

    actual_hash = sha256_file(path)
    if actual_hash != expected_hash:
        raise AssetRegistryError(
            f"checksum mismatch for {asset_id}: expected {expected_hash}, got {actual_hash}"
        )

    for dependency in asset.get("dependencies", []):
        resolve_asset(dependency, registry_path, repository_root)

    return ResolvedAsset(asset_id, path, actual_hash, asset.get("mime_type"))


def verify_registry(registry_path: Path, repository_root: Path) -> list[str]:
    registry = load_registry(registry_path)
    verified: list[str] = []
    for asset in registry["assets"]:
        if asset.get("status") == "GOLD":
            verified.append(resolve_asset(asset["asset_id"], registry_path, repository_root).asset_id)
    return verified


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve and verify immutable EduOS assets")
    parser.add_argument("asset_id")
    parser.add_argument("--registry", default="eduos/registries/asset-registry.json")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    resolved = resolve_asset(args.asset_id, Path(args.registry), Path(args.root))
    print(json.dumps({"asset_id": resolved.asset_id, "path": str(resolved.path), "sha256": resolved.sha256}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
