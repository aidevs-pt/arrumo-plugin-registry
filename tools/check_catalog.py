#!/usr/bin/env python3
"""Validate an Arrumo registry catalog and optionally verify a release ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import zipfile

from jsonschema import Draft202012Validator, ValidationError

MAX_CATALOG = 1024 * 1024
MAX_PACKAGE = 16 * 1024 * 1024
MAX_MANIFEST = 64 * 1024
SCHEMA = Path(__file__).resolve().parent.parent / "catalog.schema.json"
IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
VERSION = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)


def unique_fields(pairs):
    fields = {}
    for name, value in pairs:
        if name in fields:
            raise ValueError(f"Duplicate JSON field: {name}")
        fields[name] = value
    return fields


def read_limited(file, limit, label):
    data = file.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"{label} exceeds {limit} bytes")
    return data


def check_url(value):
    url = urlsplit(value)
    if (
        not value.startswith("https://")
        or not url.hostname
        or "@" in url.netloc
        or any(c in "\\?#" or c.isspace() or ord(c) < 32 or 127 <= ord(c) <= 159 for c in value)
    ):
        raise ValueError("Expected an HTTPS URL with no credentials, query, or fragment")
    # Accessing the port validates its numeric range.
    _ = url.port


def check_version(value):
    match = VERSION.fullmatch(value)
    if not match or any(int(part) >= 2**64 for part in match.groups()[:3]):
        raise ValueError(f"Invalid SemVer version: {value}")
    prerelease = match[4]
    if prerelease and any(
        part.isdigit() and part.startswith("0") and len(part) > 1
        for part in prerelease.split(".")
    ):
        raise ValueError(f"Invalid SemVer prerelease version: {value}")


def load_catalog(path):
    with path.open("rb") as file:
        data = read_limited(file, MAX_CATALOG, "Catalog")
    catalog = json.loads(data.decode("utf-8"), object_pairs_hook=unique_fields)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(catalog)
    if type(catalog["schemaVersion"]) is not int:
        raise ValueError("Catalog schemaVersion must be an integer")

    plugins = {}
    for plugin in catalog["plugins"]:
        plugin_id = plugin["id"]
        if not IDENTIFIER.fullmatch(plugin_id) or plugin_id in plugins:
            raise ValueError(f"Invalid or duplicate plugin ID: {plugin_id}")
        check_url(plugin["repository"])
        releases = {}
        for release in plugin.get("releases", []):
            version = release["version"]
            check_version(version)
            if version in releases:
                raise ValueError(f"Duplicate release version for {plugin_id}: {version}")
            if type(release["manifestSchemaVersion"]) is not int:
                raise ValueError(f"Invalid manifest schema version for {plugin_id} {version}")
            if not re.fullmatch(r"[0-9A-Fa-f]{64}", release["sha256"]):
                raise ValueError(f"Invalid SHA-256 for {plugin_id} {version}")
            check_url(release["packageUrl"])
            releases[version] = release
        plugins[plugin_id] = releases
    return plugins


def verify_zip(path, plugin_id, release):
    from io import BytesIO

    with path.open("rb") as file:
        data = read_limited(file, MAX_PACKAGE, "Package")
    if hashlib.sha256(data).hexdigest() != release["sha256"].lower():
        raise ValueError("Package SHA-256 differs from the catalog")
    with zipfile.ZipFile(BytesIO(data)) as archive:
        manifests = [entry for entry in archive.infolist() if entry.filename == "manifest.json"]
        if len(manifests) != 1:
            raise ValueError("Package must contain exactly one root manifest.json")
        with archive.open(manifests[0]) as manifest_file:
            manifest = json.loads(
                read_limited(manifest_file, MAX_MANIFEST, "Manifest").decode("utf-8"),
                object_pairs_hook=unique_fields,
            )
    if not isinstance(manifest, dict) or manifest.get("id") != plugin_id:
        raise ValueError("Plugin ID differs from the catalog")
    version = manifest.get("schemaVersion")
    if type(version) is not int or version != release["manifestSchemaVersion"]:
        raise ValueError("Manifest schema version differs from the catalog")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--release", nargs=3, metavar=("PLUGIN_ID", "VERSION", "ZIP"))
    args = parser.parse_args()
    try:
        plugins = load_catalog(args.catalog)
        if args.release:
            plugin_id, version, path = args.release
            release = plugins.get(plugin_id, {}).get(version)
            if release is None:
                raise ValueError("Requested plugin release is absent from the catalog")
            verify_zip(Path(path), plugin_id, release)
    except (OSError, ValueError, ValidationError, zipfile.BadZipFile, RuntimeError) as error:
        parser.exit(1, f"{error}\n")
    print("Registry validation passed.")


if __name__ == "__main__":
    main()
