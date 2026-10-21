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

## 概览页

首页为满屏键盘二维贴图与 `Key board`，首次载入有紫黑像素从右向左冲刷的开场，随后变为低透明度流动背景。顶部导航保留。动效说明和透明贴图来源见 [概览说明](docs/overview.md)。

## 交互试用

试用区上方为简短介绍，下方左侧是可操作的二维键盘，右侧是电脑显示屏。13 个按键分别切换会话、命令、确认结果、终端、语音演示和模式调节等画面；旋钮、摇杆与触摸板提供连续输入反馈。布局、按键映射和交互边界见 [试用说明](docs/try.md)。

## 素材和结构

- `src/data/assets.ts`：唯一素材配置入口，首页二维切图已接入，其余八类展示素材待接入。
- `src/components/sections`：五个章节及交互状态。
- `src/lib/input.ts`：虚拟工作台输入 reducer。
- `src/lib/three/controller.ts`：模型输入与动画控制接口。
- `src/components/three`：真实 GLB 加载、相机、灯光、材质和错误边界。
- `src/lib/animations/usePageMotion.ts`：滚动、文字、线条及未来场景联动。
- `src/data/product.ts`：硬件参数和真实下载链接。

本阶段没有创建、复制或渲染产品 3D 模型。提供真实素材并将状态改为 `ready` 之前，不挂载 Canvas、不请求 GLB。二维打印和烧录仅改变浏览器状态。

详见 [素材接入说明](docs/assets.md)。

## 资料来源

技术参数参考 conol-ai/openmicrokbd 的 V1 硬件资料；外观方案为 Acid Alloy。页面独立呈现品牌，资源链接保留真实来源。MakerWorld 是用户指定的打印来源，自动访问返回 403；打印步骤同时提供已确认可访问的外壳、旋钮、摇杆帽直接下载。链接检查记录见 artifacts/resource-links.json。
