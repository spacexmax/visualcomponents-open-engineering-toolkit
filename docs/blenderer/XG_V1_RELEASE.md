# Blenderer 2.6.0 XG V1 — GitHub 发布说明草稿

**主要用途：** 将 Visual Components 仿真场景导入 Blender，制作工业设备静态效果图及动画视频。

## 原版主要功能
- 3D 场景导出及 PNG 渲染
- 动画录制与 MP4 视频输出选项
- EEVEE / Cycles、材质映射和灯光设置

## XG V1 新增
- Blender 路径、输出文件夹、文件名及常用参数自动记忆
- 图片、视频分别选择输出目录，一键打开目录，同名自动编号
- 渲染前检查、进度与取消；完成后显示保存路径及耗时
- 动画帧数、时长及帧率提示
- 新增四套灯光及三种地板材质
- 中文提示、交互打开和网格处理优化

## 适用版本
- Visual Components Premium OLP 4.10，Python 2.7；Blender 5.3.0（修改者实测环境）
- 上游 2.6.0 按 Blender 5.2.0 LTS 开发；复杂场景和动画功能需按实际环境验证

## 下载

正式发布后在 GitHub Releases 的 Assets（附件）中下载 `Blenderer-2.6.0-XG-V1-VC4.10-FULL.zip`。这个包包含源码与全部运行素材，无需下载其他 ZIP。

## 安装
完整解压到 `%USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2\`，确保插件文件夹内含 `__init__.py`，重启 VC 并指定 `blender.exe`。

## 来源与许可
感谢原始 Blenderer 项目及 2.6.0 社区作者 tangtang：
- [原始项目](https://forum.visualcomponents.com/t/blender-addon-blenderer/773)
- [2.6.0 论坛](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477)
- [tangtang 同意上传、要求注明适用版本且不得收费的回复](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34)

**免费分享。** 历史 HDR、VCMX、纹理等资产仍需核查来源与许可。完整 FULL.zip 已上传 GitHub Release 草稿，等待正式发布。