'use client';
import {useCallback,useEffect,useMemo,useReducer,useRef,useState} from 'react';
import {initialWorkstation,workstationReducer,type Mode} from '@/lib/input';
import type {InputController} from '@/lib/three/controller';
import InputPanel from '../interactive/InputPanel';
import ComputerScreen,{type ScreenView} from '../interactive/ComputerScreen';
import {SectionLabel} from '../ui/Primitives';
export default function Workstation(){
 const [state,dispatch]=useReducer(workstationReducer,initialWorkstation);
 const [view,setView]=useState<ScreenView>('ready');const [resetVersion,setResetVersion]=useState(0);
 const [vector,setVector]=useState({x:0,y:0});const root=useRef<HTMLElement>(null);
 const key=useCallback((id:string)=>{if(!/^K(0[1-9]|1[0-3])$/.test(id))return;dispatch({type:'key',id});setView(id as ScreenView)},[]);
 const inputs=useMemo<InputController>(()=>({
  onKeyPress:key,
  onEncoderRotate:delta=>{dispatch({type:'encoder',delta});setView('encoder')},
  onEncoderPress:()=>{dispatch({type:'mute'});setView('encoder')},
  onJoystickMove:(x,y)=>{dispatch({type:'joystick',x,y});setVector({x,y});setView('joystick')},
  onTouchPadAction:action=>{if(action!=='tap')return;dispatch({type:'touch',action});setView('touch')},
 }),[key]);
 useEffect(()=>{const el=root.current;const handle=(event:KeyboardEvent)=>{
  const target=event.target;
  if(event.ctrlKey||event.altKey||event.metaKey||event.repeat||event.defaultPrevented||target instanceof HTMLInputElement||target instanceof HTMLTextAreaElement||target instanceof HTMLElement&&target.isContentEditable)return;
  const index='1234567890qwe'.indexOf(event.key.toLowerCase());
  if(index>=0){event.preventDefault();key('K'+String(index+1).padStart(2,'0'))}
 };el?.addEventListener('keydown',handle);return()=>el?.removeEventListener('keydown',handle)},[key]);
 function mode(value:Mode){dispatch({type:'mode',mode:value});setView(value)}
 function reset(){setResetVersion(value=>value+1);dispatch({type:'reset'});setView('ready');setVector({x:0,y:0})}
 return <section ref={root} id="try" className="section try-section" tabIndex={-1} aria-label="交互试用工作台">
  <SectionLabel n="03" label="交互试用"/>
  <div className="try-introduction" data-reveal><h2>按下，即刻响应。</h2><p>点按键帽，查看 Codex 快捷键。旋转调音量，按压静音。<br/>拨动摇杆导航，轻触触摸板暂停或继续媒体。</p></div>
  <div className="try-desk"><InputPanel key={resetVersion} inputs={inputs} active={view}/><ComputerScreen state={state} dispatch={dispatch} view={view} onKey={key} onView={setView} onMode={mode} onReset={reset} vector={vector}/></div>
 </section>;
}
