# 概览开场与二维键盘贴图

概览占据一个完整视口。画面内容仅为键盘二维贴图和 `Key board`，顶部导航保留。

## 动画

- 每次网页文档首次加载时播放一次约 1.38 秒的开场，导航和滚动返回概览不会重播。
- 紫黑底色与荧光绿像素先覆盖最上层；揭幕边界从右向左推进，块纹同时水平向左运动。
- 揭幕后像素退为低透明度背景。右侧像素更密集，向左移动时逐渐稀疏，形成脱落流逝的效果。
- 键盘贴图有轻微悬浮、鼠标视差与滚动视差。
- 开启系统“减少动态效果”时直接显示静态概览。切换到其他章节或隐藏标签页会暂停背景绘制。

实现：`src/components/sections/OverviewHero.tsx`、`overview.css`、`src/components/interactive/PixelWash.tsx`。像素使用 Canvas 2D，不创建或渲染三维产品模型。接口和键盘素材路径在 `src/data/assets.ts`。

## 素材

- 编辑源：`modeling/acid_alloy/renders/11_keyprints_hero.png`。
- 使用素材：`website/public/assets/acid-alloy-keyboard-cutout.png`。
- 处理工具：内置 imagegen，透明背景切图；未调用 Blender。
- 用户参考：`D:/App/下载.jpg`，作为紫黑像素与少量荧光绿的动效风格参考。

内置 imagegen 使用的完整提示词：

> Use case: background-extraction. Edit target: the supplied existing ACID ALLOY keyboard product render. Produce a faithful isolated transparent PNG cutout for a website. Remove only the entire gray studio background and the ground shadow. Preserve the exact keyboard silhouette, camera perspective, all 13 keycaps, rotary knob, purple joystick, acid lime cover, dark enclosure, materials, markings and lighting. The whole keyboard must be visible with generous transparent margins around it; no crop. Do not invent, add, remove, redraw or reconfigure hardware. Remove the tiny KEYBOARD label on the front top edge only, keeping its lime surface continuous. No additional text. Output true alpha transparency, no checkerboard baked into pixels. Keep the original photorealistic render quality.
