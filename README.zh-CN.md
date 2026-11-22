# Visual Components 开放工程工具集

[English](README.md) · [兼容性](docs/COMPATIBILITY.md) · [通用安装说明](docs/INSTALLATION.md)

面向 Visual Components 的非官方工程效率工具及插件合集，按具体软件版本记录适配情况与测试范围。

## 已发布：Blenderer 2.6.0 XG V1

用于将 Visual Components 仿真场景导入 Blender，渲染工业设备效果图和动画。

**主要环境：** Visual Components Premium OLP **4.10（Python 2.7）**；Blender **5.3.0** 已有本地静态 PNG 渲染记录。动画及复杂场景尚未全面验收。

**[下载 Blenderer XG V1 完整安装包 FULL.zip](https://github.com/spacexmax/visualcomponents-open-engineering-toolkit/releases/download/blenderer-xg-v1-vc410/Blenderer-2.6.0-XG-V1-VC4.10-FULL.zip)** · [查看正式发布说明](https://github.com/spacexmax/visualcomponents-open-engineering-toolkit/releases/tag/blenderer-xg-v1-vc410)

安装只需下载 **一个 FULL.zip**，里面已经包含源码、灯光、HDR、纹理和配置。GitHub 首页的 `Code → Download ZIP` 是仓库源码包，**不能代替完整安装包**。

- [中文功能介绍及安装方法](addons/blenderer/README.zh-CN.md)
- [English README](addons/blenderer/README.md)
- [在线查看源码](addons/blenderer/src/) · [更新记录](addons/blenderer/CHANGELOG.md)
- [历史安装与测试记录](docs/blenderer/README.zh-CN.md)

**作者说明：** XG V1 是基于 tangtang 维护的 Blenderer 2.6.0 进行的**免费社区修改版**，不是 Visual Components 官方产品。[tangtang 同意公开免费上传的回复](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34)。上游版本按 Blender 5.2.0 设计，不能将当前的有限测试理解为对所有版本的兼容保证。

## 其他规划插件

| 插件 | 用途 | VC 4.10 | VC 5.0 | 状态 |
| --- | --- | --- | --- | --- |
| [Batch Rename（批量重命名）](addons/batch-rename/README.md) | 场景组件批量改名 | 未验证 | 未验证 | 规划中 |
| [Component Audit（组件检查）](addons/component-audit/README.md) | 检查名称、属性与结构 | 未验证 | 未验证 | 规划中 |
| [Robot TCP Checker（工具坐标检查）](addons/robot-tcp-checker/README.md) | 辅助核对机器人 TCP 坐标 | 未验证 | 未验证 | 规划中 |

**版本兼容必须基于实测，不推断 VC 4.10 与 VC 5.x 通用。**

## 仓库结构与反馈

- [`addons/`](addons/README.md)：已发布插件及规划中的项目
- [`docs/`](docs/INSTALLATION.md)：安装、兼容性、测试记录
- [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/)：问题反馈模板

反馈请说明 Visual Components、Blender 的精确版本、操作步骤和错误日志，注意隐去保密工程文件与软件授权信息。

## 开源声明

本仓库有权授权的原创内容按 [MIT License](LICENSE) 发布；**MIT 不会自动覆盖 Blenderer 原作者代码及第三方资源，XG V1 修改版按作者要求免费分享**。

本项目非官方独立社区项目，不代表 Visual Components 厂商。
