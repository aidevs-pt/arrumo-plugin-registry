"""Record a published plugin ZIP as a release in the catalog.

    python tools/add_release.py catalog.json <plugin-id> <version> <package.zip> <package-url>

The ZIP must be the exact published file. Run check_catalog.py with --release afterwards.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_catalog import check_url, check_version  # noqa: E402


def add_release(catalog_path, plugin_id, version, package, package_url):
    check_version(version)
    check_url(package_url)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    plugin = next((item for item in catalog["plugins"] if item["id"] == plugin_id), None)
    if plugin is None:
        raise ValueError(f"The catalog has no plugin {plugin_id}")
    releases = plugin.setdefault("releases", [])
    if any(release["version"] == version for release in releases):
        raise ValueError(f"{plugin_id} {version} is already in the catalog")
    data = package.read_bytes()
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read("manifest.json"))
    if manifest.get("id") != plugin_id:
        raise ValueError(f"The package is {manifest.get('id')}, not {plugin_id}")
    releases.append({
        "version": version,
        "manifestSchemaVersion": manifest["schemaVersion"],
        "packageUrl": package_url,
        "sha256": hashlib.sha256(data).hexdigest(),
    })
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return releases[-1]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("plugin_id")
    parser.add_argument("version")
    parser.add_argument("package", type=Path)
    parser.add_argument("package_url")
    args = parser.parse_args()
    try:
        release = add_release(args.catalog, args.plugin_id, args.version, args.package, args.package_url)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(release))


if __name__ == "__main__":
    main()
