'use client';
import {useRef,useState} from 'react';
export default function FilePicker({label,kind,value,onChange,preset,presetBytes}:{label:string;kind:'zip'|'bom'|'smt'|'hex';value:string;onChange:(name:string,bytes?:number)=>void;preset:string;presetBytes?:number}){
 const ref=useRef<HTMLInputElement>(null);const [error,setError]=useState('');const [drag,setDrag]=useState(false);const [reading,setReading]=useState(false);const request=useRef(0);
 async function select(file:File|undefined){if(!file)return;const sequence=++request.current;setError('');setReading(true);try{
  const ext=kind==='bom'||kind==='smt'?'csv':kind;
  if(!file.name.toLowerCase().endsWith(`.${ext}`))throw new Error(`请选择 .${ext} 文件`);
  if(file.size===0||file.size>30*1024*1024)throw new Error('文件需非空且小于 30 MB');
  if(kind==='zip'){const bytes=new Uint8Array(await file.slice(0,4).arrayBuffer());if(bytes[0]!==80||bytes[1]!==75)throw new Error('文件不是有效的 ZIP 格式');}
  else{const text=await file.slice(0,8192).text();if(kind==='hex'&&!/^:[0-9a-f]+/im.test(text))throw new Error('文件不是 Intel HEX 格式');if(kind==='bom'&&!/designator|reference/i.test(text))throw new Error('BOM 缺少 Designator / Reference 列');if(kind==='smt'&&!/designator|reference/i.test(text)||kind==='smt'&&!/rotation|mid x|posx/i.test(text))throw new Error('坐标文件缺少位号或位置字段');}
  if(sequence===request.current)onChange(file.name,file.size);
 }catch(e){if(sequence===request.current){setError((e as Error).message);onChange('')}}finally{if(sequence===request.current)setReading(false);if(ref.current)ref.current.value='';}}
 return <div className={`file-picker ${drag?'dragging':''}`} onDragOver={e=>{e.preventDefault();setDrag(true)}} onDragLeave={()=>setDrag(false)} onDrop={e=>{e.preventDefault();setDrag(false);void select(e.dataTransfer.files[0])}}><label className="mono">{label}</label><input ref={ref} className="sr-only" tabIndex={-1} type="file" accept={kind==='zip'?'.zip':kind==='hex'?'.hex':'.csv'} aria-label={`选择${label}`} onChange={e=>void select(e.target.files?.[0])}/><div className="file-name"><span aria-hidden="true">{value?'✓':'↥'}</span><span>{reading?'正在检查…':value||'拖入文件，或选择预设'}</span></div><div className="file-actions"><button className="text-button" disabled={reading} onClick={()=>ref.current?.click()}>选择文件</button><button className="text-button" disabled={reading} onClick={()=>{request.current++;setError('');onChange(preset,presetBytes)}}>使用预设</button>{value?<button className="text-button muted" onClick={()=>{request.current++;onChange('')}}>清除</button>:null}</div>{error?<p role="alert" className="error-text">{error}</p>:null}</div>;
}
