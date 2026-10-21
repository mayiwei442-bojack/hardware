import {codexKeys,shortcutApps,shortcutExamples,type Platform,type ShortcutApp} from '@/data/trial';
import type {TouchAction} from './three/controller';

export type Mode='CODEX'|'MEDIA'|'SHORTCUTS';
export type MediaScene='music'|'lesson';
export type WorkstationState={
 mode:Mode;platform:Platform;session:number;newChat:boolean;request:'pending'|'approved'|'rejected';
 terminalOpen:boolean;sideOpen:boolean;volume:number;muted:boolean;playing:boolean;mediaScene:MediaScene;
 shortcutApp:ShortcutApp;lastShortcut:string|null;navigation:{row:number;col:number};status:string;history:string[];
};
export const initialWorkstation:WorkstationState={
 mode:'CODEX',platform:'windows',session:0,newChat:false,request:'pending',terminalOpen:false,sideOpen:false,
 volume:70,muted:false,playing:true,mediaScene:'music',shortcutApp:'vscode',lastShortcut:null,
 navigation:{row:1,col:1},status:'选择一个输入，查看原项目支持的操作示例。',history:[],
};
export type WorkstationAction=
 |{type:'mode';mode:Mode}|{type:'platform';platform:Platform}|{type:'key';id:string}
 |{type:'encoder';delta:number}|{type:'mute'}|{type:'joystick';x:number;y:number}
 |{type:'touch';action:TouchAction}|{type:'play'}|{type:'scene';scene:MediaScene}
 |{type:'shortcut-app';app:ShortcutApp}|{type:'shortcut';id:string}|{type:'reset'};
const clamp=(n:number,a:number,b:number)=>Math.min(b,Math.max(a,n));
export function workstationReducer(state:WorkstationState,action:WorkstationAction):WorkstationState{
 const next={...state};let message='';
 switch(action.type){
  case 'mode':next.mode=action.mode;message='查看'+{CODEX:'Codex 按键',MEDIA:'媒体控制',SHORTCUTS:'应用快捷键'}[action.mode]+'示例';break;
  case 'platform':next.platform=action.platform;message='显示 '+(action.platform==='mac'?'macOS':'Windows / Linux')+' 组合键';break;
  case 'key':{
   const index=codexKeys.findIndex(key=>key.id===action.id);if(index<0)return state;
   const key=codexKeys[index];next.mode='CODEX';
   if(index===0){next.session=0;next.newChat=false;}
   if(index===1)next.newChat=true;
   if(index>=2&&index<=5){next.session=index-2;next.newChat=false;}
   if(index===7)next.request='approved';
   if(index===8)next.request='rejected';
   if(index===9)next.terminalOpen=!state.terminalOpen;
   if(index===11)next.sideOpen=!state.sideOpen;
   message=key.id+' · '+key[state.platform]+' → '+key.action+'（本页示例）';break;
  }
  case 'encoder':next.mode='MEDIA';next.volume=clamp(state.volume+action.delta,0,100);message='音量'+(action.delta>0?'增加':'降低')+' · 演示值 '+next.volume+'%';break;
  case 'mute':next.mode='MEDIA';next.muted=!state.muted;message='按压旋钮 · '+(next.muted?'静音':'取消静音')+'（本页示例）';break;
  case 'joystick':{
   if(!action.x&&!action.y)return state;
   next.navigation={row:clamp(state.navigation.row+Math.sign(action.y),0,2),col:clamp(state.navigation.col+Math.sign(action.x),0,2)};
   message='方向键 '+(action.x<0?'←':action.x>0?'→':'')+(action.y<0?'↑':action.y>0?'↓':'')+' · 移动示例选中项';break;
  }
  case 'touch':
   // V1 is a single-zone pad: swipe slots in the protocol are not detectable by this hardware.
   if(action.action!=='tap')return state;
   next.mode='MEDIA';next.playing=!state.playing;message='轻触触摸板 → 播放 / 暂停 → 示例媒体已'+(next.playing?'继续':'暂停');break;
  case 'play':next.playing=!state.playing;message='播放器示例已'+(next.playing?'继续':'暂停');break;
  case 'scene':next.mediaScene=action.scene;next.playing=true;message='场景示例：'+(action.scene==='music'?'工作时控制背景音乐':'暂停教程，跟着操作');break;
  case 'shortcut-app':
   if(!shortcutApps.some(app=>app.id===action.app))return state;
   next.shortcutApp=action.app;next.lastShortcut=null;message='查看 '+shortcutApps.find(app=>app.id===action.app)!.name+' 快捷键示例';break;
  case 'shortcut':{
   const example=shortcutExamples.find(item=>item.id===action.id&&item.app===state.shortcutApp);if(!example)return state;
   next.lastShortcut=example.id;message='示例：'+example.target+' · '+example[state.platform]+' → '+example.action;break;
  }
  case 'reset':return {...initialWorkstation,navigation:{...initialWorkstation.navigation},status:'试用已复位'};
 }
 next.status=message;next.history=[message,...state.history].slice(0,4);return next;
}
