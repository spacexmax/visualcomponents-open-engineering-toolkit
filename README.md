# Visual Components Open Engineering Toolkit

[简体中文](README.zh-CN.md) · [Compatibility](docs/COMPATIBILITY.md) · [Installation](docs/INSTALLATION.md)

An **unofficial, community-maintained collection** of engineering productivity tools, automation scripts, and add-ons for Visual Components.

> **Current status:** Blenderer XG V1 source and documentation are now available in this repository; the complete FULL.zip is attached to a **draft Release**, pending publication. The other add-on ideas remain proposals.

## Goals

- Build practical, reproducible tools for simulation, component handling, and robot offline programming (OLP).
- Track compatibility by exact Visual Components release (starting with 4.10 and 5.0).
- Publish source code, installation instructions, validation notes, and tested release ZIP packages.
- Keep each tool independent so users can install only what they need.

## Blenderer XG V1 — community modification

[Features and installation (English)](addons/blenderer/README.md) · [中文功能介绍](addons/blenderer/README.zh-CN.md) · [Changelog](addons/blenderer/CHANGELOG.md)

For VC Premium OLP 4.10 (Python 2.7) and locally tested with Blender 5.3.0. Features include separately configured image/video output folders and filenames, persistent settings, progress and cancel UI, four new light presets and three floor materials. The upstream author designed the 2.6.0 version for Blender 5.2.0. [Permission to share the modification](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34) requires correct version labeling and free access. [Browse XG V1 source](addons/blenderer/src/) and [download instructions](addons/blenderer/README.md). The complete FULL.zip is uploaded to the draft Release and will be available after publication.

## Proposed add-ons

| Add-on | Purpose | VC 4.10 | VC 5.0 | Status |
| --- | --- | --- | --- | --- |
| [Batch Rename](addons/batch-rename/README.md) | Batch-rename scene components | Not tested | Not tested | Planned |
| [Component Audit](addons/component-audit/README.md) | Check component names, properties and organization | Not tested | Not tested | Planned |
| [Robot TCP Checker](addons/robot-tcp-checker/README.md) | Assist with reviewing robot tool coordinate frames | Not tested | Not tested | Planned |

**Compatibility rule:** A version appears as supported only after installation and functional tests on that exact release. VC 5.x is **not** assumed compatible with VC 4.10 or every other 5.x version.

## Structure

```text
addons/
  batch-rename/
    README.md
    vc4.10/       # version-specific source will go here
    vc5.0/        # version-specific source will go here
  component-audit/
  robot-tcp-checker/
docs/
  COMPATIBILITY.md
  INSTALLATION.md
  RELEASING.md
.github/ISSUE_TEMPLATE/
```

## Download and installation

The Blenderer source is available in [addons/blenderer/src/](addons/blenderer/src/); the complete FULL.zip is attached to a **draft Release**, pending publication. Follow the [single-archive installation instructions](addons/blenderer/README.md); the repository's source ZIP is not a complete plugin installer. Once available, download the matching ZIP from **Releases** and follow the add-on's installation guide. Downloading the repository's source ZIP is not the same as downloading a validated plugin package.

See [installation guidance](docs/INSTALLATION.md) and [release conventions](docs/RELEASING.md).

## Community guides and verified workflows

- [Blenderer: VC 4.10 → Blender rendering (Chinese guide)](docs/blenderer/README.zh-CN.md) — third-party add-on guide, installation notes, observed VC 4.10 + Blender 5.3 PNG test results, and troubleshooting. **Source files are now available in addons/blenderer/src; the complete FULL.zip has been uploaded to the draft Release and is awaiting publication.** Animation support is not yet validated.

## Development and contributions

Issues and contributions are welcome. Please include the exact Visual Components version, operating system, reproduction steps, and relevant logs/screenshots, but never share license keys, private CAD models, or company-confidential data.

## License and disclaimer

Original code and documentation in this repository are offered under the [MIT License](LICENSE), unless a future file explicitly states a different license. Third-party dependencies and assets keep their own licenses.

**This is an independent community project. It is not made, endorsed, or supported by Visual Components.** Visual Components and other trademarks belong to their respective owners. No commercial software binaries, license files, or proprietary SDK packages are distributed here.
