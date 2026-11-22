# Arrumo Plugin Registry

The official Arrumo plugin catalog and default installation list.

Copyright © 2026 DEVS AI Unipessoal LDA. Licensed under the [GNU Affero General Public License v3.0](LICENSE).

For custom AI solutions for your company, visit [DEVS AI](https://aidevs.pt).

The [catalog](catalog.json) identifies source repositories and selects the defaults to include in editor builds. Published package records specify the supported manifest version and the exact ZIP digest.

## Plugin guides

[English](https://github.com/aidevs-pt/arrumo-docs/blob/main/content/docs/en/plugins/index.md) · [Español](https://github.com/aidevs-pt/arrumo-docs/blob/main/content/docs/es/plugins/index.md) · [Português](https://github.com/aidevs-pt/arrumo-docs/blob/main/content/docs/pt/plugins/index.md)

## Release entries

The [catalog schema](catalog.schema.json) describes the format consumed by Arrumo. Plugin IDs must be unique, and release versions must be unique within each plugin. Add to a plugin's optional `releases` array only after publishing the exact SDK ZIP. Each record declares the SemVer `version`, `manifestSchemaVersion`, HTTPS `packageUrl`, and 64-digit SHA-256 `sha256` of the published bytes. Repository and package URLs must omit credentials, query strings, and fragments.

Arrumo can use a local catalog snapshot to verify an explicitly selected release against a local ZIP. The plugin ID inside the archive must match the selected catalog entry. Obtain the catalog independently from the package so the checksum can detect a substituted archive.

Catalogs can list releases for different manifest schema versions. Hosts can display all available versions and should refuse to install releases requiring a manifest schema they do not support.

## Validate changes

Install `jsonschema` for Python and run `python tools/check_catalog.py catalog.json`. CI runs this check on pushes and pull requests. It checks the catalog schema, IDs, release versions, source URLs, and checksums.

Before adding a release, run `python tools/check_catalog.py catalog.json --release <plugin-id> <version> <package.zip>` against the exact ZIP. This compares the file's SHA-256, plugin ID, and manifest schema version with the catalog. Test the ZIP in Arrumo as well to exercise the host's package validation.

## Stage defaults for an editor build

Use the catalog snapshot and exact downloaded ZIPs as build inputs. Repeat `--release` for each default with executable code or provider adapters selected for this build. Catalog entries that only supply manifest metadata require no ZIP.

```sh
python tools/stage_defaults.py catalog.json /tmp/arrumo-default-packages \
  --release example-plugin 1.0.0 /path/to/downloaded-release.zip
```

The command writes the verified bytes to `<plugin-id>.zip` in a new directory after every selection passes validation. Set `ARRUMO_PLUGIN_REGISTRY` to the absolute path to the catalog snapshot and `ARRUMO_PLUGIN_RELEASE_ROOT` to the staged directory when building the editor. The matching plugin checkouts provide the default manifests. The editor rechecks the digest and records release provenance.
