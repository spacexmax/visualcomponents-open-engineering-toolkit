# Release conventions / 发布规范

This is a multi-add-on repository. Each add-on should use its own version tag rather than a single global version.

**Example tags / 标签示例**

- `batch-rename-v0.1.0`
- `component-audit-v0.1.0`

**Example release assets / 安装包命名示例**

- `batch-rename-v0.1.0-vc4.10.zip`
- `batch-rename-v0.1.0-vc5.0.zip`

Only upload packages that have been installed and tested on the version stated in the filename. Include release notes for tested builds, installation path, features, and known limitations.

## Release checklist / 发布检查清单

- [ ] Original source and third-party licenses reviewed / 授权合规
- [ ] No license keys, customer files, or confidential CAD data / 无敏感信息
- [ ] Installation and rollback tested / 安装与回退验证
- [ ] Compatibility table updated / 更新兼容性
- [ ] README and changelog updated / 更新说明与日志
- [ ] ZIP package contents reviewed / 检查压缩包内容
- [ ] Publish GitHub Release / 发布版本

**已发布 / Published：** [Blenderer XG V1](https://github.com/spacexmax/visualcomponents-open-engineering-toolkit/releases/tag/blenderer-xg-v1-vc410)。其他规划中插件仍未发布。
