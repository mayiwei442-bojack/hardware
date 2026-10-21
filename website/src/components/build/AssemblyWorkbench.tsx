'use client';
import {useEffect,useRef,useState} from 'react';
import dynamic from 'next/dynamic';
import {manualSlots,manualKind,type AssemblyState,type PartKind} from '@/data/build';
import BoardView,{LabSteps} from './BoardView';

const AssemblyModel=dynamic(()=>import('./AssemblyModel'),{ssr:false,loading:()=> <p className="lab-hint">正在加载三维模型…</p>});
const kinds:[PartKind,string,string][]=[['switch','机械轴','13 × Choc V2'],['encoder','编码器','1 × EC11'],['joystick','摇杆','1 × RKJXV']];
export default function AssemblyWorkbench({value,onChange,onComplete,done}:{value:AssemblyState;onChange:(v:AssemblyState)=>void;onComplete:()=>void;done:boolean}){
 const [selected,setSelected]=useState<PartKind>('switch');
 const [back,setBack]=useState(false);const [rotation,setRotation]=useState(0);const [model,setModel]=useState(false);
 const [message,setMessage]=useState('先选择机械轴，再点击发光的 SW03 孔位，完成第一颗安装。');
 const [heating,setHeating]=useState<string|null>(null);const [heat,setHeat]=useState(0);
 const timer=useRef<ReturnType<typeof setInterval>|null>(null);
 const stop=()=>{if(timer.current)clearInterval(timer.current);timer.current=null;setHeating(null);setHeat(0)};
 useEffect(()=>()=>{if(timer.current)clearInterval(timer.current)},[]);
 function install(id:string,kind=selected){
  if(manualKind(id)!==kind){setMessage('零件类型不匹配，请放到对应的发光轮廓中。');return;}
  if(value.installed.includes(id)){
   onChange({installed:value.installed.filter(v=>v!==id),soldered:value.soldered.filter(v=>v!==id)});setMessage(`${id} 已取下，可以重新安装。`);return;
  }
  if(value.installed.length===0&&id!=='SW03'){setMessage('首次安装请先完成 SW03，随后即可自由装配。');return;}
  onChange({...value,installed:[...value.installed,id]});setMessage(`${id} 已对准引脚并装入 PCB；翻到背面后固定焊点。`);
 }
 function solder(id:string){
  if(timer.current||!value.installed.includes(id)||value.soldered.includes(id))return;
  setHeating(id);setHeat(0);let progress=0;
  timer.current=setInterval(()=>{progress+=12.5;setHeat(progress);if(progress>=100){if(timer.current)clearInterval(timer.current);timer.current=null;setHeating(null);setHeat(0);onChange({...value,soldered:[...value.soldered,id]});setMessage(`${id} 焊点已形成，部件已固定。`)}},90);
 }
 const all=value.soldered.length===15;
 return <div className="assembly-workbench lab-panel">
  <div className="lab-panel-top"><span className="lab-badge">交互演示</span><span className="mono">装配工作台</span><span className="lab-live">{all?'装配检查通过':'等待你的操作'}</span></div>
  <LabSteps items={['选零件','对准孔位','放入零件','焊接固定','完成检查']} current={all?4:back?3:value.installed.length?2:0}/>
  <div className="assembly-desk">
   <aside className="parts-tray" aria-label="待安装零件"><h4>零件托盘</h4>{kinds.map(([kind,label,spec])=><button key={kind} draggable aria-label={`选择${label}`} aria-pressed={selected===kind} onClick={()=>{setSelected(kind);setBack(false);setModel(false);setMessage(`已选择${label}，点击或拖入对应轮廓。`)}} onDragStart={event=>{event.dataTransfer.setData('application/x-acid-part',kind);setSelected(kind);setBack(false)}}><i className={`part-icon ${kind}`} aria-hidden="true"/><strong>{label}</strong><small>{spec}</small><span>{value.installed.filter(id=>manualKind(id)===kind).length} / {kind==='switch'?13:1}</span></button>)}</aside>
   <div className="assembly-board-wrap" onDragOver={event=>event.preventDefault()} onDrop={event=>{event.preventDefault();if(!(event.target as Element).closest('.assembly-slot'))setMessage('尚未对准孔位，请将零件拖到对应的发光轮廓中。')}}>
    <div className="board-tools"><button aria-pressed={!model} onClick={()=>setModel(false)}>安装视图</button><button aria-pressed={model} onClick={()=>setModel(true)}>三维检查</button><button onClick={()=>{stop();setBack(!back);setModel(false)}}>{back?'翻到正面':'翻到背面'}</button></div>
    {model?<div className="assembly-model"><AssemblyModel installed={value.installed}/><p>拖动旋转 · 滚轮缩放 · 复用产品真实模型</p></div>:<BoardView side={back?'B':'T'} rotation={rotation}>
     {manualSlots.map(slot=>{const installed=value.installed.includes(slot.id);const fixed=value.soldered.includes(slot.id);const matching=manualKind(slot.id)===selected;return <button key={slot.id} className={`assembly-slot slot-${manualKind(slot.id)} ${installed?'installed':''} ${fixed?'fixed':''} ${!installed&&matching?'matching':''} ${heating===slot.id?'heating':''}`} style={{left:`${slot.x/95*100}%`,top:`${slot.y/95*100}%`,transform:`translate(-50%,-50%) rotate(${-rotation}deg)`,'--heat':`${heat}%`} as React.CSSProperties} aria-label={`${back?'焊接':installed?'取下':'安装'} ${slot.id}`} disabled={back&&(!installed||fixed)} onClick={()=>{if(!back)install(slot.id)}} onDragOver={event=>event.preventDefault()} onDrop={event=>{event.preventDefault();if(back)return;const kind=event.dataTransfer.getData('application/x-acid-part');if(['switch','encoder','joystick'].includes(kind))install(slot.id,kind as PartKind)}} onPointerDown={event=>{if(back){event.currentTarget.setPointerCapture(event.pointerId);solder(slot.id)}}} onPointerUp={stop} onPointerCancel={stop} onKeyDown={event=>{if(back&&(event.key===' '||event.key==='Enter')){event.preventDefault();if(!event.repeat)solder(slot.id)}}} onKeyUp={stop} onBlur={stop}><span aria-hidden="true" className="slot-part">{back?(fixed?'●':'◉'):installed?(manualKind(slot.id)==='switch'?'＋':manualKind(slot.id)==='encoder'?'◉':'⊕'):'+'}</span><small>{slot.id}</small></button>})}
    </BoardView>}
    {!model?<label className="board-rotation">旋转 PCB<input type="range" min="-30" max="30" value={rotation} onChange={e=>setRotation(Number(e.target.value))}/><span>{rotation}°</span></label>:null}
   </div>
   <aside className="assembly-guide"><span className="mono muted">装配进度</span><strong>{String(value.installed.length).padStart(2,'0')}<small>/ 15</small></strong><p>已安装 {value.installed.length} / 15</p><p>已固定 {value.soldered.length} / 15</p><div className="lab-meter"><span style={{width:`${value.soldered.length/15*100}%`}}/></div><p className="lab-hint">{back?'长按焊点约 0.7 秒形成焊锡。键盘可聚焦焊点后长按空格。':'点击零件，再点击孔位；桌面端也可拖入。点击已安装部件可取下。'}</p>
    {value.installed.some(id=>manualKind(id)==='switch')&&value.installed.filter(id=>manualKind(id)==='switch').length<13?<button className="btn small" onClick={()=>{onChange({...value,installed:[...new Set([...value.installed,...manualSlots.filter(p=>manualKind(p.id)==='switch').map(p=>p.id)])]});setMessage('其余机械轴已依次装入。接下来安装编码器和摇杆。')}}>自动安装剩余机械轴</button>:null}
    {back?<button className="btn small" disabled={value.installed.length!==15||all||!!heating} onClick={()=>{onChange({...value,soldered:[...value.installed]});setMessage('全部引脚固定完成，机械轴、编码器和摇杆装配检查通过。')}}>演示焊接其余焊点</button>:null}
   </aside>
  </div>
  <p className="lab-message" role="status">{message}</p>
  <div className="lab-bottom"><span>15 个手工部件 · 外壳与键帽留待打印后组装</span><button className="btn primary" disabled={!all||done} onClick={onComplete}>{done?'手工装配已完成':'确认手工装配'}</button></div>
 </div>;
}
