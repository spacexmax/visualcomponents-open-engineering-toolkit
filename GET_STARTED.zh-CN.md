# 第一次创建公开 GitHub 仓库：5 分钟操作指引

这个压缩包只是**仓库初始模板**，不代表 GitHub 线上仓库已创建。

1. 登录 GitHub，打开 https://github.com/new 。
2. Owner（所有者）选 `spacexmax`。
3. Repository name（仓库名）填 `visualcomponents-open-engineering-toolkit`。
4. Description（简介）填：`Unofficial open-source add-ons and engineering utilities for Visual Components 4.10 and 5.x.`
5. Visibility（可见范围）选 **Public（公开）**。
6. 因为模板已经包含 `README.md`、`.gitignore` 和 `LICENSE`，在创建时**不需要**额外初始化这三个文件，直接点击 **Create repository（创建仓库）**。
7. 在新建的空仓库页面点击 **uploading an existing file（上传现有文件）**。
8. 解压本 ZIP，打开解压后的 `visualcomponents-open-engineering-toolkit` 文件夹，将里面的**文件和子文件夹**拖进上传页面。注意：**不要只上传 ZIP 压缩包**，否则 GitHub 不会自动展开目录。
9. 等文件全部列出来，填写 Commit message（提交说明）：`docs: initialize VC toolkit repository`，然后点击 **Commit changes（提交更改）**。
10. 刷新仓库首页，确认 README、LICENSE、addons、docs 等目录都出现。

如浏览器不支持整目录拖拽，可以使用 GitHub Desktop（GitHub 桌面客户端）把本地文件复制进克隆后的仓库再提交；或者逐级在网页端创建文件。

注意：这只是示范结构，当前所有插件均标注**规划中/未测试**，没有下载包。第一个插件完成并测试后再创建 Release（正式版本）。
