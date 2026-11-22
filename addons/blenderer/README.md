# Blenderer 2.6.0 — XG V1 (VC 4.10 Community Modification)

**Export Visual Components simulation scenes to Blender for industrial images and animation.** Free community modification of Blenderer, not a standalone or official Visual Components product.

## Features

- VC scene export and PNG still renders
- Animation and MP4 output options: PNG Sequence or Direct Video
- EEVEE and Cycles render options, material mapping, lighting presets and exposure settings

## What's New in XG V1 (2026-11-22)

- Remembers Blender executable, image/video directories, filenames and commonly used settings
- Separate folder and filename selection for images and videos, open-folder shortcuts and automatic filename numbering
- Pre-export checks, progress and cancellation controls, output path and render duration feedback
- Video frame count, duration and frame rate information; FPS linked to recording step
- Four lighting presets: starry moonlight, soft overcast, equipment close-up and night shift
- Three factory-floor materials: green rubber, blue-gray epoxy and dark-gray studded rubber
- Expanded Chinese UI feedback, Blender interactive launching and geometry export optimizations

These descriptions reflect the modification's source and release notes; not every feature has been tested in every environment.

## Compatibility

- **Primary tested environment:** Visual Components Premium OLP **4.10** (Python 2.7) with Blender **5.3.0**
- The upstream 2.6.0 release by **tangtang** targeted **Blender 5.2.0 LTS**; the local 5.3.0 result is not an upstream compatibility guarantee
- Still render confirmed; all animation modes, large layouts, other GPUs and VC 5.x / Python 3 are **not fully verified**

## Installation

Copy the entire plugin folder containing `__init__.py` and `Blenderer.py` to:

```text
%USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2\
```

Restart VC and point Blenderer to `blender.exe`. Test with a simple PNG before rendering animations.

[中文说明](README.zh-CN.md) · [Changelog](CHANGELOG.md)

## Download status

**No GitHub Release installer is available yet.** Repository source downloads are not validated installer packages. A community post with an external download link is available in [post #32](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/32?u=spacex).

## Credits and redistribution

- [Original Blenderer community thread](https://forum.visualcomponents.com/t/blender-addon-blenderer/773)
- [tangtang's Blenderer 2.6.0 thread](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477)
- [tangtang's permission to share modified builds, specifying compatible versions and keeping downloads free (#34)](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34?u=spacex)

Free distribution only. The repository's MIT license does not automatically relicense Blenderer upstream code or historical third-party HDR, VCMX and texture resources.