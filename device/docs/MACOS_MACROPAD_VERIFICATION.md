# MacroPad Apple Silicon 改写记录

日期：2026-10-23（Asia/Shanghai）。此记录区分本机可确认的源码/资源与尚待 macOS 编译的成品。

## REA 原版包检查

- 对象：官方 v0.15.0 的 `OpenMicro-0.15.0-macos-aarch64.dmg`。
- SHA-256：`e13633df9f88db410a570aeeaceae3051d956337f07e7cb0a70a8da5a159dd7f`。
- REA MCP 已连接；`open_binary`、`inspect_artifact`、`export_evidence_bundle`、`close_binary` 均已执行。
- 摘要 Evidence：`ev_7dfd5587c4aee948de4438830cae11301b1df3d17b3cb3d6059090c98b550a6a`。
- 完整 Evidence：`ev_fd34eb9d44d238f4c08b1bcce12780b7c5239026ef60659c165d2bb4de3e8e5c`。
- 清单 Evidence：`ev_8403f8efdc4f22af79bcde323f158b2f69d9ac26a43ec89abdb8c87141a99a2d`。
- 本地记录：`device/artifacts/rea/macos-upstream-evidence.json`。

Windows 上的 REA 仅确认 DMG 容器身份和哈希；返回的清单只有根节点，明确要求 macOS 原生适配器才能检查内部文件。这不构成对原版 Mac 二进制内部结构、界面或运行行为的确认。此次改写基于可获得的原生 Rust/GPUI 源码。

## 产品改写

- 显示名称 MacroPad，应用标识 `io.macropad.desktop`。
- Apple Silicon 平台标签 `MAC / ARM64`，交付目标 `aarch64-apple-darwin`。
- 沿用网页的石墨黑 `#0b0e0d`、黄绿 `#c6ff36`、紫色 `#9673ff`、细边框和矩形控制面板。
- 根据网页和机械模型的布局绘制 13 键、旋钮、摇杆与触摸区；不嵌入带有旧产品文字的模型截图。
- 产品主界面不显示主题名和原作者声明；MIT 与第三方许可作为应用包中的声明文件附带。
- 默认不连接旧更新源，不使用旧 Sparkle 公钥。
- 菜单栏使用透明模板资源，Dock 使用 MacroPad 彩色 ICNS。
- 现有配置兼容别名、USB 协议、macOS 辅助功能授权入口及键盘行为保留。

## 已有本机记录

共享 Rust 库在本次平台标签修改后，Windows release 回归日志为 `device/artifacts/macos-shared-regression.log`：161 passed、0 failed、1 ignored。跳过项需要实体键盘。该记录不能证明 macOS 条件编译分支可编译，也不能代替 Mac 实机验证。

本机是 Windows，未获得可用的 Mac 编译环境。没有生成或验证最终 ARM64 `.app` / `.dmg`，没有执行 Mac 界面交互、系统授权、实体键盘连接或固件烧录，也没有完成 Developer ID 签名或 Apple 公证。

## 原生构建入口

根目录工作流 `.github/workflows/macropad-macos.yml` 和 `device/scripts/package-macos.sh` 提供 Mac 原生编译及打包入口。运行结果、产物哈希、架构检查和签名状态应以实际 macOS 构建日志为准；尚未运行的步骤不记为通过。
