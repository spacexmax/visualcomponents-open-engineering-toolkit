# Visual Components Open Engineering Toolkit

[简体中文](README.zh-CN.md) · [Compatibility](docs/COMPATIBILITY.md) · [Installation](docs/INSTALLATION.md)

An **unofficial, community-maintained collection** of engineering productivity tools, automation scripts, and add-ons for Visual Components.

> **Current status: project scaffold only.** No working add-ons or installable releases have been published. Project ideas below are proposals, not completed features.

## Goals

- Build practical, reproducible tools for simulation, component handling, and robot offline programming (OLP).
- Track compatibility by exact Visual Components release (starting with 4.10 and 5.0).
- Publish source code, installation instructions, validation notes, and tested release ZIP packages.
- Keep each tool independent so users can install only what they need.

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

There are **no tested plugin packages yet**. Once available, download the matching ZIP from **Releases** and follow the add-on's installation guide. Downloading the repository's source ZIP is not the same as downloading a validated plugin package.

See [installation guidance](docs/INSTALLATION.md) and [release conventions](docs/RELEASING.md).

## Development and contributions

Issues and contributions are welcome. Please include the exact Visual Components version, operating system, reproduction steps, and relevant logs/screenshots, but never share license keys, private CAD models, or company-confidential data.

## License and disclaimer

Original code and documentation in this repository are offered under the [MIT License](LICENSE), unless a future file explicitly states a different license. Third-party dependencies and assets keep their own licenses.

**This is an independent community project. It is not made, endorsed, or supported by Visual Components.** Visual Components and other trademarks belong to their respective owners. No commercial software binaries, license files, or proprietary SDK packages are distributed here.
