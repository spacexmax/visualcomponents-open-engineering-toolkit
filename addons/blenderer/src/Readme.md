# Blenderer 2.6.0 — XG V1（VC 4.10 修改版）

**将 Visual Components 的三维仿真场景导出到 Blender，制作工业设备效果图和仿真动画。**

这个版本是在社区 Blenderer 2.6.0（Python 2）基础上整理的**免费修改版**。重点优化了日常操作中的路径选择、文件命名、设置记忆、渲染反馈和中文提示，并增加了部分灯光与地板预设。原有核心导出与渲染功能来自 Blenderer 项目及社区维护者；本版本不宣称独立原创。

**主要使用环境：Visual Components Premium OLP 4.10（Python 2.7） + Blender 5.3.0。** Blenderer 2.6.0 上游版本以 Blender 5.2.0 LTS 为设计目标；5.3.0 的使用情况属于 XG V1 的本地测试记录，不能视为全面兼容性保证。

## 1. 主要功能

| 功能 | 简介 |
| --- | --- |
| **仿真场景导出** | 将 Visual Components 场景中的设备几何信息、材质及必要的场景数据转换到 Blender，用于展示渲染。 |
| **静态图片渲染** | 输出 PNG 效果图，用于设备展示、方案汇报和课程截图。 |
| **动画与视频导出** | 提供动画录制与视频渲染设置，支持 MP4；可选择 PNG Sequence（逐帧图片后合成）或 Direct Video（直接视频）两种方式。 |
| **渲染引擎** | 提供 EEVEE 和 Cycles 选项；Cycles 可按原版说明选择部分 GPU 后端和采样数。 |
| **材质与灯光** | 支持材质转换方案、灯光预设、曝光与场景环境配置。 |

> 说明：表格描述的是压缩包包含的功能及其使用方向，**不代表在 VC 4.10 + Blender 5.3.0 上全部组合均已逐项通过测试**。大型场景、不同显卡和动画流程应先用简单样例验证。

## 2. XG V1 新增与改进（2026-11-22）

| 改进项目 | 具体变化 |
| --- | --- |
| **自动记住设置** | 记住 Blender 程序位置、图片/视频输出目录、文件名和常用渲染参数；移动安装目录后可尝试恢复旧设置引用的内置贴图。 |
| **图片、视频输出更方便** | 图片和视频分别选择保存文件夹、填写文件名；可一键打开输出文件夹；同名成品自动编号，减少覆盖风险。 |
| **导出过程可查看** | 增加导出前检查、渲染进度和取消操作；完成后显示输出位置和耗时，视频另外显示帧数、时长、帧率。 |
| **动画参数提示** | 动画帧率跟随录制步长；渲染前显示预计帧数与时长。 |
| **新增 4 套灯光** | 星空月夜、阴天柔光、设备特写、夜班作业；切换预设时可应用默认曝光，并允许保存个人曝光值或恢复默认。 |
| **新增 3 种地板材质** | 工厂绿色橡胶、蓝灰环氧地坪、深灰防滑圆点橡胶。 |
| **中文操作提示** | 补充常用按钮、设置及错误提示的中文显示。 |
| **Blender 交互操作** | 使用独立场景副本打开 Blender，便于在 VC 中继续操作和导出。 |

### 本包同时包含的 2026-11-20 V1 优化

- 优化顶点、UV 与三角面导出流程，减少重复计算。
- 在 Blender 导入阶段跳过一次额外的网格边计算。
- 使用「在 Blender 中打开」时，启动后可继续操作 VC；交互模式的线程由 Blender 处理。

上述是打包源码和更新记录所记载的优化内容；本次 README 调整**没有修改这些代码**。

## 3. 适用版本与已知限制

| 项目 | 版本与说明 |
| --- | --- |
| Visual Components | **Premium OLP 4.10**，Python 2.7（XG V1 主要目标环境） |
| Blender | **5.3.0**（修改版使用者已进行实际渲染测试） |
| 上游 Blenderer 2.6.0 | 作者 **tangtang** 按 **Blender 5.2.0 LTS** 设计；请不要把 XG V1 测试结果当作上游兼容保证 |
| VC 5.x / Python 3 | **未作为本修改版的目标环境验证**，不提供兼容承诺 |
| 动画、复杂场景和显卡后端 | 不同环境可能有差异，请先用少量帧的测试场景验证；如遇问题附版本与报错反馈 |

## 4. 安装与初次使用

1. 下载并解压插件，将**包含 `__init__.py` 和 `Blenderer.py` 的整个插件目录**放进 VC 4.10 的 `Python 2` 用户命令目录：

   ```text
   %USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2\
   ```

2. 重启 Visual Components，确认 Blenderer 命令和设置面板出现。
3. 在 Advanced（高级）中选择 Blender **5.3.0 安装目录中的 `blender.exe`**；路径应指向实际可执行文件。
4. 先使用一个简单场景，分别设置图片输出文件夹和文件名，测试单张 PNG。
5. 如需输出动画，先用短时间、少量帧的场景核对动画记录与 MP4 视频结果，再尝试更大场景。

**提示：** 安装路径依每个人的 Windows 用户目录变化；不要把他人的绝对路径直接复制到自己的电脑中。若旧版本已经存在，先备份并避免两个 Blenderer 版本同时注册命令。

## 5. 下载、作者、授权与致谢

- **项目来源：** [Blenderer 原始社区帖](https://forum.visualcomponents.com/t/blender-addon-blenderer/773)
- **2.6.0 社区维护者：** **tangtang** — [Blenderer 2.6.0 发布帖](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477)
- **公开上传许可：** [tangtang 于 2026-11-22 的回复（#34）](https://forum.visualcomponents.com/t/blender-add-on-2-6-0-with-python2/9477/34)；作者同意公开上传，要求标注实际可用版本，并明确保持免费、不设置收费机制。
- **XG V1 改进版：** 基于社区版本优化易用性、文件输出、设置记忆以及部分渲染预设；感谢原项目作者、tangtang 和测试反馈者。
- **发布原则：** 本修改版**免费分享，不设置收费下载**，也不冒充原版作者的官方发布。
- **第三方资源：** 部分灯光、VCMX、HDR、纹理来自历史 Blenderer 资源。作者关于上传修改版的回复**不自动等同于每项第三方资源的独立许可证**；再分发时仍需核对其来源与授权。

## 6. 上游功能与技术更新记录（保留原版说明）

下面保留上游说明的技术细节及历史更新记录，供需要了解渲染引擎、视频编码、材质转换的用户参考。它们来自 2.6.0 版本说明，并非 XG V1 新增功能，也不意味着在所有版本组合下都已实测。

What's new 2.6.0 (Blender 5.2):
-upgraded for Blender 5.2.0 LTS ; engine remains BLENDER_EEVEE (EEVEE Next)
-Python Add on path (XG V1 / VC 4.10): %USERPROFILE%\Documents\Visual Components\4.10\My Commands\Python 2
-Original Blender 5.2.0 LTS release information: https://www.blender.org/download/releases/5-2/ (upstream target; XG V1 tested with Blender 5.3.0)
-Add Cycles
---Cyclse | NVIDIA  |cuda/Optix |Cuda faster
---       | AMD     | HIP
---OnlyCyclesSamples |64/128/256
-No CPU Render
-Bigger.Faster.You’ll need more spacious storage—and a beefy GPU to match.
-一不小心把它升级到了Blender 5.2.0 LTS应用。为了更流畅使用，我禁用了CPU渲染模式，为了更快速渲染，我选择了牺牲压缩文件，让文件变大了，同时也为了更高效使用GPU。一切的一切，就是为了更快。所以使用的时候，比较考验使用的硬件，需要更大的硬盘，更好的GPU来支持。
-出现的任何bug,我将不会立即修复。毕竟我没有为了任何报酬，纯粹为了体验。

---

## Video Rendering Options (2026-08-04)

新增视频渲染选项（位于 Animation 标签页，仅对视频生效，不影响图片渲染）：

### Animation::Container
- 仅支持 MP4（H.264 + MPEG4 容器）
- 移除了 AVI 格式支持

### Animation::RenderVideoMode
视频渲染策略，两种模式可选：

| 模式 | 说明 | 特点 |
|------|------|------|
| PNG Sequence（默认） | 先渲染每帧 PNG 到 Picture_frames 文件夹，再通过 VSE + FFMPEG 合成视频 | 保留 PNG 中间帧，可后期编辑 |
| Direct Video | 通过 `image_settings.media_type='VIDEO'` 直接渲染为 MP4 | 零 PNG 中间文件，节省磁盘空间和 I/O |

### Animation::VideoQuality
视频质量，三档可选（基于 H.264 CRF 恒定速率因子）：

| 选项 | Blender 枚举值 | 近似 CRF | 说明 |
|------|----------------|----------|------|
| Lossless | `PERC_LOSSLESS` | CRF 17 | 感知无损，视觉无差异，文件较大 |
| High（默认） | `HIGH` | CRF 20 | 高质量，平衡质量与大小 |
| Low | `LOW` | CRF 26 | 低质量，文件最小 |

更新时间：2026-08-04

---

## Material Version (2026-08-05)

新增材质版本选项（位于 Materials 标签页）：

### Materials::MaterialVersion
| 选项 | 说明 |
|------|------|
| OLD（默认） | 保留原有材质方案 |
| NEW | 新方案，VC 与 Blender 材质灯光精确对应 |

### NEW 方案改进
- **RGB 颜色**：标准 sRGB→Linear 转换（IEC 61966-2-1），替代旧的 `x**2.2` 近似
- **透明材质**：Alpha 直接对应 VC opacity，不额外调亮颜色或缩放粗糙度
- **玻璃特殊处理**：opacity<0.2 时启用 Transmission Weight 模拟折射效果
- **灯光物理对应**：
  - Point/Spot/Area：1:1 对应（瓦特）
  - Sun：VC 强度 / 100 → W/m²

更新时间：2026-08-05

### NEW 方案进一步优化（2026-08-06）
- **Specular 高光色（Ks）**：VC 高光颜色亮度映射到 Principled BSDF 的 Specular IOR Level
- **Emission 自发光（Ke）**：VC 自发光强度 > 0 时启用 Emission Color + Emission Strength 通道
- **玻璃材质 IOR**：透明度<0.2 时设置 IOR=1.45 模拟真实玻璃折射
- **玻璃粗糙度自适应**：玻璃表面粗糙度强制降至 0.05 以下，避免折射模糊
- **半透明分档**：opacity<0.2 (玻璃) / <0.5 (半透明) / 其他 三档处理 Transmission Weight
- **纹理色彩空间**：显式设置 texture colorspace 为 sRGB，确保 Blender 自动转换正确
- **背面剔除**：禁用 backface culling，避免 VC 单面模型出现破洞
- **导出端扩展**：VC 端 `Ks`（Specular）字段现在被解析并使用

更新时间：2026-08-06
### NEW 方案进一步优化（2026-08-07）
- **排除了AMD和intel核显

---
