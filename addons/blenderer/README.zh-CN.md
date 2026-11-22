# Blenderer 2.6.0 — XG V1（VC 4.10 修改版）

**把 Visual Components 的三维仿真场景导入 Blender，制作工业设备效果图和仿真动画。**

这是基于社区 Blenderer 2.6.0（Python 2）的**免费修改版**，不是独立原创插件，也不是 Visual Components 官方产品。

## 主要功能

- 将 VC 仿真场景导入 Blender，进行静态 PNG 图片渲染
- 提供动画录制及 MP4 视频输出选项，可选 PNG Sequence（图片序列）和 Direct Video（直接视频）
- 支持 EEVEE（实时渲染）及 Cycles（路径追踪渲染）选项
- 支持材质转换、灯光预设、曝光和地板材质设置

## XG V1 新增与改进（2026-11-22）

| 功能 | 改进内容 |
| --- | --- |
| **设置记忆** | 记住 Blender 程序位置、图片与视频输出目录、文件名及常用参数 |
| **输出管理** | 图片和视频分别选择目录、填写文件名，一键打开保存文件夹；同名结果自动编号 |
| **渲染反馈** | 导出前检查、进度、取消操作，完成后显示路径和耗时；视频附帧数、时长与帧率 |
| **动画设置** | 帧率与录制步长联动，渲染前显示预计帧数及视频时长 |
| **灯光预设** | 新增星空月夜、阴天柔光、设备特写、夜班作业四种灯光 |
| **地板材质** | 新增绿色橡胶、蓝灰环氧地坪、深灰防滑圆点橡胶三种材质 |
| **操作体验** | 中文按钮与提示、Blender 交互打开方式优化 |
| **性能** | 整合 2026-11-20 的顶点、UV、三角面及导入流程优化 |

上述内容整理自修改版源码和随包文档，不代表所有功能已在所有环境完整实测。

## 适用版本及状态

- **主要测试环境：Visual Components Premium OLP 4.10 / Python 2.7 / Blender 5.3.0**
- 上游 Blenderer 2.6.0 由社区作者 tangtang **以 Blender 5.2.0 LTS 为目标设计**；5.3.0 为 XG V1 使用者实测环境，并非上游兼容性保证
- 静态渲染已有成功记录。视频模式、复杂场景、其他硬件配置和 VC 5.x / Python 3 **未全面验证**

## 安装

将包含 `__init__.py`、`Blenderer.py` 的完整插件文件夹放入：

```text
%USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2\
```

重启 VC，打开 Blenderer 并指定实际的 `blender.exe`。建议先测试简单场景的 PNG 图片，确认正常后再尝试短动画。安装前备份旧版，避免重复加载。

[详细安装说明](../../docs/blenderer/INSTALL_VC410.md) · [常见问题](../../docs/blenderer/TROUBLESHOOTING.md) · [更新记录](CHANGELOG.md)

## 下载方式：源码与素材分开（必读）

**本插件采用“GitHub 查看源码 + 单独下载完整素材 ZIP”的分发方式。**

| 你需要的文件 | 从哪里获取 | 用途 |
| --- | --- | --- |
| **Python 源码和界面配置** | [本仓库 `addons/blenderer/src/`](src/) | 包含 `Blenderer.py`、`__init__.py`、`defaults.xml`、XAML、CSV、SVG 等 |
| **灯光与纹理素材**（`ASSETS.zip`） | [本仓库 Releases 页面](https://github.com/spacexmax/visualcomponents-open-engineering-toolkit/releases) | 包含 `Lights/`、`Textures/` 和灯光预设；**截至当前，尚未上传此 ZIP 到 Releases，页面上还没有该附件** |
| **一包安装版** | [社区帖子 #32](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/32?u=spacex) 中的既有外部下载链接 | 这是之前提供的完整打包版本，不是上述分离式素材附件 |

> **重点：只下载 GitHub 源码无法完整运行。** 需要与 XG V1 对应的 `ASSETS.zip`，且不能将旧版的任意灯光预设直接视为兼容。素材 ZIP 上传到 Releases 后，建议附件使用名称 `Blenderer-2.6.0-XG-V1-VC4.10-ASSETS.zip`，本文会再补上指向那个附件的**直接下载地址**。

### 安装步骤（两个包合并）

1. 在 `addons/blenderer/src/` 取得全部源文件，**保持文件名不变**；或者使用同版本的 SOURCE.zip。
2. 从上述 Releases 下载**同为 XG V1 / VC 4.10** 的 ASSETS.zip。**当前尚未上传到 GitHub，无法通过 Releases 完成此步骤。**
3. 将两个包内的文件合并到**同一个 Blenderer 插件文件夹**，不要覆盖错误版本。目标结构应该是：

```text
%USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2\
└── Blenderer-XG-V1\
    ├── __init__.py
    ├── Blenderer.py
    ├── defaults.xml
    ├── BlenderAddOn_Language.py
    ├── export_from_vc.py
    ├── import_to_blender.py
    ├── material_helper.py
    ├── materials.csv
    ├── *.xaml
    ├── rBlendererIcon.svg
    ├── Lights\
    │   ├── Presets\
    │   │   └── presets.xml
    │   └── *.vcmx
    └── Textures\
```

4. 重启 VC 4.10，指定你的 `blender.exe`，先使用简单场景测试静态 PNG。

**注意：** 不要将整个仓库的 `Code → Download ZIP` 直接放进 VC 的 Python 2 目录；那个 ZIP 包含仓库其他内容，而且不含大体积素材。

## 作者、许可与致谢

- [Blenderer 原始社区讨论](https://forum.visualcomponents.com/t/blender-addon-blenderer/773)
- [tangtang 发布的 Blenderer 2.6.0](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477)
- [tangtang 同意公开上传修改版的回复（#34）](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34?u=spacex)

作者要求标明实际可用版本，并**保持免费、不得设置收费机制**。本修改版遵守免费分享原则。仓库 MIT 许可证不能自动覆盖原项目源码及历史第三方资源。