import type {TouchAction} from './three/controller';
export type Mode='CODE'|'AUDIO'|'SHORTCUTS';
export type WorkstationState={mode:Mode;file:number;files:string[];palette:boolean;terminal:boolean;voice:boolean;side:boolean;model:number;volume:number;tone:number;delay:number;muted:boolean;playing:boolean;app:number;focus:number;status:string;history:string[];fontSize:number};
export const fileNames=['input.ts','controls.ts','session.json','notes.md'];
export const apps=['代码编辑器','音频混音台','文件管理','浏览器'];
export const initialWorkstation:WorkstationState={mode:'CODE',file:0,files:[`// ACID ALLOY · input mapping\n\nexport const instrument = {\n  keys: 13,\n  encoder: 'parameter',\n  joystick: 'navigate',\n  touch: 'trigger',\n};\n\nexport function onInput(key: string) {\n  return instrument.keys;\n}\n`,`// Continuous controls\n\nexport const gain = 72;\nexport const focus = { x: 0, y: 0 };\n`,`{\n  "session": "01",\n  "mode": "CODE",\n  "status": "ready"\n}\n`,`# Session notes\n\n在这里输入内容。\n旋钮调整字号，摇杆切换文件。`],palette:false,terminal:false,voice:false,side:false,model:0,volume:72,tone:50,delay:24,muted:false,playing:false,app:0,focus:0,status:'系统已就绪',history:[],fontSize:14};
export type WorkstationAction={type:'mode';mode:Mode}|{type:'key';id:string}|{type:'encoder';delta:number}|{type:'joystick';x:number;y:number}|{type:'touch';action:TouchAction}|{type:'edit';text:string}|{type:'file';index:number}|{type:'parameter';name:'volume'|'tone'|'delay';value:number}|{type:'mute'}|{type:'play'}|{type:'palette';open:boolean}|{type:'command';command:string}|{type:'app';index:number}|{type:'reset'};
const clamp=(n:number,a:number,b:number)=>Math.min(b,Math.max(a,n));
export function workstationReducer(state:WorkstationState,action:WorkstationAction):WorkstationState{
 let next={...state};let message='';
 switch(action.type){
  case 'mode':next.mode=action.mode;message=`切换到${{CODE:'代码',AUDIO:'音频',SHORTCUTS:'快捷键'}[action.mode]}模式`;break;
  case 'file':next.file=action.index;message=`打开 ${fileNames[action.index]}`;break;
  case 'edit':next.files=state.files.map((s,i)=>i===state.file?action.text:s);return next;
  case 'parameter':next[action.name]=clamp(action.value,0,100);message=`${{volume:'音量',tone:'音色',delay:'延迟'}[action.name]} ${next[action.name]}%`;break;
  case 'mute':next.muted=!state.muted;message=next.muted?'音频已静音':'音频已取消静音';break;
  case 'play':next.playing=!state.playing;message=next.playing?'电平演示运行中':'电平演示已暂停';break;
  case 'palette':next.palette=action.open;message=action.open?'命令面板已打开':'命令面板已关闭';break;
  case 'command':next.palette=false; if(action.command==='terminal')next.terminal=!state.terminal; if(action.command==='format')next.files=state.files.map((s,i)=>i===state.file?s.split('\n').map(l=>l.trimEnd()).join('\n'):s);if(action.command==='new')next.files=state.files.map((s,i)=>i===3?'# New session\n\n':s),next.file=3;message=action.command==='format'?'代码尾部空白已整理':action.command==='new'?'新会话笔记已创建':'终端显示已切换';break;
  case 'app':next.app=action.index;message=`切换应用 ${apps[action.index]}`;break;
  case 'encoder':
   if(state.mode==='CODE'){next.fontSize=clamp(state.fontSize+Math.sign(action.delta),12,22);message=`编辑器字号 ${next.fontSize}px`;}
   else{next.volume=clamp(state.volume+action.delta,0,100);message=`音量 ${next.volume}%`;}
   break;
  case 'joystick':{const direction=action.x||action.y;const delta=Math.sign(direction);next.focus=(state.focus+delta+4)%4;
   if(state.mode==='CODE')next.file=(state.file+delta+4)%4;
   if(state.mode==='SHORTCUTS')next.app=(state.app+delta+4)%4;
   if(state.mode==='AUDIO')next.tone=clamp(state.tone+delta*5,0,100);
   message=`摇杆 X:${action.x} Y:${action.y} · ${state.mode==='CODE'?fileNames[next.file]:state.mode==='AUDIO'?`音色 ${next.tone}%`:apps[next.app]}`;break;}
  case 'touch':
   if(action.action==='tap'){if(state.mode==='AUDIO'){next.playing=!state.playing;message=next.playing?'触摸 · 电平演示开始':'触摸 · 电平演示暂停';}else{next.palette=!state.palette;message='触摸 · 切换命令面板';}}
   else{next.app=(state.app+(action.action==='right'?1:3))%4;message=`触摸事件 · ${apps[next.app]}`;}break;
  case 'key':{const k=Number(action.id.replace('K',''));if(!Number.isInteger(k)||k<1||k>13)return state;
   if(k===1){next.file=0;message='已定位待处理会话';}
   if(k===2){next.file=3;next.files=state.files.map((s,i)=>i===3?'# New session\n\n':s);message='已新建会话笔记';}
   if(k>=3&&k<=6){next.file=k-3;next.app=k-3;if(state.mode==='AUDIO'){next.tone=[25,50,75,90][k-3];next.delay=[0,15,30,50][k-3];}message=`会话 ${k-2} 已选择`;}
   if(k===7){next.palette=true;message='命令面板已打开';}
   if(k===8){message='已批准当前模拟请求';}
   if(k===9){message='已拒绝当前模拟请求';next.playing=false;}
   if(k===10){next.terminal=!state.terminal;message=next.terminal?'终端已展开':'终端已收起';}
   if(k===11){next.voice=!state.voice;message=next.voice?'语音输入演示已启用':'语音输入演示已关闭';}
   if(k===12){next.side=!state.side;message=next.side?'侧边会话已打开':'侧边会话已关闭';}
   if(k===13){next.model=(state.model+1)%3;message=`模型选择 ${['标准','快速','深入'][next.model]}`;}
   message=`K${String(k).padStart(2,'0')} / ${message}`;break;}
  case 'reset':return {...initialWorkstation,files:[...initialWorkstation.files],status:'试用已复位'};
 }
 next.status=message;next.history=[message,...state.history].slice(0,8);return next;
}
