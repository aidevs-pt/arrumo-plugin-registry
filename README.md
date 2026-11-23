<p align="center">
  <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-video-editor/main/public/arrumo-icon.svg" width="88" height="88" alt="">
</p>

<h1 align="center">Arrumo Plugin Registry</h1>

<p align="center">The official plugin catalog for <b>Arrumo AI Video Editor</b>: where each plugin comes from, its digest-checked releases, and which ones ship by default.</p>

<p align="center">
  <a href="LICENSE"><img alt="License: AGPL-3.0" src="https://img.shields.io/badge/license-AGPL--3.0-2337B4"></a>
  <img alt="Official plugins: 7" src="https://img.shields.io/badge/official%20plugins-7-111">
</p>

<p align="center">
  <a href="#official-plugins"><b>Official plugins</b></a> · <a href="https://github.com/aidevs-pt/arrumo-plugin-sdk">Plugin SDK</a> · <a href="https://www.aidevs.pt/tools/arrumo/docs/plugins">Guides</a>
</p>

## Official plugins

| | Plugin | What it adds | Guide |
| --- | --- | --- | --- |
| <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-plugin-claude-code/main/icon.svg" width="28" alt=""> | [Claude Code](https://github.com/aidevs-pt/arrumo-plugin-claude-code) | The agent that writes, designs and cuts videos, on your Claude plan | [Set up](https://www.aidevs.pt/tools/arrumo/docs/plugins/claude-code/setup) |
| <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-plugin-codex/main/icon.svg" width="28" alt=""> | [Codex](https://github.com/aidevs-pt/arrumo-plugin-codex) | The same agent work on your ChatGPT plan, plus images | [Set up](https://www.aidevs.pt/tools/arrumo/docs/plugins/codex/setup) |
| <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-plugin-elevenlabs/main/icon.svg" width="28" alt=""> | [ElevenLabs](https://github.com/aidevs-pt/arrumo-plugin-elevenlabs) | Narration, music, sound effects, transcription and dubbing | [Narration](https://www.aidevs.pt/tools/arrumo/docs/plugins/elevenlabs/narration) |
| <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-plugin-higgsfield/main/icon.svg" width="28" alt=""> | [Higgsfield](https://github.com/aidevs-pt/arrumo-plugin-higgsfield) | Video clips and images from 45 video and 15 image models | [Clips and images](https://www.aidevs.pt/tools/arrumo/docs/plugins/higgsfield/video-and-images) |
| <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-plugin-openai/main/icon.svg" width="28" alt=""> | [OpenAI](https://github.com/aidevs-pt/arrumo-plugin-openai) | Transcription with timestamps and images | [Images](https://www.aidevs.pt/tools/arrumo/docs/plugins/openai/images) |
| <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-plugin-gemini/main/icon.svg" width="28" alt=""> | [Gemini](https://github.com/aidevs-pt/arrumo-plugin-gemini) | Images | [Images](https://www.aidevs.pt/tools/arrumo/docs/plugins/gemini/images) |
| <img src="https://raw.githubusercontent.com/aidevs-pt/arrumo-plugin-auto-dubbing/main/icon.svg" width="28" alt=""> | [Auto-Dubbing](https://github.com/aidevs-pt/arrumo-plugin-auto-dubbing) | Dubbed versions and translated subtitles | [Dub a video](https://www.aidevs.pt/tools/arrumo/docs/plugins/auto-dubbing/dub-a-video) |

Every plugin above comes installed with Arrumo; creators turn each one on or off in **Settings › Plugins**. Guides are in [English](https://www.aidevs.pt/tools/arrumo/docs/plugins), [Español](https://www.aidevs.pt/es/tools/arrumo/docs/plugins) and [Português](https://www.aidevs.pt/pt/tools/arrumo/docs/plugins). To write your own, start with the [Plugin SDK](https://github.com/aidevs-pt/arrumo-plugin-sdk).

## The catalog

The [catalog](catalog.json) identifies source repositories and selects the defaults to include in editor builds. Published package records specify the supported manifest version and the exact ZIP digest.

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

## License

Copyright © 2026 DEVS AI Unipessoal LDA. Licensed under the [GNU Affero General Public License v3.0](LICENSE). Part of [Arrumo AI Video Editor](https://github.com/aidevs-pt/arrumo-video-editor), built by [DEVS AI](https://aidevs.pt), who make custom AI solutions for companies.
