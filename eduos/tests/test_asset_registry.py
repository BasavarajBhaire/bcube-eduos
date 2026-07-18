import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from eduos.src.asset_registry import AssetRegistryError, resolve_asset


class AssetRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.asset = self.root / "logo.png"
        self.asset.write_bytes(b"official-logo-bytes")
        self.digest = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        self.registry = self.root / "registry.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write_registry(self, status="GOLD", checksum=None):
        self.registry.write_text(json.dumps({
            "registry_version": "1.0.0",
            "assets": [{
                "asset_id": "LOGO_BCUBE.PRIMARY.V1.0.0",
                "family": "LOGO_BCUBE",
                "variant": "PRIMARY",
                "version": "1.0.0",
                "type": "BRAND",
                "status": status,
                "path": "logo.png",
                "sha256": checksum,
                "dependencies": []
            }]
        }), encoding="utf-8")

    def test_resolves_gold_asset_with_matching_checksum(self):
        self.write_registry(checksum=self.digest)
        resolved = resolve_asset("LOGO_BCUBE.PRIMARY.V1.0.0", self.registry, self.root)
        self.assertEqual(resolved.sha256, self.digest)

    def test_rejects_non_gold_asset(self):
        self.write_registry(status="REVIEW", checksum=self.digest)
        with self.assertRaises(AssetRegistryError):
            resolve_asset("LOGO_BCUBE.PRIMARY.V1.0.0", self.registry, self.root)

    def test_rejects_missing_checksum(self):
        self.write_registry(checksum=None)
        with self.assertRaises(AssetRegistryError):
            resolve_asset("LOGO_BCUBE.PRIMARY.V1.0.0", self.registry, self.root)

    def test_rejects_checksum_drift(self):
        self.write_registry(checksum="0" * 64)
        with self.assertRaises(AssetRegistryError):
            resolve_asset("LOGO_BCUBE.PRIMARY.V1.0.0", self.registry, self.root)

    def test_rejects_unknown_asset(self):
        self.write_registry(checksum=self.digest)
        with self.assertRaises(AssetRegistryError):
            resolve_asset("STAR.WAVE.V1.0.0", self.registry, self.root)


if __name__ == "__main__":
    unittest.main()
