# ACID ALLOY / 酸性合金

独立产品单页，包含概览、硬件、交互工作台、七步制作实验室和项目资料五个章节。

## 本地启动

```powershell
cd website
npm ci
npm run dev
```

访问 http://localhost:3100 。生产构建使用 `npm run build`，随后 `npm run start`。
Node.js 20.9 或以上。字体随应用本地分发。

## 项目检查

```powershell
npm run typecheck
npx playwright install chromium
npm run test:e2e
```

测试覆盖桌面和手机的章节导航、素材缺失、四类输入、三个工作模式、完整七步制作、配置失效处理、键盘焦点、减少动态效果和 WCAG AA 自动检查。截图在 artifacts，失败追踪在 test-results。

完整生产构建验收：先运行 `npm run build`，再运行 `npx playwright test -c playwright.production.config.ts --trace=off --reporter=line`。该配置独占 3112 端口，避免复用其他工作区的服务器。

## 概览页

首页为满屏键盘二维贴图与 `Key board`，首次载入有紫黑像素从右向左冲刷的开场，随后变为低透明度流动背景。顶部导航保留。动效说明和透明贴图来源见 [概览说明](docs/overview.md)。

## 硬件解构与交互试用

硬件章节已接入 `MacroPad_AcidAlloy.blend` 导出的真实模型：全屏滚动解构、部件聚焦与旋转，以及键帽打印文件和 PCB 制造资料下载。细节见 [硬件解构](docs/hardware.md)。

试用区左侧为可操作的二维键盘，右侧为电脑显示屏。13 个按键、旋钮、摇杆与触摸板提供连续输入反馈。布局和交互说明见 [交互试用](docs/try.md)。

## 素材和结构

- `src/data/assets.ts`：素材配置入口，首页二维切图和硬件解构模型已接入，其余场景按独立状态配置。
- `src/components/sections`：五个章节及交互状态。
- `src/lib/input.ts`：虚拟工作台输入 reducer。
- `src/lib/three/controller.ts`：模型输入与动画控制接口。
- `src/components/three`：真实 GLB 加载、相机、灯光、材质和错误边界。
- `src/lib/animations/usePageMotion.ts`：滚动、文字、线条及未来场景联动。
- `src/data/product.ts`：硬件参数和真实下载链接。

硬件模型在接近章节时加载，其他待接入场景在状态改为 `ready` 前不挂载 Canvas、不请求 GLB。二维打印和烧录仅改变浏览器状态。

详见 [素材接入说明](docs/assets.md)。

## 项目文件

制作流程已加入 PCB 工艺配置、SMT 物料匹配与贴装预览、可拆装的手工配装工作台，以及支持断线重试的固件烧录演示。交互说明、数据来源及演示边界见 [制作工作台说明](docs/build-lab.md)。

制造文件和打印模型链接指向本仓库的 `device/` 目录。预编译固件已归档到本仓库。

`public/assets/keyboard-exploded.glb` 为约 2.86 MB 的压缩解构模型。`public/downloads/keyboard-*`、`keyboardKbkCase.3mf` 与本仓库制造资料同步，键帽等 STL 使用 `acid-alloy-*` 命名。导出脚本位于 `modeling/tools/export_hardware_web.py`，源文件现名为 `modeling/assets/MacroPad_AcidAlloy.blend`。
