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

## 下载完整安装包（一个 ZIP 即可）

**普通用户只需下载 `Blenderer-2.6.0-XG-V1-VC4.10-FULL.zip`，无需另行下载 SOURCE.zip 或 ASSETS.zip。**

从 [GitHub Releases（版本发布）](https://github.com/spacexmax/visualcomponents-open-engineering-toolkit/releases) 找到 **Blenderer 2.6.0 XG V1 — VC 4.10**，展开下方 **Assets（附件）**，下载名称带 `FULL.zip` 的完整压缩包。里面已包含源码、配置、灯光、HDR、纹理及预设。

将 ZIP **解压**，把其中**直接包含 `__init__.py`、`Blenderer.py`、`Lights/` 和 `Textures/`** 的整个插件文件夹放进：

```text
%USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2\
```

然后重启 VC 4.10，在 Blenderer 中指定实际的 `blender.exe`；建议先测试简单场景的 PNG。

**开发者：** [这里可在线查看 Python 源码](src/)。仓库的 `Code → Download ZIP` 或 GitHub 自动生成的 `Source code (zip)` **并非完整版插件**，不要用它代替 Releases 里的 FULL.zip。

> 发布状态：FULL.zip 已上传至 GitHub Release 草稿，**尚需正式发布后，其他用户才能从 Releases 下载**。

## 作者、许可与致谢

- [Blenderer 原始社区讨论](https://forum.visualcomponents.com/t/blender-addon-blenderer/773)
- [tangtang 发布的 Blenderer 2.6.0](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477)
- [tangtang 同意公开上传修改版的回复（#34）](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34)

作者要求标明实际可用版本，并**保持免费、不得设置收费机制**。本修改版遵守免费分享原则。仓库 MIT 许可证不能自动覆盖原项目源码及历史第三方资源。