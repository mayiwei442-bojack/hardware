# keyboard V1 源 CAD 基准批次

日期：2026-10-01

## 输入与处理

- 读取 `references/source_inventory.json` 与 `references/source_meshes.json`，从 `keyboardKbkCase.3mf`、`keyboardRotator.3mf`、`keyboardJoystickCap.3mf` 的顶点/三角面重建 Blender 网格。
- 场景采用 Z-up、毫米坐标（`scale_length=0.001`）。外壳包络 99.4 × 99.4 × 12.6 mm；旋钮 15 × 15 × 20 mm；摇杆帽约 18 × 18 × 13 mm。
- 旋钮和摇杆帽仅为参考展示而横向分离，不代表装配坐标。
- KiCad USB-C 位于 (0,-45.64) mm，按项目 XY 约定映射至 Blender 后侧 +Y；已对照实拍。源网格的 USB 缺口在正交图中仍不够明确，外壳朝向待批次2复核。

## 落地资产

- 已建立 `OMK_ROOT`、外壳/PCB/按键/控件/电子/LED/紧固件/控制/工作室/源参考集合。
- 正式网格 `Housing_Shell_V1` 直接复制源外壳三角网格，记录尺寸和源文件；参考对象隐藏保留。
- 保存主文件 `assets/MacroPad.blend`，断点 `checkpoints/batch_01_formal_housing.blend`。当前场景无外部贴图依赖。

## 视觉检查

首轮 Eevee 图过暗，未用于几何判断；切换工作台渲染后重新生成并用 `view_image` 实看源 CAD 和正式外壳各五个方向。四角孔、圆角、厚度、旋钮滚花、摇杆帽轴孔可辨。USB 缺口方向/可视性不足，明确留到 PCB 装配批次核验，未宣称通过。
