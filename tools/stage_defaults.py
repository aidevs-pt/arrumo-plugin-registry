#!/usr/bin/env python3
"""Stage exact registry-pinned default plugin ZIPs for an editor release build."""

import argparse
from pathlib import Path
import tempfile
import zipfile

from jsonschema import ValidationError

if __package__:
    from .check_catalog import read_catalog, verify_zip
else:
    from check_catalog import read_catalog, verify_zip


def stage_defaults(catalog_path, output, selections):
    catalog, releases = read_catalog(catalog_path)
    defaults = {plugin["id"] for plugin in catalog["plugins"] if plugin["default"]}
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Staging directory already exists: {output}")

    staged = set()
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".arrumo-defaults-") as temporary:
        pending = Path(temporary) / "packages"
        pending.mkdir()
        for plugin_id, version, archive in selections:
            if plugin_id not in defaults:
                raise ValueError(f"Plugin is absent from the default list: {plugin_id}")
            if plugin_id in staged:
                raise ValueError(f"Default plugin selected more than once: {plugin_id}")
            entries = releases[plugin_id]
            release = entries.get(version)
            if release is None:
                raise ValueError(f"Default release is absent from the catalog: {plugin_id} {version}")
            digest = release["sha256"].lower()
            if sum(entry["sha256"].lower() == digest for entry in entries.values()) != 1:
                raise ValueError(f"Default ZIP digest matches multiple releases: {plugin_id}")
            data = verify_zip(Path(archive), plugin_id, release)
            (pending / f"{plugin_id}.zip").write_bytes(data)
            staged.add(plugin_id)
        pending.rename(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path, help="new directory for verified ZIPs")
    parser.add_argument(
        "--release", nargs=3, action="append", required=True,
        metavar=("PLUGIN_ID", "VERSION", "ZIP"),
    )
    args = parser.parse_args()
    try:
        stage_defaults(args.catalog, args.output, args.release)
    except (OSError, ValueError, ValidationError, zipfile.BadZipFile, RuntimeError) as error:
        parser.exit(1, f"{error}\n")
    print(f"Staged {len(args.release)} registry default package(s) in {args.output}.")


if __name__ == "__main__":
    main()
