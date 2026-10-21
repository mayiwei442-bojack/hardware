'use client';

import dynamic from 'next/dynamic';
import {Component,useCallback,useEffect,useMemo,useRef,useState,type ReactNode} from 'react';
import {useReducedMotion} from 'motion/react';
import {hardwareLabels,hardwareParts,type PartSelection} from '@/data/hardware';
import {createSceneController} from '@/lib/three/controller';

const HardwareScene=dynamic(()=>import('../three/HardwareScene'),{ssr:false});
class SceneBoundary extends Component<{children:ReactNode;onRetry:()=>void;onError:()=>void},{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 componentDidCatch(){this.props.onError();}
 render(){return this.state.failed?<div className="hardware-loading" role="alert"><p>模型暂时无法加载</p><button className="btn small" onClick={this.props.onRetry}>重新加载</button></div>:this.props.children;}
}

export default function Hardware(){
 const section=useRef<HTMLElement>(null);
 const viewport=useRef<HTMLDivElement>(null);
 const controller=useMemo(createSceneController,[]);
 const reduced=!!useReducedMotion();
 const [nearby,setNearby]=useState(false);
 const [active,setActive]=useState(false);
 const [loaded,setLoaded]=useState(false);
 const [complete,setComplete]=useState(false);
 const [selected,setSelected]=useState<PartSelection|null>(null);
 const [attempt,setAttempt]=useState(0);
 const [failed,setFailed]=useState(false);
 const [focusReady,setFocusReady]=useState(false);
 const back=useRef<HTMLButtonElement>(null);
 const selectedRef=useRef(selected);
 const close=useCallback(()=>{
  const part=selectedRef.current?.part;
  setSelected(null);
  requestAnimationFrame(()=>{if(part)section.current?.querySelector<HTMLButtonElement>(`[data-part="${part}"]`)?.focus({preventScroll:true});});
 },[]);
 useEffect(()=>{selectedRef.current=selected;},[selected]);
 useEffect(()=>{
  const element=section.current;
  if(!element)return;
  const observer=new IntersectionObserver(entries=>setNearby(entries[0].isIntersecting),{rootMargin:'1000px 0px'});
  observer.observe(element);
  return()=>observer.disconnect();
 },[]);
 useEffect(()=>{
  let frame=0;
  const update=()=>{
   frame=0;
   if(!section.current||!viewport.current)return;
   const rect=section.current.getBoundingClientRect();
   const height=viewport.current.clientHeight;
   const progress=Math.max(0,Math.min(1,-rect.top/(height*2.35)));
   controller.setProgress(progress);
   section.current.dataset.progress=progress.toFixed(3);
   setActive(rect.top<height&&rect.bottom>0);
   if(selectedRef.current&&(progress<.99||rect.bottom<height*.25))setSelected(null);
  };
  const schedule=()=>{if(!frame)frame=requestAnimationFrame(update);};
  update();
  window.addEventListener('scroll',schedule,{passive:true});
  window.addEventListener('resize',schedule);
  return()=>{cancelAnimationFrame(frame);window.removeEventListener('scroll',schedule);window.removeEventListener('resize',schedule);};
 },[controller]);
 useEffect(()=>{
  if(!selected)return;
  const escape=(event:KeyboardEvent)=>{if(event.key==='Escape')close();};
  window.addEventListener('keydown',escape);
  back.current?.focus({preventScroll:true});
  return()=>window.removeEventListener('keydown',escape);
 },[selected,close]);
 const select=useCallback((value:PartSelection)=>{setFocusReady(false);setSelected(value);},[]);
 const onLoaded=useCallback(()=>setLoaded(true),[]);
 const onComplete=useCallback((value:boolean)=>setComplete(value),[]);
 const onFocusReady=useCallback((value:boolean)=>setFocusReady(value),[]);
 const onError=useCallback(()=>{setFailed(true);setLoaded(false);setComplete(false);setSelected(null);},[]);
 const retry=()=>{setLoaded(false);setFailed(false);setAttempt(value=>value+1);};
 const item=selected?hardwareParts[selected.part]:null;
 const capNumber=selected?.part==='keycaps'?selected.node.match(/SW\d+/)?.[0]:null;
 const phase=selected?'inspecting':complete?'exploded':'assembling';

 return <section id="hardware" ref={section} className="hardware-experience" aria-label="硬件解构" data-phase={phase} data-loaded={loaded} data-focus-ready={focusReady}>
  <div className="hardware-viewport" ref={viewport}>
   <h2 className="sr-only">硬件解构</h2>
   <div className={`hardware-canvas${selected?' is-inspecting':''}`}>
    {nearby?<SceneBoundary key={attempt} onRetry={retry} onError={onError}><HardwareScene controller={controller} selected={selected} onSelect={select} onLoaded={onLoaded} onComplete={onComplete} onFocusReady={onFocusReady} reduced={reduced} active={active} attempt={attempt}/></SceneBoundary>:null}
   </div>
   {!loaded&&!failed?<div className="hardware-loading" role="status"><span className="hardware-loader"/><span>正在加载键盘模型</span></div>:null}
   {loaded&&complete&&!selected?<div className="hardware-part-labels" role="group" aria-label="选择硬件部件">{hardwareLabels.map((id,index)=><button key={id} data-part={id} className={`hardware-part-label label-${index}`} onClick={()=>select({part:id,node:hardwareParts[id].node})}><span className="part-label-dot"/>{hardwareParts[id].name}<span aria-hidden="true">↗</span></button>)}</div>:null}
   {selected&&item?<>
    <button ref={back} className="hardware-back" onClick={close}><span aria-hidden="true">↖</span> 返回解构总览 <kbd>ESC</kbd></button>
    <aside className="hardware-part-card" aria-label={`${item.name}下载`}>
     <span className="hardware-card-index mono">{capNumber||'ACID / ALLOY'}</span>
     <h3>{item.name}</h3><p>{item.detail}</p>
     <div className="hardware-downloads">{capNumber?<a href={`/downloads/acid-alloy-keycap-${capNumber}.stl`} download>下载此键帽 · STL <span aria-hidden="true">↓</span></a>:null}{item.downloads.map(download=><a key={download.href} href={download.href} download>{download.label}<span aria-hidden="true">↓</span></a>)}</div>
    </aside>
   </>:null}
   {loaded?<div className="hardware-scroll-hint" aria-live="polite">{selected?<><span className="hint-orbit" aria-hidden="true">↔</span> 拖动旋转，查看细节</>:complete?<>点击部件或名称，查看细节 <span aria-hidden="true">·</span> 继续下滑浏览</>:<>向下滚动，展开设备 <span className="hint-down" aria-hidden="true">↓</span></>}</div>:null}
  </div>
 </section>;
}
