# Blenderer 2.6.0 V2：VC 4.10 安装与首张图片测试

> 安装对象：Visual Components Premium OLP **4.10.0**，Python 2 Add-on。**仅已确认静态渲染，不代表所有功能兼容。** 请先备份原有插件和设置。

## 1. 准备

- VC 4.10 已安装；Blenderer 2.6.0 V2 从[论坛作者回复](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/16)获取，保留原始 ZIP 备份。
- Blender 端：该改版 README 指定 **Blender 5.2.0 LTS**；本机曾用 Steam **Blender 5.3.0** 成功输出一张静态 PNG，但这是有限实测，不等同于官方支持。
- 旧版 Blenderer 2.1/2.3 如已安装，先完整备份并禁用，防止插件命令冲突。不要混装不同版本的 `.py`。

## 2. VC 插件目录

完全退出 VC，将**直接包含 `__init__.py` 的内层插件目录**复制到：

```text
%USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2\
└─ Blenderer_2_6_0__2026_0807\
   ├─ __init__.py
   ├─ Blenderer.py
   ├─ export_from_vc.py
   ├─ import_to_blender.py
   ├─ material_helper.py
   ├─ defaults.xml
   └─ ...
```

文件夹名以实物为准；**不能多套一层没有 `__init__.py` 的下载容器目录**。无需将 Blenderer 作为常规 Blender 扩展安装到 Blender 的 Add-ons 管理界面。

### 重要：核对资源

实际报错曾指向 `Lights\Presets\presets.xml` 缺失（详见排错页）。**先检查文件是否存在；不存在时应向来源作者核实完整安装包或资源的正确获取方式。** 不要制作假的 XML，也不要假设 2.1.0/2.3.0 的灯光资源必定能被 2.6.0 使用。

## 3. 在 VC 中加载

重启 VC → 顶部 Home（开始）功能区查看 `Blenderer5.2.0` 按钮 → 点击打开右侧 Action Panel（操作面板）。如出现 Python 错误，请查看 VC 底部 Output（输出），不要继续点击渲染。

## 4. 选择 Blender 程序

在 Blenderer 面板的 `Advanced（高级）` 中定位 `Blender Executable（Blender 可执行文件）`，使用 `...` 选择**完整的 `blender.exe` 文件**，不是 Steam 文件夹。如果提示 `Failed to locate Blender executable`，选择 Yes（是），在文件对话框中指定真实路径。

Steam 安装路径由用户安装库决定；请通过 Steam → Blender → 属性 → 已安装文件 → 浏览，找到可执行文件，不要照抄别人的盘符。

## 5. 最小静态渲染

1. 在 VC 布局中放入一台简单设备（不要用空场景或大规模产线）。
2. Blenderer → 默认：分辨率先选 `1280×720`，EEVEE 采样数设 `8`，方向选 `Landscape（横向）`。
3. 输出文件填写一个真实可写的完整 PNG 路径，如 `D:\VC_Render\Images\test.png`；提前建立目录。`...` 可能打开的是“打开文件”对话框，可以先尝试直接编辑路径输入框。
4. Advanced → 渲染引擎先用 `EEVEE`，`在 Blender 中打开`先不勾选。
5. 点击“渲染图片”，等待 Blenderer 输出，检查生成 PNG 和 VC Output 日志。
6. 如画面过白，再尝试把 Exposure（曝光）从 `0` 调到 `-2` 对比。不同场景需要不同曝光，必要时再检查灯光预设和材质版本。

## 6. 参数持久化

本机曾观察到：重启 VC 后输出路径、渲染参数可能恢复默认。`defaults.xml` 虽然存在，但**2.6.0 V2 的实际读取/保存字段尚未通过源码检查**，不得直接臆造标签。修改前备份该文件，检查读写代码并在重启后验收。

## 7. 动画与视频

2.6.0 V2 的 README 描述 Animation（动画）页支持 PNG Sequence（逐帧 PNG）或 Direct Video（直接视频），MP4 为其视频容器。但本仓库 **尚未在 VC 4.10 + Blender 5.3 上验收动画**，请先完成静态图测试。不要直接把完整工厂场景投入长时间渲染。

更多说明：[常见问题](TROUBLESHOOTING.md) · [实测记录](BLENDER_53_TEST.md)
