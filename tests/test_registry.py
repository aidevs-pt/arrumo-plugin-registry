import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.check_catalog import load_catalog, verify_zip
from tools.stage_defaults import stage_defaults


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.catalog = self.root / "catalog.json"
        self.archive = self.root / "plugin.zip"
        self.write_package("fixture", 1)

    def write_package(self, plugin_id, schema_version):
        with zipfile.ZipFile(self.archive, "w") as package:
            package.writestr("manifest.json", json.dumps({
                "id": plugin_id,
                "schemaVersion": schema_version,
            }))
        self.release = {
            "version": "1.0.0",
            "manifestSchemaVersion": 1,
            "packageUrl": "https://example.org/fixture.zip",
            "sha256": hashlib.sha256(self.archive.read_bytes()).hexdigest(),
        }
        self.plugin = {
            "id": "fixture",
            "repository": "https://example.org/source",
            "default": False,
            "releases": [self.release],
        }

    def write_catalog(self, *plugins):
        self.catalog.write_text(json.dumps({"schemaVersion": 1, "plugins": plugins}), encoding="utf-8")

    def test_verifies_exact_zip(self):
        self.write_catalog(self.plugin)
        catalog = load_catalog(self.catalog)
        verify_zip(self.archive, "fixture", catalog["fixture"]["1.0.0"])
        with self.archive.open("ab") as package:
            package.write(b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            verify_zip(self.archive, "fixture", self.release)

    def test_requires_matching_identity_and_manifest_schema(self):
        self.write_package("another-plugin", 1)
        with self.assertRaisesRegex(ValueError, "Plugin ID"):
            verify_zip(self.archive, "fixture", self.release)
        self.write_package("fixture", 2)
        with self.assertRaisesRegex(ValueError, "schema version"):
            verify_zip(self.archive, "fixture", self.release)

    def test_rejects_duplicate_plugins_and_releases(self):
        self.write_catalog(self.plugin, self.plugin)
        with self.assertRaisesRegex(ValueError, "duplicate plugin ID"):
            load_catalog(self.catalog)
        self.plugin["releases"].append(self.release)
        self.write_catalog(self.plugin)
        with self.assertRaisesRegex(ValueError, "Duplicate release version"):
            load_catalog(self.catalog)

    def test_rejects_credentials_and_noncanonical_versions(self):
        self.write_catalog(dict(self.plugin, repository="https://user@example.org/source"))
        with self.assertRaisesRegex(ValueError, "credentials"):
            load_catalog(self.catalog)
        self.release["version"] = "1.0.0-01"
        self.write_catalog(self.plugin)
        with self.assertRaisesRegex(ValueError, "SemVer"):
            load_catalog(self.catalog)

    def test_stages_exact_selected_default_bytes(self):
        self.write_catalog(dict(self.plugin, default=True))
        output = self.root / "staged"
        selection = [("fixture", "1.0.0", self.archive)]
        stage_defaults(self.catalog, output, selection)
        self.assertEqual((output / "fixture.zip").read_bytes(), self.archive.read_bytes())
        with self.assertRaises(FileExistsError):
            stage_defaults(self.catalog, output, selection)

    def test_rejects_non_defaults_and_ambiguous_release_digests(self):
        self.write_catalog(self.plugin)
        output = self.root / "staged"
        selection = [("fixture", "1.0.0", self.archive)]
        with self.assertRaisesRegex(ValueError, "default list"):
            stage_defaults(self.catalog, output, selection)
        second_release = dict(self.release, version="2.0.0")
        self.write_catalog(dict(self.plugin, default=True, releases=[self.release, second_release]))
        with self.assertRaisesRegex(ValueError, "multiple releases"):
            stage_defaults(self.catalog, output, selection)
        self.assertFalse(output.exists())

    def test_failed_batch_leaves_no_partial_output(self):
        other = dict(self.plugin, id="other", default=True)
        self.write_catalog(dict(self.plugin, default=True), other)
        output = self.root / "staged"
        with self.assertRaisesRegex(ValueError, "Plugin ID"):
            stage_defaults(self.catalog, output, [
                ("fixture", "1.0.0", self.archive),
                ("other", "1.0.0", self.archive),
            ])
        self.assertFalse(output.exists())
        self.assertFalse(list(self.root.glob(".arrumo-defaults-*")))
