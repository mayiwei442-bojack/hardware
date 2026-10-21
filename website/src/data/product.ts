export const sections=[['overview','01','概览'],['hardware','02','硬件'],['try','03','交互试用'],['build','04','制作流程'],['resources','05','项目资料']] as const;
export const resources={
 project:'https://github.com/mayiwei442-bojack/hardware',
 projectZip:'https://github.com/mayiwei442-bojack/hardware/archive/refs/heads/main.zip',
 sourceZip:'https://github.com/mayiwei442-bojack/hardware/archive/refs/heads/main.zip',
 gerber:'https://github.com/mayiwei442-bojack/hardware/raw/refs/heads/main/device/hw/v1/fab/openmicro-gerbers.zip',
 bom:'https://github.com/mayiwei442-bojack/hardware/raw/refs/heads/main/device/hw/v1/fab/openmicro-bom.csv',
 smt:'https://github.com/mayiwei442-bojack/hardware/raw/refs/heads/main/device/hw/v1/fab/openmicro-smt.csv',
 shell:'https://raw.githubusercontent.com/mayiwei442-bojack/hardware/main/device/hw/v1/mechanical/OpenMicroKbkCase.3mf',
 knob:'https://raw.githubusercontent.com/mayiwei442-bojack/hardware/main/device/hw/v1/mechanical/OpenMicroRotator.3mf',
 joystickCap:'https://raw.githubusercontent.com/mayiwei442-bojack/hardware/main/device/hw/v1/mechanical/OpenMicroJoystickCap.3mf',
 mechanical:'https://github.com/mayiwei442-bojack/hardware/tree/main/device/hw/v1/mechanical',
 firmware:'https://github.com/conol-ai/openmicrokbd/releases/download/v0.15.0/openmicro-fw-0.10.1.hex',
};
export const hardware=[
 {id:'keycaps',name:'键帽',cn:'指尖接触面',value:'13',unit:'定制键帽',desc:'烟黑与半透明黄绿键帽，紫色重点键。编号与功能印花明确区分每个输入。',type:'外观方案',specs:['酸性合金配色','自定义功能印花']},
 {id:'switches',name:'机械轴',cn:'机械输入',value:'13',unit:'Kailh Choc V2',desc:'13 个独立机械轴，低矮轴体与 MX 十字轴心。',type:'硬件规格',specs:['Kailh Choc V2','13 个独立输入']},
 {id:'encoder',name:'旋转编码器',cn:'连续调节',value:'EC11',unit:'旋转编码器',desc:'旋转调节参数，按压触发操作。',type:'硬件规格',specs:['EC11E15244A5','旋转 + 按压']},
 {id:'joystick',name:'模拟摇杆',cn:'双轴控制',value:'XY',unit:'模拟输入',desc:'双轴模拟输入，配合独立按压开关。',type:'硬件规格',specs:['RKJXV122400R','X / Y + 按压']},
 {id:'touch',name:'触摸板',cn:'轻触输入',value:'01',unit:'电容触摸区',desc:'单区域电容触摸输入。试用界面以轻触触发播放或命令。',type:'硬件规格',specs:['电容式感应','单触摸区']},
 {id:'pcb',name:'PCB',cn:'控制核心',value:'95×95',unit:'毫米 / 4 层',desc:'STM32F072CBT6 控制核心，四层 FR-4 电路板。',type:'硬件规格',specs:['1.6 毫米 FR-4 · 1 盎司铜厚','STM32F072CBT6']},
 {id:'lighting',name:'灯光' ,cn:'输入反馈',value:'21',unit:'可寻址 RGB',desc:'13 个单键 RGB LED 与 8 个底部 RGB LED。',type:'硬件规格',specs:['13 个单键 + 8 个底部灯珠','独立可寻址 RGB']},
 {id:'enclosure',name:'外壳' ,cn:'外壳与遮板',value:'02',unit:'外部组件',desc:'三维打印底壳与定制遮板。石墨外壳搭配酸绿面板。',type:'外观方案',specs:['定制 PCB 遮板','石墨黑 / 酸绿']},
];
export const assemblyStages=['完整键盘','键帽分离','机械轴分离','遮板抬升','PCB 显露','底壳分离'];
export const keyLabels=['待处理','新建','会话 1','会话 2','会话 3','会话 4','命令','确认','拒绝','终端','语音','侧栏','模式'];
