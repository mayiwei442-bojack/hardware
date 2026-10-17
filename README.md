# OpenMicroKbd 建模与外观方案

本仓库包含 OpenMicroKbd 原始建模文件、建模记录和四个独立外观方案。四个方案均基于原始模型制作副本，保留已有器件和交互结构； Acid Alloy 按照既定范围新增一块遮盖 PCB 的盖板。

## Blender 文件

| 版本 | 文件 | 方案说明 |
| --- | --- | --- |
| 原始建模 | [`modeling/assets/OpenMicroKbd.blend`](modeling/assets/OpenMicroKbd.blend) | OpenMicroKbd 装配、器件和交互控制的原始建模版本 |
| ① 酸性合金 | [`modeling/assets/OpenMicroKbd_AcidAlloy.blend`](modeling/assets/OpenMicroKbd_AcidAlloy.blend) | 荧酸绿实验面板、石墨外壳、紫色控制器、Codex 功能印花 |
| ② 电光瓷器 | [`modeling/assets/OpenMicroKbd_ElectricPorcelain.blend`](modeling/assets/OpenMicroKbd_ElectricPorcelain.blend) | 釉白与钴蓝、冰青透光键帽、电路纹样 |
| ③ 超频仪器 | [`modeling/assets/OpenMicroKbd_OverclockInstrument.blend`](modeling/assets/OpenMicroKbd_OverclockInstrument.blend) | 仪器白灰外壳、信号橙、增益刻度与校准印花 |
| ④ 反叛玩具 | [`modeling/assets/OpenMicroKbd_RebelToy.blend`](modeling/assets/OpenMicroKbd_RebelToy.blend) | 奶黄紫色撞色、亮面塑料、涂鸦与棋盘图形 |

## 预览

| 方案 | 主视渲染 |
| --- | --- |
| 酸性合金 | ![酸性合金](modeling/acid_alloy/renders/11_keyprints_hero.png) |
| 电光瓷器 | ![电光瓷器](modeling/electric_porcelain/renders/01_hero.png) |
| 超频仪器 | ![超频仪器](modeling/overclock_instrument/renders/01_overclock_hero.png) |
| 反叛玩具 | ![反叛玩具](modeling/rebel_toy/renders/01_hero.png) |

## 项目资料

- `modeling/`：原始模型、验收/操作文档、参考资料、过程检查点、渲染、材质与印花源文件。
- `modeling/acid_alloy/`、`electric_porcelain/`、`overclock_instrument/`、`rebel_toy/`：各方案的交付说明、渲染、贴图和可复现的印花脚本。
- Blender 自动保存文件（`.blend1`、`.blend2`）及 Acid Alloy 键帽印花调整前的临时备份不纳入版本控制。

请使用 Blender 打开 `.blend` 文件。印花贴图已内嵌到各成品文件中。
