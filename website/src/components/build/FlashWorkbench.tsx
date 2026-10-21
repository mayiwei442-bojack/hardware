'use client';
import {useEffect,type Dispatch,type SetStateAction} from 'react';
import type {FlashState} from '@/data/build';
import FilePicker from '../interactive/FilePicker';
import BoardView,{LabSteps} from './BoardView';

export default function FlashWorkbench({value,onChange,onInvalidate,onComplete,done}:{value:FlashState;onChange:Dispatch<SetStateAction<FlashState>>;onInvalidate:()=>void;onComplete:()=>void;done:boolean}){
 const {phase,connected,progress}=value;
 const busy=['writing','verifying','booting'].includes(phase);
 useEffect(()=>{
  if(phase==='writing'){
   const timer=setInterval(()=>onChange(old=>old.phase!=='writing'?old:{...old,progress:Math.min(100,old.progress+2),phase:old.progress>=98?'written':'writing'}),110);
   return()=>clearInterval(timer);
  }
  if(phase==='verifying'||phase==='booting'){
   const timer=setTimeout(()=>onChange(old=>({...old,phase:phase==='verifying'?'verified':'booted'})),phase==='verifying'?1200:800);
   return()=>clearTimeout(timer);
  }
 },[phase,onChange]);
 useEffect(()=>{if(phase==='booted'&&!done)onComplete()},[phase,done,onComplete]);
 function connection(){
  onInvalidate();
  onChange(old=>({...old,connected:!old.connected,phase:old.connected&&old.phase!=='idle'?'interrupted':old.phase==='interrupted'?'interrupted':'idle',progress:old.connected?old.progress:0}));
 }
 const status=phase==='writing'?'数据正在写入 STM32':phase==='interrupted'?(connected?'烧录演示已中止，请重新烧录。':'连接已断开，请重新连接后重试。'):phase==='written'?'写入完成，请校验固件。':phase==='verifying'?'正在逐页校验写入内容…':phase==='verified'?'校验通过，可以重新启动。':phase==='booting'?'正在启动键盘…':phase==='booted'?'键盘已启动':connected?'演示设备已连接，请选择固件。':'将 SWD 连接线接到 PCB 的 J2 接口。';
 return <div className={`lab-panel flash-workbench flash-${phase}`}>
  <div className="lab-panel-top"><span className="lab-badge">交互演示</span><span className="mono">固件烧录工作台</span><span className={`lab-live ${connected?'':'offline'}`}>{connected?'SWD 已连接':'设备未连接'}</span></div>
  <LabSteps items={['接线','选择固件','写入','校验','启动']} current={phase==='booted'?5:['booting','verified'].includes(phase)?4:['written','verifying'].includes(phase)?3:phase==='writing'?2:connected?1:0}/>
  <div className="flash-desk">
   <div className="flash-visual">
    <div className="board-tools"><span>SWD / J2</span><span>{phase==='booted'?'USB 1209:0001':'STM32F072CBT6'}</span></div>
    <BoardView side="B" lit={phase==='booted'}>
     {phase!=='booted'?<div className={`chip-memory ${phase==='verifying'?'scanning':''}`} aria-label="芯片写入示意"><span>STM32</span><div>{Array.from({length:64},(_,i)=><i key={i} className={i<progress/100*64?'filled':''}/>)}</div></div>:null}
     {phase==='booted'?<div className="boot-keyboard" aria-label="完整键盘启动预览">{Array.from({length:13},(_,i)=><span key={i}>{String(i+1).padStart(2,'0')}</span>)}</div>:null}
     <button className={`swd-port ${connected?'connected':''}`} aria-label={connected?'断开 SWD 接口':'连接 SWD 接口'} onClick={connection} onDragOver={event=>event.preventDefault()} onDrop={event=>{event.preventDefault();if(!connected&&event.dataTransfer.getData('application/x-acid-cable')==='swd')connection()}}>J2<span>{connected?'● ● ●':'○ ○ ○'}</span></button>
    </BoardView>
    <div className={`swd-cable ${connected?'connected':''} ${phase==='writing'?'transferring':''}`} aria-hidden="true"><i/><i/><i/></div>
    <button className="programmer" draggable={!connected} onDragStart={event=>event.dataTransfer.setData('application/x-acid-cable','swd')} onClick={connection} aria-label={connected?'断开连接':'点击连接'}><i className={connected?'connected':''}/><span>SWD 烧录器<small>{connected?'点击断开连接':'拖到 J2 或点击连接'}</small></span><b>{connected?'×':'↗'}</b></button>
    <p className="lab-hint">J2：GND / SWCLK / SWDIO。此接口无 3.3 V 引脚，真实设备需通过 USB-C 供电。</p>
   </div>
   <div className="flash-controls">
    <fieldset disabled={busy}><FilePicker label="固件 / HEX" kind="hex" value={value.file} preset="keyboard-fw-0.10.1.hex" presetBytes={266018} onChange={(file,bytes)=>{onInvalidate();onChange(old=>({...old,file,bytes:bytes||0,progress:0,phase:'idle'}))}}/></fieldset>
    <dl className="flash-file-info"><div><dt>文件大小</dt><dd>{value.file?(value.bytes?`${(value.bytes/1024).toFixed(1)} KB`:'内置示例 · 大小以下载文件为准'):'—'}</dd></div><div><dt>目标地址</dt><dd className="mono">0x08000000</dd></div><div><dt>固件内容</dt><dd>Bootloader + Application</dd></div></dl>
    <div className="flash-progress" role="progressbar" aria-label="固件写入进度" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}><span>写入进度</span><strong className="mono">{progress}%</strong><div className="lab-meter"><span style={{width:`${progress}%`}}/></div></div>
    <div className="flash-actions"><button className="btn primary" disabled={!connected||!value.file||busy||['written','verified','booted'].includes(phase)} onClick={()=>{onInvalidate();onChange(old=>({...old,progress:0,phase:'writing'}))}}>{phase==='interrupted'?'重新烧录':'开始烧录'}</button><button className="btn" disabled={phase!=='written'||!connected} onClick={()=>onChange(old=>({...old,phase:'verifying'}))}>校验固件</button><button className="btn" disabled={phase!=='verified'||!connected} onClick={()=>onChange(old=>({...old,phase:'booting'}))}>重新启动</button></div>
    <p className={`lab-message ${phase==='interrupted'?'error-text':''}`} role={phase==='interrupted'?'alert':'status'}>{status}</p>
    {phase==='booted'?<span className="boot-result">✓ 设备启动成功，可以进入最终测试。</span>:null}
    <details className="lab-log"><summary>查看演示日志</summary><ul><li>SWD：{connected?'已连接':'未连接'}</li><li>固件：{value.file||'尚未选择'}</li><li>擦除与写入：{progress}%</li><li>校验：{['verified','booting','booted'].includes(phase)?'通过':phase==='verifying'?'进行中':'等待'}</li><li>本地交互演示，不访问 USB 或真实芯片。</li></ul></details>
   </div>
  </div>
 </div>;
}
