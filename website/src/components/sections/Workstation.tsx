'use client';
import {useCallback,useEffect,useMemo,useReducer,useRef,useState} from 'react';
import {initialWorkstation,workstationReducer,type Mode} from '@/lib/input';
import type {InputController} from '@/lib/three/controller';
import InputPanel from '../interactive/InputPanel';
import ComputerScreen,{type ScreenView} from '../interactive/ComputerScreen';
import {SectionLabel} from '../ui/Primitives';
export default function Workstation(){
 const [state,dispatch]=useReducer(workstationReducer,initialWorkstation);const [view,setView]=useState<ScreenView>('ready');const [touches,setTouches]=useState(0);const [resetVersion,setResetVersion]=useState(0);const [vector,setVector]=useState({x:0,y:0});const [note,setNote]=useState('记录这次会话的想法…');const root=useRef<HTMLElement>(null);
 const key=useCallback((id:string)=>{if(!/^K(0[1-9]|1[0-3])$/.test(id))return;dispatch({type:'key',id});setView(id as ScreenView)},[]);
 const inputs=useMemo<InputController>(()=>({onKeyPress:key,onEncoderRotate:delta=>{dispatch({type:'encoder',delta,target:view==='K13'?'effort':undefined});if(view!=='K13')setView('encoder')},onJoystickMove:(x,y)=>{dispatch({type:'joystick',x,y});setVector({x,y});setView('joystick')},onTouchPadAction:action=>{dispatch({type:'touch',action});setTouches(count=>count+1);setView('touch')}}),[key,view]);
 useEffect(()=>{const el=root.current;const handle=(event:KeyboardEvent)=>{const target=event.target;if(event.ctrlKey||event.altKey||event.metaKey||event.repeat||target instanceof HTMLInputElement||target instanceof HTMLTextAreaElement)return;const index='1234567890qwe'.indexOf(event.key.toLowerCase());if(index>=0){event.preventDefault();key(`K${String(index+1).padStart(2,'0')}`)}};el?.addEventListener('keydown',handle);return()=>el?.removeEventListener('keydown',handle)},[key]);
 function mode(value:Mode){dispatch({type:'mode',mode:value});setView(value)}
 function reset(){setResetVersion(value=>value+1);dispatch({type:'reset'});setView('ready');setTouches(0);setVector({x:0,y:0});setNote('记录这次会话的想法…')}
 return <section ref={root} id="try" className="section try-section" tabIndex={-1} aria-label="交互试用工作台"><SectionLabel n="03" label="交互试用"/><div className="try-introduction" data-reveal><h2>按下，即刻响应。</h2><p>点按左侧键帽，在右侧查看对应功能。<br/>拖动或滚动旋钮，拨动摇杆，轻触触摸板。</p></div><div className="try-desk"><InputPanel key={resetVersion} inputs={inputs} active={view}/><ComputerScreen state={state} dispatch={dispatch} view={view} onView={setView} onMode={mode} onReset={reset} vector={vector} touches={touches} note={note} onNote={setNote}/></div></section>;
}
