# Visual Components Open Engineering Toolkit

[简体中文](README.zh-CN.md) · [Compatibility](docs/COMPATIBILITY.md) · [Installation](docs/INSTALLATION.md)

An independent, unofficial collection of engineering productivity tools and add-ons for Visual Components. Releases and compatibility are tracked by exact software version.

## Available release: Blenderer 2.6.0 XG V1

**Visual Components Premium OLP 4.10 (Python 2.7) → Blender rendering**. Local testing has demonstrated static PNG rendering with Blender 5.3.0; animation and complex scenes are not fully verified.

**[Download Blenderer XG V1 — complete FULL.zip](https://github.com/spacexmax/visualcomponents-open-engineering-toolkit/releases/download/blenderer-xg-v1-vc410/Blenderer-2.6.0-XG-V1-VC4.10-FULL.zip)** · [Release notes](https://github.com/spacexmax/visualcomponents-open-engineering-toolkit/releases/tag/blenderer-xg-v1-vc410)

The complete ZIP includes source code, lights, HDR environments, and textures. **Download only FULL.zip**; the repository-wide source archive does not include those large resources.

- [Blenderer features and installation (English)](addons/blenderer/README.md)
- [Blenderer 中文功能与安装](addons/blenderer/README.zh-CN.md)
- [Browse source](addons/blenderer/src/) · [Changelog](addons/blenderer/CHANGELOG.md)
- [Historical usage/testing notes](docs/blenderer/README.zh-CN.md)

XG V1 is a **free community modification** based on Blenderer 2.6.0 maintained by tangtang, who [allowed public sharing with clear version labeling and no charging](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34). Upstream Blenderer 2.6.0 was designed around Blender 5.2.0; the XG V1 local Blender 5.3.0 test is not a general compatibility guarantee.

## Other proposed add-ons

| Add-on | Purpose | VC 4.10 | VC 5.0 | Status |
| --- | --- | --- | --- | --- |
| [Batch Rename](addons/batch-rename/README.md) | Batch-rename scene components | Not tested | Not tested | Planned |
| [Component Audit](addons/component-audit/README.md) | Review component names, properties and organization | Not tested | Not tested | Planned |
| [Robot TCP Checker](addons/robot-tcp-checker/README.md) | Assist with reviewing robot tool coordinate frames | Not tested | Not tested | Planned |

**Do not assume compatibility across Visual Components 4.10 and 5.x.** See [compatibility notes](docs/COMPATIBILITY.md).

## Repository layout

- [`addons/`](addons/README.md): released add-ons and proposed projects
- [`docs/`](docs/INSTALLATION.md): installation, compatibility and validation notes
- [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/): bug reporting templates

## Contributing and licensing

For bug reports, include VC and Blender versions, steps to reproduce and relevant output logs; do not upload private models or license information.

Original repository material is covered by the [MIT License](LICENSE) where applicable. **That license does not automatically relicense upstream Blenderer code or third-party assets**, and XG V1 is shared free of charge in accordance with the upstream maintainer's permission.

This project is independent and unofficial; it is not made, endorsed or supported by Visual Components.
