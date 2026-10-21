export type HardwarePartId = 'keycaps'|'switches'|'knob'|'encoder'|'joystickCap'|'joystick'|'touch'|'panel'|'pcb'|'lighting'|'enclosure'|'fasteners';
export type PartSelection = {part:HardwarePartId;node:string};
type Download = {label:string;href:string};
type HardwarePart = {name:string;detail:string;node:string;downloads:Download[]};
const file=(name:string)=>`/downloads/${name}`;
export const hardwareParts:Record<HardwarePartId,HardwarePart> = {
 keycaps:{name:'键帽',detail:'13 个独立键帽 · STL / 毫米',node:'keycap_SW03',downloads:[{label:'下载全部键帽 · STL',href:file('acid-alloy-keycaps.zip')}]},
 switches:{name:'机械轴',detail:'Kailh Choc V2 · 13 个独立输入',node:'switch_SW03',downloads:[{label:'下载元件清单 · BOM',href:file('openmicro-bom.csv')}]},
 knob:{name:'旋钮',detail:'六角旋钮 · 3D 打印模型',node:'knob',downloads:[{label:'下载旋钮 · STL',href:file('acid-alloy-knob.stl')}]},
 encoder:{name:'旋转编码器',detail:'EC11 · 旋转与按压输入',node:'encoder',downloads:[{label:'下载元件清单 · BOM',href:file('openmicro-bom.csv')}]},
 joystickCap:{name:'摇杆帽',detail:'紫色摇杆帽 · 3D 打印模型',node:'joystickCap',downloads:[{label:'下载摇杆帽 · STL',href:file('acid-alloy-joystick-cap.stl')}]},
 joystick:{name:'模拟摇杆',detail:'RKJXV · 双轴模拟输入',node:'joystick',downloads:[{label:'下载元件清单 · BOM',href:file('openmicro-bom.csv')}]},
 touch:{name:'触摸区',detail:'电容感应区域 · PCB 铜箔',node:'touch',downloads:[{label:'下载电路板制造资料',href:file('openmicro-pcb-fabrication.zip')}]},
 panel:{name:'盖板',detail:'酸绿遮板 · 3D 打印模型',node:'panel',downloads:[{label:'下载盖板 · STL',href:file('acid-alloy-panel.stl')}]},
 pcb:{name:'PCB',detail:'95 × 95 mm · 四层 FR-4',node:'pcb',downloads:[{label:'下载打板材料包',href:file('openmicro-pcb-fabrication.zip')},{label:'Gerber',href:file('openmicro-gerbers.zip')},{label:'BOM',href:file('openmicro-bom.csv')},{label:'贴片坐标',href:file('openmicro-smt.csv')}]},
 lighting:{name:'RGB 灯珠',detail:'13 个单键灯珠 + 8 个底部灯珠',node:'lighting',downloads:[{label:'下载元件清单 · BOM',href:file('openmicro-bom.csv')}]},
 enclosure:{name:'底壳',detail:'底部外壳 · 3MF 打印模型',node:'enclosure',downloads:[{label:'下载底壳 · 3MF',href:file('OpenMicroKbkCase.3mf')}]},
 fasteners:{name:'固定螺丝',detail:'设备固定组件',node:'fasteners',downloads:[{label:'下载元件清单 · BOM',href:file('openmicro-bom.csv')}]},
};
export const hardwareLabels:HardwarePartId[]=['knob','keycaps','joystickCap','switches','panel','touch','pcb','enclosure'];
