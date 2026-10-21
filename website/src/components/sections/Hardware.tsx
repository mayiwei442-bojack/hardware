'use client';
import {useEffect,useMemo,useRef,useState} from 'react';
import {motion,AnimatePresence,useReducedMotion} from 'motion/react';
import {hardware,assemblyStages} from '@/data/product';
import {assets} from '@/data/assets';
import {createSceneController} from '@/lib/three/controller';
import {bindSceneScroll} from '@/lib/animations/usePageMotion';
import ModelSlot from '../three/ModelSlot';
import {SectionLabel} from '../ui/Primitives';
export default function Hardware(){
 const [selected,setSelected]=useState(0);const [progress,setProgress]=useState(0);const [notice,setNotice]=useState('');const reduced=useReducedMotion();const ref=useRef<HTMLDivElement>(null);
 const controller=useMemo(createSceneController,[]);const ready=assets.models.keyboardExploded.status==='ready'&&!!assets.models.keyboardExploded.src;
 useEffect(()=>ref.current?bindSceneScroll(ref.current,controller,ready&&!reduced):undefined,[controller,ready,reduced]);
 const item=hardware[selected];const stage=Math.min(5,Math.floor(progress*6/101));
 return <section id="hardware" className="section"><SectionLabel n="02" label="硬件解构"/><div className="section-heading" data-reveal><h2>逐一认识输入。<br/><span className="serif-line">一台控制设备。</span></h2><p>从触感到控制核心。<br/>逐个查看构成酸性合金的部件。</p></div><div className="hardware-layout" ref={ref}><div className="hardware-visual"><ModelSlot id="keyboardExploded" controller={controller}/><div className="assembly-control"><div className="between mono"><label htmlFor="assembly">装配阶段 / {assemblyStages[stage]}</label><span>{progress.toString().padStart(3,'0')}%</span></div><input id="assembly" aria-label="拆解阶段预览" type="range" min="0" max="100" value={progress} onChange={e=>{const value=Number(e.target.value);setProgress(value);controller.setProgress(value/100);setNotice(ready?'':'阶段预览已更新，三维动画待接入。')}}/><div className="between"><small>{ready?'拖动查看装配阶段':'界面预览 · 三维拆解待接入'}</small><button className="text-button" onClick={()=>{setProgress(0);controller.resetAssembly();setNotice('已回到完整键盘阶段。')}}>重置装配 ↺</button></div><span className="sr-only" role="status">{notice}</span></div></div><div className="hardware-info"><div className="part-menu" role="group" aria-label="硬件部件">{hardware.map((part,i)=><button key={part.id} aria-pressed={selected===i} onClick={()=>setSelected(i)}><span className="mono">0{i+1}</span>{part.name}<span aria-hidden="true">↗</span></button>)}</div><AnimatePresence mode="wait" initial={false}><motion.div className="part-detail" key={item.id} initial={{opacity:0,x:reduced?0:12}} animate={{opacity:1,x:0}} exit={{opacity:0,x:reduced?0:-12}} transition={{duration:.18}}><div className="between"><span className="mono">{item.cn}</span><span className="tag">{item.type}</span></div><strong className="part-value">{item.value}</strong><span className="mono part-unit">{item.unit}</span><p>{item.desc}</p><ul>{item.specs.map(s=><li key={s}>{s}</li>)}</ul></motion.div></AnimatePresence></div></div></section>;
}
