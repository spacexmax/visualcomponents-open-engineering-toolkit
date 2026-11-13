# Blenderer：Visual Components 仿真场景在 Blender 中渲染

> 这是 **第三方插件的中文使用、测试与排错资料**，不是本仓库原创插件，也不是第三方软件镜像。维护日期：2026-11-13。

## 它能做什么

Blenderer 在 Visual Components（VC）中读取仿真场景和动画数据，导入 Blender 生成更高质量的图片或视频。VC 仍负责仿真和运动计算；Blender 负责渲染，**不是**在 Blender 中实时运行 VC 控制器。

常见用途：机器人工作站展示、自动化产线宣传图、课程截图、仿真动画视频。通常先验证静态图片，再进行动画录制与视频合成。

## 插件与下载来源

| 版本 | 来源及说明 | 当前建议 |
| --- | --- | --- |
| 2.1.0（2020） | 原版历史版本 | 仅备份、对照；不要与新版源码混装 |
| [2.3.0（2023）](https://forum.visualcomponents.com/t/blender-addon-blenderer/773) | 原作者社区帖子，说明以 VC 4.8 + Blender 3.6 测试 | 兼容问题时的对照方案；下载可能需信息登记 |
| [2.6.0 V2（2026）](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/16) | 社区用户 tangtang 发布的 Python 2 改版；[论坛附件 ZIP](https://forum.visualcomponents.com/uploads/short-url/rbQ3FvVM7fhF2vCSH59twOD92kN.zip) | 当前实测资料所用版本；安全性与具体授权需自行核验 |

2.6.0 V2 自带的 README 明确面向 **Blender 5.2.0 LTS** 更新，示例安装目录使用 **VC 5.0 / Python 2**。这不等于官方保证兼容 VC 4.10 或 Blender 5.3；下方仅记录本人的有限实测。

## 实际测试结论

| 测试组合 | 验证到的程度 | 尚未验证 |
| --- | --- | --- |
| VC Premium OLP **4.10.0** + Blenderer **2.6.0 V2** + Steam Blender **5.3.0**（Windows） | VC 按钮和配置面板显示正常；指定 Blender 可执行文件后，**静态 PNG 渲染成功** | 动画录制、MP4、复杂布局、持续稳定性、重新启动后全部参数持久化 |

测试时默认画面严重偏白；将 Advanced（高级）→ Exposure（曝光）从 `0` 改为 `-2` 后，这个样例的画面明显改善。**`-2` 是单场景调试值，不是通用推荐曝光。**

安装初期曾因缺少 `Lights/Presets/presets.xml` 报错，之后面板可打开；**资源究竟如何补齐尚未记录为可重复步骤**。不能据此断言 2.6.0 V2 原包完整，也不应随意混用旧版脚本或伪造 XML。

## 文档导航

- [在 VC Premium OLP 4.10 中安装与第一次渲染](INSTALL_VC410.md)
- [VC 4.10 + Blender 5.3 的实际测试记录](BLENDER_53_TEST.md)
- [常见错误与排查](TROUBLESHOOTING.md)

## 原创内容与第三方授权

本目录仅收录**原创中文说明、测试记录和排障经验**，不托管 Blenderer 的第三方 Python 脚本、打包 ZIP、灯光、纹理或其他附件。原版作者、2.6.0 修改作者及相关资产可能拥有不同权利；**未查到足以确认可再分发的明确许可证之前，不得将插件源码或附件直接上传到本仓库**。

本仓库的 MIT 许可证只适用于有权授权的原创内容，不会覆盖第三方软件。此项目不是 Visual Components、Blender Foundation 或插件作者官方发布、认可或支持的产品。

## 反馈需要提供

VC 精确版本、Blenderer 版本、Blender 版本、Windows 版本、操作步骤、VC Output（输出）日志；不要公开授权信息或公司保密工程文件。
