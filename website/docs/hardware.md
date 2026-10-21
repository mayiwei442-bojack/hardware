# 硬件解构

源文件：`modeling/assets/MacroPad_AcidAlloy.blend`。沿用 main 的最新文件名，模型内容与原导出源文件一致，未重新保存或覆盖。

## 模型与动画

- `modeling/tools/export_hardware_web.py` 通过官方 Blender MCP 执行。导出使用独立临时场景，恢复原场景的帧和解构状态。
- 读取 `DEMO_OMK_ROOT_CTRL` 第 240–285 帧原始 Bézier 曲线，并采样其驱动后的世界坐标。原文件将属性标记为整数；仅在内存中将其恢复为浮点类型，避免曲线被截断为 0/1。
- 984 个可见表面按部件及相同运动合为 38 组；原文件已隐藏的 42 个旧印花不导出。13 个键帽和 13 个轴保持独立。
- 保留求值后的几何、UV、材质和印花；将不兼容 glTF 的 alpha 混合颜色合成为基础色贴图，单独保留透射遮罩。
- 37 个运动通道合并为 `HardwareExplode`。Draco 压缩后模型约 2.86 MB，解码器位于 `public/draco`，无运行时 CDN 请求。
- 机器可读导出记录：`modeling/references/hardware_web_export.json`。

## 页面行为

页面高 440svh，模型画布在顶部到达屏幕顶部后 sticky 固定。后续 2.35 屏滚动驱动解构，余下约一屏停留供用户选择，继续滚动自然进入下一节。向上滚动反向合拢，退出部件观察。

解构完成后显示部件名称。点击名称或网格均选择真实节点。镜头用约 0.95 秒过渡到部件包围盒中心，淡出其他部件；拖动绕部件旋转。滚轮仍用于页面滚动。返回按钮和 Escape 恢复爆炸视图，键盘焦点回到名称入口。系统减少动态效果设置下跳过平滑过渡。

移动端将部件名称放在底部，并调整镜头投影以给名称和下载卡片留出空间。仅在硬件章节进入导航下方的可见区域后挂载场景，首页开场和跳过硬件直接进入试用页时不加载隐藏画布；离屏卸载场景并停止连续渲染。加载失败可重试，重试使用独立请求避免复用已失败缓存。

## 下载来源

- 13 个键帽 STL：从本次指定 Blender 文件的实际键帽几何导出，毫米单位，落到 Z=0；提供单个键帽和完整 ZIP。STL 不含颜色和印花。导出件仍需在切片器检查壁厚和配合，未新增制造认证。
- 盖板、旋钮、摇杆帽 STL：同一源文件的对应真实网格。
- 底壳 3MF：`device/hw/v1/mechanical/keyboardKbkCase.3mf`，下载名相同，与 main 的最新文件逐字节一致。
- Gerber、BOM、贴片坐标与打板 ZIP：使用 main 的 `device/hw/v1/fab/keyboard-*` 资料。材料包内也使用 `keyboard-*` 名称，保留制造说明；可单独下载，也可下载材料包。
- Draco 运行文件来自已安装的 Three.js 包，附 Apache 2.0 许可证。上游模型/制造资料许可位于 `public/downloads/LICENSE.txt`。

## 验证

`npm run typecheck`、`npm run build`。生产构建的交互检查：`npx playwright test -c playwright.hardware.config.ts --reporter=line`。该配置使用本地 3101 端口，避免开发热更新影响镜头和测试。

测试覆盖屏幕未占满时进度为零、进入后滚动解构、反向合拢、名称和网格选择、相机聚焦、鼠标/触摸旋转、STL 二进制结构、PCB 材料实际下载、退出页面、横向溢出与加载失败重试。截图在 `artifacts/hardware-*`。

## 分支整合

保留 main 最新的文件命名、制造资源链接和项目资料整理；保留功能分支最新的试用界面、全屏解构、相机交互及 Draco 压缩。旧 `openmicro-*` 下载文件和旧底壳文件不再提供，所有部件下载入口同步改用 `keyboard-*`、`keyboardKbkCase.3mf`。
