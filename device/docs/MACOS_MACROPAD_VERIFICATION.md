# MacroPad Apple Silicon 改写记录

日期：2026-10-23（Asia/Shanghai）。Apple Silicon 原生编译、打包及静态产物检查已完成；未进行 Mac 界面或实体键盘交互验证。

## 成品

- `device/dist/macos/MacroPad-0.15.0-macos-aarch64.dmg`：12,238,248 字节。
- `device/dist/macos/MacroPad-0.15.0-macos-aarch64.app.zip`：10,569,903 字节。
- DMG SHA-256：`21b7f980a62066a1b9310271254c7d43d1a1cf87aa7f6147742125d54068ea4f`。
- APP ZIP SHA-256：`885c2da1cad067d0bacd0b12aede5d3324689f76c8fdbc6f6919f3bf00bbd3b2`。
- 应用二进制 SHA-256：`35b93dc34cc6833c8516ba0c52d2794e005f7fef3e3f9acd03a9eea813c363c6`。
- 原生架构 ARM64，最低部署版本 macOS 11；应用名 MacroPad，bundle ID `io.macropad.desktop`。

DMG 内含 MacroPad.app 和 Applications 快捷入口。原作者 MIT 及第三方声明位于应用内 `Contents/Resources/licenses`，不作为产品界面展示。

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

本机是 Windows；真实 Mac 编译及原生工具检查由已授权的 GitHub Apple Silicon 构建机执行。下载后又在本机核对包哈希，并独立检查解压应用的 plist、图标、ARM64 Mach-O 头、固定固件及声明文本哈希。

## Mac 原生构建

- 分支：`codex/macropad-macos`，编译源码提交 `e79a6c0e598983e57d37c950a4ab9ea4eca9f8fb`。
- [成功构建记录](https://github.com/mayiwei442-bojack/hardware/actions/runs/39924953098)。未合并 main，也未发布 GitHub Release。
- 原生主机：macOS 15.7.9 ARM64；Xcode 16.4，SDK 15.5，Rust/Cargo 1.99.1。
- Rust release 编译成功，用时 9 分 22 秒。
- `lipo`：单架构 `arm64`；`otool`：仅使用系统库和框架，没有 Sparkle 链接。
- `codesign --verify --deep --strict` 通过；应用标识正确，签名类型为 `adhoc`，没有 Developer ID TeamIdentifier。
- `hdiutil verify` 对 DMG 返回校验有效；下载到本机后的 DMG、ZIP 哈希均与云端记录一致。
- 574 个 Mac normal/build 依赖全部出现在声明清单中。原始声明、固定版本恢复来源、SHA 校验均保留；13 个只提供许可元数据的包附带明确标注的 SPDX 标准参考，1 个包保留历史源码等价恢复说明。未编造版权年或作者。
- 日志：`device/artifacts/macos-build-39924953098/`；包括 host、toolchain、package、native bundle report 和本机 portable report。

前两次构建分别因原工具不能识别声明、通用 `*.orig` 忽略规则漏提交原 manifest 而停止；已修复后成功，未通过删除检查绕开问题。

## REA 成品检查

对实际下载的 APP ZIP 执行 `open_binary` → `inspect_artifact` → `export_evidence_bundle` → `close_binary`。

- 摘要 Evidence：`ev_fe0722e6ce2787bc0c6f264eabe9c546eaa2edd5205de201d6f123f70ef59d99`。
- 完整 Evidence：`ev_e489136c97d2cca02c19a967663ef357e938ecaa8e2013dc665e90cdd8e29f5f`。
- 清单 Evidence：`ev_1d501ec8dfcdcb804e04235369891105d62018b1b2ce9aa3e516c1197538d22f`。
- 包清单含 20 个节点（含根节点），完整性矛盾为 0；识别 MacroPad Mach-O、plist、图标、固件和声明文件。
- 本地证据：`device/artifacts/rea/macropad-macos-app-final-evidence.json`。

REA 此项为 ZIP 成员及哈希静态检查，不能证明界面运行行为；ARM64 架构来自 Apple 原生工具及独立 Mach-O 头检查。

## 验证边界

未执行 Mac 界面交互、系统辅助功能授权、实体键盘连接或固件烧录。没有 Developer ID 签名或 Apple 公证，不声称 Gatekeeper 放行或实机功能验收通过。此次 Mac 流水线没有新增或运行测试套件。

## 原生构建入口

根目录工作流 `.github/workflows/macropad-macos.yml` 和 `device/scripts/package-macos.sh` 提供 Mac 原生编译及打包入口。具体步骤、产物哈希、架构检查和签名状态以本次成功构建及上述本地记录为准。
