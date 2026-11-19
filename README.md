# Arrumo Plugin Registry

The official Arrumo plugin catalog and default installation list.

This repository is being initialized. See the Arrumo workspace roadmap for implementation status.

Copyright © 2026 DEVS AI Unipessoal LDA. Licensed under the [GNU Affero General Public License v3.0](LICENSE).

For custom AI solutions for your company, visit [DEVS AI](https://aidevs.pt).

The [catalog](catalog.json) records planned defaults. Entries identify source repositories. Installation will require published releases and compatibility and integrity metadata.

## Release entries

The [catalog schema](catalog.schema.json) describes the format consumed by Arrumo. Plugin IDs must be unique, and release versions must be unique within each plugin. Add to a plugin's optional `releases` array only after publishing the exact SDK ZIP. Each record declares the SemVer `version`, `manifestSchemaVersion`, HTTPS `packageUrl`, and 64-digit SHA-256 `sha256` of the published bytes. Repository and package URLs must omit credentials, query strings, and fragments.

Arrumo can use a local catalog snapshot to verify an explicitly selected release against a local ZIP. The plugin ID inside the archive must match the selected catalog entry. Obtain the catalog independently from the package so the checksum can detect a substituted archive.
