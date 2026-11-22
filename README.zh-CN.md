# Visual Components 开放工程工具集

[English](README.md) · [兼容性](docs/COMPATIBILITY.md) · [安装说明](docs/INSTALLATION.md)

这是一个面向 **Visual Components（工业仿真软件）** 的非官方开源工具合集，计划收录工程效率插件、Python（编程语言）脚本及机器人 OLP（离线编程）辅助工具。

> **当前状态：已增加 Blenderer XG V1 的中文/英文介绍、更新记录和发布文档；源码已经上传至 `addons/blenderer/src/`，大型素材 ZIP 仍未上传 GitHub Releases。** 下列其他插件仍为开发计划。

## 仓库目标

- 从 **Visual Components 4.10** 开始开发和验证，之后根据实际情况适配 **5.0**。
- 每个插件独立管理源代码、安装方法和兼容性。
- 公开自己拥有发布权限的代码、说明文档及测试结果。
- 通过 GitHub Releases（版本发布）提供经验证的 ZIP（压缩包）下载。

## Blenderer XG V1 — 社区修改版

[中文功能介绍与安装](addons/blenderer/README.zh-CN.md) · [English](addons/blenderer/README.md) · [更新记录](addons/blenderer/CHANGELOG.md)

面向 VC Premium OLP 4.10（Python 2.7），使用 Blender 5.3.0 进行过本地渲染测试。新增图片/视频输出目录与文件名独立设置、参数记忆、进度及取消、四套灯光和三种地板材质。原版 2.6.0 由 tangtang 按 Blender 5.2.0 设计。[作者同意公开免费上传的回复](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34?u=spacex)。**[源码已发布](addons/blenderer/src/)，但完整安装仍需要单独下载素材包；[详细下载说明](addons/blenderer/README.zh-CN.md)。素材 ZIP 尚未上传到 GitHub Releases。**

## 插件规划

| 插件 | 预期用途 | VC 4.10 | VC 5.0 | 状态 |
| --- | --- | --- | --- | --- |
| [Batch Rename（批量重命名）](addons/batch-rename/README.md) | 批量修改场景组件名称 | 尚未验证 | 尚未验证 | 规划中 |
| [Component Audit（组件检查）](addons/component-audit/README.md) | 检查组件名称、属性和结构 | 尚未验证 | 尚未验证 | 规划中 |
| [Robot TCP Checker（工具坐标检查）](addons/robot-tcp-checker/README.md) | 辅助检查机器人 TCP（工具中心点）坐标 | 尚未验证 | 尚未验证 | 规划中 |

注意：VC 4.10 与 VC 5.0 的脚本运行环境及 API（应用程序编程接口）可能不同。**不会在未测试的情况下宣称兼容。**

## 目录说明

```text
addons/                  # 各个独立插件
  batch-rename/           # 批量重命名（规划中）
    vc4.10/               # 将来存放 4.10 版本代码
    vc5.0/                # 将来存放 5.0 版本代码
  component-audit/        # 组件检查（规划中）
  robot-tcp-checker/      # 机器人 TCP 检查（规划中）
docs/                    # 安装、兼容性、发布说明
.github/ISSUE_TEMPLATE/ # 问题反馈模板
```

## 将来如何下载插件？

完成开发及测试后，访问仓库右侧 **Releases（版本发布）**，下载与实际 VC 版本匹配的 ZIP 包，按照各插件的 README（说明文件）进行安装。

**Blenderer 源码现已发布，但素材 ZIP 尚未上传。请阅读[源码与素材分开下载说明](addons/blenderer/README.zh-CN.md)，不要把仓库整体 ZIP 当成完整安装包。**

## 第三方工具使用指南

- [Blenderer：VC 4.10 仿真导出到 Blender 中文专题](docs/blenderer/README.zh-CN.md) — 含插件来源、安装教程、VC 4.10 + Blender 5.3 静态渲染实测及常见问题排查。**完整源码现已发布在 `addons/blenderer/src/`，灯光与纹理素材需要单独的 ZIP；GitHub Releases 素材包尚未上传。**

## 开源与免责声明

仓库中的原创代码和文档计划采用 [MIT License（MIT 开源许可证）](LICENSE)。其他作者的代码、模型、第三方依赖仍须遵守各自许可证。

这是**非官方独立社区项目**，与 Visual Components 厂商无隶属或官方支持关系。禁止将商业软件本体、授权信息、专有 SDK（软件开发工具包）、未经许可的 CAD（计算机辅助设计）模型等内容上传到本仓库。

问题反馈请使用 GitHub Issues（问题反馈），写明软件版本、复现步骤和错误信息，注意隐去个人或企业敏感信息。
