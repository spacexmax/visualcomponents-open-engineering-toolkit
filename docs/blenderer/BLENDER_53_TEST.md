# 本地实测记录：VC 4.10 + Blenderer 2.6.0 V2 + Blender 5.3

> 记录日期：2026-11-13。来自用户实际界面截图和对话中观察到的结果，**非官方兼容性认证**。测试工程的品牌、型号等不保证可再分发。

| 项目 | 环境 / 结果 | 证据范围 |
| --- | --- | --- |
| VC | Visual Components Premium OLP 4.10.0 | 软件标题栏可见 |
| 插件 | Blenderer 2.6.0 V2（Python 2） | `Blenderer5.2.0` 按钮可见 |
| Blender | Steam 安装的 Blender 5.3.0 | Blender 标题栏可见 |
| 插件初始化 | 通过 | Home 按钮出现，Output 打印 `Blender5.2.0,Please!` |
| 操作面板 | 通过 | 默认 / Lights / Advanced / Materials / Animation 等页面可见 |
| 初次错误 | 出现过 | `IOError: [Errno 2]`：缺少 `Lights\Presets\presets.xml`，后来面板可打开；补齐方法未确认 |
| Blender 程序发现 | 出现过错误，后可调用 | 曾提示 `Failed to locate Blender executable`，手动指定后进入渲染 |
| 静态 PNG | **已成功** | 实际生成并展示设备与地面渲染图 |
| 曝光 | 单场景 `0` 过曝，改为 `-2` 后改善 | 对比过曝图与正常图 |
| 输出路径永久保存 | **待解决** | 重新启动后参数有恢复默认的报告 |
| 动画录制 / MP4 | **未验证** | 尚无测试结果 |
| 复杂布局 / 全部功能 / 长期稳定性 | **未验证** | 不得据此声称“全面兼容” |

## 下一轮验证建议

先用无保密信息的单组件样例验证：重启后的配置读取、输出文件命名、连续渲染、Blender 5.2 与 5.3 差异；之后再验证短动画和 MP4。每轮保留版本号、截图、日志与可重复步骤。

## 兼容性措辞

**可以写：**“在 VC Premium OLP 4.10.0、Blenderer 2.6.0 V2、Steam Blender 5.3.0 的本机环境，静态 PNG 渲染已成功。”

**不要写：**“VC 4.10 完全兼容 Blenderer 2.6.0 和 Blender 5.3”“动画导出已通过”“插件由本仓库维护发布”。

资源包、脚本与第三方资产均不随本仓库再分发。
