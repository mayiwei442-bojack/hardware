# 正式素材接入

首页已接入的透明二维图片使用 `assets.overviewImage` 配置，来源与提示词见 [概览说明](overview.md)。

2026-10-21：硬件解构页已接入 `MacroPad_AcidAlloy.blend` 导出的正式模型和 `HardwareExplode` 动画，不再使用滑杆或待接入占位。导出、下载来源和验证说明见 [硬件解构](hardware.md)。其余场景的模型状态仍独立配置。

## 模型

把正式 GLB 放进 public/assets，然后修改 src/data/assets.ts 中对应条目：

```ts
assets.models.keyboard.src = '/assets/keyboard.glb';
assets.models.keyboard.status = 'ready';
assets.models.keyboard.camera = { position:[0,2,4], target:[0,0,0], fov:36 };
assets.models.keyboard.scale = 1;
assets.models.keyboard.lighting = { ambient:0.7, key:3, color:'#f0f1ec' };
assets.models.keyboard.materials = { Shell:{color:'#242925',roughness:0.35,metalness:0.6} };
assets.models.keyboard.nodeInputs = {
  Key01:{type:'key',keyId:'K01'},
  EncoderPlus:{type:'encoder',delta:5},
  JoystickRight:{type:'joystick',x:1,y:0},
  Touch:{type:'touch',action:'tap'}
};
```

示例名称必须替换成正式文件中存在的节点和材质名。配置只改变既有材质，不生成几何体。节点点击事件转交统一 InputController；连续拖动、旋转手势可直接调用相同的 onEncoderRotate、onJoystickMove 接口。键位支持 K01–K13。

资源列表包括 keyboard、keyboardExploded、computer、printer、smtMachine、pcb。每个条目独立指定相机和灯光。缺少资源保留 pending，不填入虚构文件。

## 动画

正式 GLB 内须提供实际动画片段。通用 ModelScene 用 clips.assembly 指定拆解片段名称，通过 createSceneController 的 setProgress(0–1)、resetAssembly、playClip(name)、stop 控制。硬件页使用独立 HardwareScene：页面顶部到达视口顶部后，继续滚动 2.35 个视口高度推动完整解构；之后保留停留区用于选择部件。动画直接读取同一控制器，反向滚动反向合拢。

## 图片和贴图

productImages.status='ready' 后填入 items：{src,alt,width,height}。keycapTextures.status='ready' 后把 items 配成材质名到贴图 URL 的映射。贴图按 sRGB 读取并作用于既有材质。纹理与材质实例在卸载时释放。

## 接入后的检查

硬件解构模型已有真实资源；桌面/手机取景、部件点击、名称选择、镜头聚焦、拖动旋转、下载和加载重试由 tests/hardware.spec.ts 验证。其余 pending 模型和图片仍需在提供正式素材后检查取景、UV、事件和性能。
