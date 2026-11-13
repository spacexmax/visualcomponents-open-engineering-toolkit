# Blenderer 常见问题与排查（VC 4.10）

本页根据 VC Premium OLP 4.10.0 + Blenderer 2.6.0 V2 + Blender 5.3.0 的有限实测整理。先保存 VC Output（输出）日志，再针对现象操作；不要同时修改多个版本或配置项。

## 1. VC 找不到 Blenderer 按钮

检查插件目录是否在 `Documents\Visual Components\4.10\My Commands\Python 2\`，且插件文件夹内直接含 `__init__.py`。禁用重复的 Blenderer 版本；关闭并重启 VC 后查看 Output。

## 2. 点击按钮后报 `Lights\Presets\presets.xml` 不存在

示例报错：`IOError: [Errno 2] No such file or directory`。插件在初始化时尝试读取灯光预设文件，但当前安装路径下没有该资源。**这是文件/资源问题，不是已证实的 Blender 5.3 问题。**

先核对完整文件结构及发布者的安装说明。如果新版 ZIP 缺少资源，联系原发布者获取准确依赖。不要自行伪造 XML，也不要直接认定 2.1/2.3 的资源可以混用。

## 3. `Failed to locate Blender executable`

选择 Yes（是），通过文件窗口指定 Blender 的实际 `blender.exe`。在 Steam → Blender → 属性 → 已安装文件 → 浏览中查找。路径必须指向可执行文件，不能只是父文件夹。

## 4. PNG 非常白、细节消失

先把 Advanced（高级）→ Exposure（曝光）从 `0` 临时改为 `-2` 作对照（该值仅在某个本机样例中改善画面）。如果仍然过曝，再检查 `3 Light Studio` 等灯光预设、Materials（材质）模式与场景环境。

## 5. 输出文件路径对话框只有“打开”

`...` 可能调用“选择文件”的对话框，不是目录选择器。先取消窗口，尝试在“输出文件”白色输入框中直接写**带 `.png` 文件名的完整路径**；提前创建目标文件夹。

## 6. 重新启动后输出路径/曝光又恢复

插件可能重新加载默认配置；目前尚未确认 2.6.0 V2 的持久化机制。备份 `defaults.xml`，检查插件源码中的配置字段、保存触发条件，再用“关闭 VC → 重启 → 验证”的方式确认。不要猜测 XML 字段后直接改写。

## 7. Blender 能打开但 VC 窗口似乎卡住

论坛有用户反馈 Blender 进程保持打开期间 VC 界面需要等待。先检查是否启用 `Open in Blender（在 Blender 中打开）`；渲染测试时建议取消勾选。仅凭界面等待不能认定 VC 崩溃，应先查看进程和 Output 日志。

## 8. 静态图成功，但动画没有视频

动画录制及 MP4 **尚未本机验证**。2.6.0 V2 的说明提供 PNG Sequence 和 Direct Video 两种模式，正式处理前先用有确定运动的 2～3 秒场景测试，核对录制时间、输出文件和日志。

## 版本与来源

- [原版 Blenderer 2.3.0 社区帖](https://forum.visualcomponents.com/t/blender-addon-blenderer/773)（作者标注 VC 4.8 + Blender 3.6 测试）
- [社区 Blenderer 2.6.0 V2 帖及附件](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/16)（修改版 README 指向 Blender 5.2）
- [资料首页](README.zh-CN.md) · [本机测试记录](BLENDER_53_TEST.md)
