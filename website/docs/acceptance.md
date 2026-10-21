# 本阶段验收记录

日期：2026-10-21。范围：五章节网页、中文界面、二维交互和正式素材接入架构。正式 3D 内容留待下一阶段。

| 目标要求 | 当前实现与证据 |
| --- | --- |
| 独立 Acid Alloy 品牌、统一配色与工业排版 | globals.css 的六色变量、本地字体、细线网格；ProductSite 五章节。浏览器检查可见文本没有原项目名称或开源宣传。桌面与手机截图人工查看。 |
| 五章节、固定导航、连续纵向浏览 | tests/site.spec.ts 的 五个章节 与 all navigation 检查所有锚点，顶部至资源均可到达。 |
| 极简满屏概览 | 按后续要求，概览仅显示既有键盘渲染图的透明二维切图与 Key board；顶部导航保留。OverviewHero、PixelWash 与 overview.css 实现快速像素揭幕和持续左向脱落背景。 |
| 硬件菜单、参数、六阶段、复位、外观/规格区分 | Hardware 的八部件菜单与标签；测试切到 PCB 并检查 STM32、阶段滑块与 Reset Assembly；明确标注 3D 待接入。 |
| CODE 编辑器、文件、命令、状态 | Workstation / input reducer；浏览器编辑、新建、文件切换、字体大小、命令面板、终端、笔记实际操作。 |
| AUDIO 音量、参数、电平、静音 | 浏览器改变主音量、旋钮增量、触摸启停、电平状态、静音及延迟；音频明确为界面模拟。 |
| SHORTCUTS 应用、命令、历史 | 浏览器摇杆切换应用、批准请求、历史记录、复位。 |
| 四类统一输入接口 | controller.ts 定义所有四个事件；二维 InputPanel 和未来 ModelScene 使用同一接口。 |
| 七步制作全流程 | tests 的 seven-step 在桌面与手机依次完成全部七步；最终要求 13 键、两个旋转方向、四个摇杆方向、触摸和 RGB 三通道全部操作。 |
| 每步参数、说明、反馈、资源、前后导航 | BuildLab 的 steps 配置及共享页脚；未满足前置条件禁用下一步；异步进度可取消；重新配置使后续完成状态失效。 |
| 上传/预设 Gerber、BOM、CPL、HEX | FilePicker 支持拖放与文件选择，检查扩展名、容量和格式字段；浏览器实测拒绝无效 ZIP，再使用预设完整前进。 |
| 二维打印和烧录 | 配置打印部件、进度反馈；Connect→Program→Verify 顺序门控并完成。无设备 API 调用。 |
| 制作完成界面、项目和回顶 | 浏览器检测 7/7 完成状态；截图 desktop-build-complete / mobile-build-complete；完成模块中具有真实项目和顶部链接。 |
| 动画清单 | usePageMotion 实现视差、标题入退、章节 reveal、章节转场、SVG 生长、数字；CSS 实现网格、按钮、电平、进度；Motion 实现横向部件/步骤及纵向模式转换。减少动态效果模式通过测试。 |
| 模型加载、相机、灯光、材质、输入、动画/滚动架构 | assets.ts / ModelSlot / ModelScene / controller.ts / bindSceneScroll；GLB 延迟加载，有加载和错误状态、独立相机灯光材质配置与真实片段控制。无资源不挂载 Canvas。 |
| 八类待接入素材清单及替换 | 所有明确要求的六种模型、产品图片和键帽贴图集中配置为待接入；public/assets 仅说明文件；docs/assets.md 提供接入方法。 |
| 禁止伪造 3D | 源代码无几何体生成、无模型文件；浏览器仅有像素背景 Canvas 2D，未挂载三维模型画布或请求 GLB/glTF；没有调用 Blender。 |
| 响应式与无障碍 | 320、390、768、1024、1440 宽度无页面横向溢出；桌面和手机核心流程；axe WCAG A/AA 自动检查通过；命令框焦点与 Escape；无 hydration error。 |
| 下载链接 | resource-links.json：十个 GitHub/原始文件入口返回 200。用户指定 MakerWorld 自动访问为 403，保留原链接，并提供三个已确认 200 的直接部件下载入口。 |
| 技术栈与构建 | package.json 与 lock 包含 Next App Router、TS、Tailwind、GSAP、Motion、Three、R3F、Drei；typecheck 与生产 build 成功。 |

## 执行结果

- 桌面和手机核心检查：8 / 8 通过。
- 补充全导航与窄屏检查：2 / 2 通过。
- 已人工查看首屏、硬件、工作台、制作完成与资源截图。
- 制作的模拟流程不发出真实订单、不下载虚假资源、不刷写设备。
- 正式素材尚未提供；它们的视觉、动画轨迹、UV 与媒体解码需在下一阶段接入时验收。

未发布线上服务；本地启动方法见 README。

补充记录：本次按用户要求移除了原影像章节，并将网站界面文案调整为中文。此次未重新运行自动检查。


## 极简概览更新（2026-10-21）

- 概览高度在桌面 1440×1000、手机及横屏 844×390 均等于完整视口；无额外参数、按钮或占位信息。
- 紫黑像素最初遮盖全屏和顶栏，约 1.38 秒内从右向左揭开。中间帧实测左侧 alpha=255、右侧 alpha=0，揭幕后覆盖层隐藏，背景透明度为 0.48（手机 0.36）。
- 回到概览不会重播；离开概览时背景停止变化；开启系统减少动态效果时跳过开场、冻结像素和悬浮。
- 本轮全量 14 项检查中，首页、导航、工作台、无障碍和布局 12 项通过；两项制作流程检查发现上一轮中文化后遗留的英文测试定位，修正定位后桌面与手机制作流程 2 项均通过。
- TypeScript 检查及生产构建通过。
- 视觉证据：artifacts/pixel-wash-01-cover.png、pixel-wash-02-reveal.png、pixel-wash-03-background.png、desktop-pixel-overview.png、mobile-pixel-overview.png；中间帧采样记录在 pixel-wash-review.json。
- 二维透明图来源及内置 imagegen 提示词见 overview.md。
