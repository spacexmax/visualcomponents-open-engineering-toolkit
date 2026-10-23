# Compatibility / 兼容性记录

A compatibility claim requires a test on the named product version, including installation, command visibility, expected operation, and error handling.

兼容性必须经过**指定 VC 版本的实际测试**才能标注为“支持”，不能仅根据脚本语法推测。

| Add-on / 插件 | VC 4.10 | VC 5.0 | VC 5.1 | Tested environment / 测试环境 |
| --- | --- | --- | --- | --- |
| Batch Rename | Not tested / 未测试 | Not tested / 未测试 | Not tested / 未测试 | None |
| Component Audit | Not tested / 未测试 | Not tested / 未测试 | Not tested / 未测试 | None |
| Robot TCP Checker | Not tested / 未测试 | Not tested / 未测试 | Not tested / 未测试 | None |

## Before declaring support / 标注支持前

1. Confirm edition and exact build number / 确认具体版本与构建号。
2. Confirm scripting interpreter and available API / 确认 Python（脚本语言）解释器和 API（应用程序编程接口）。
3. Test on a **copy** of a non-confidential sample layout / 使用无敏感信息的示例项目副本。
4. Record installation path, required dependencies, tested functions, and known limitations / 记录安装路径、依赖、功能与限制。
5. Publish only the tested package / 仅发布已验证包。

Do not assume compatibility between major versions or between all VC 5.x releases.
