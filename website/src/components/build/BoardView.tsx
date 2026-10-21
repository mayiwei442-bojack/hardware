'use client';
import type {ReactNode} from 'react';
import {boardParts,smdParts} from '@/data/build';

export default function BoardView({side='T',color='purple',children,rotation=0,lit=false,rotations}:{side?:string;color?:string;children?:ReactNode;rotation?:number;lit?:boolean;rotations?:Record<string,number>}){
 const fill=({green:'#234a38',purple:'#47325c',black:'#242a2b',blue:'#263f66',white:'#69766d'} as Record<string,string>)[color]||'#47325c';
 return <div className={`lab-board-stage ${lit?'board-lit':''}`}>
  <div key={side} className="lab-board" style={{transform:`rotate(${rotation}deg)`}}>
   <svg viewBox="0 0 95 95" aria-hidden="true" className="board-drawing">
    <rect x=".6" y=".6" width="93.8" height="93.8" rx="3" fill={fill} stroke="#b8c8a7" strokeWidth=".4"/>
    <rect x="2" y="2" width="91" height="91" rx="2" fill="none" stroke="#b8c8a7" strokeOpacity=".3" strokeWidth=".2"/>
    {boardParts.filter(p=>p.id.startsWith('H')).map(p=><g key={p.id}><circle cx={p.x} cy={p.y} r="2.2" fill="#b7a775"/><circle cx={p.x} cy={p.y} r="1.1" fill="#0b0e0d"/></g>)}
    {boardParts.filter(p=>p.id.startsWith('SW')&&p.id!=='SW1').map((p,i)=><g key={p.id} stroke="#afc98d" strokeWidth=".25" opacity=".32" fill="none"><path d={`M${p.x} ${p.y}v${5+i%3}H7V71h2`}/><circle cx={p.x} cy={p.y+7} r=".7"/></g>)}
    {smdParts.filter(p=>p.side===side).map(p=><g key={p.id} data-part={p.id} data-rotation={(p.rotation+(rotations?.[p.id]||0))%360} transform={`translate(${p.x} ${p.y}) rotate(${-p.rotation-(rotations?.[p.id]||0)})`}>
     <rect x={p.id==='U3'?-4:-1.25} y={p.id==='U3'?-4:-.8} width={p.id==='U3'?8:2.5} height={p.id==='U3'?8:1.6} rx=".3" fill={p.id.startsWith('LED')&&lit?'#c6ff36':'#111a18'} stroke="#c1c7b1" strokeWidth=".2"/>
     <circle cx={p.id==='U3'?-2.6:-.7} cy={p.id==='U3'?-2.6:0} r=".35" fill="#c6ff36"/>
    </g>)}
    <rect x="42" y=".6" width="11" height="4" rx="1" fill="#bec4c4"/>
    <rect x="43" y="88" width="9" height="5" rx=".5" fill="#151c19" stroke="#c6ff36" strokeWidth=".3"/>
    {[0,1,2,3,4,5].map(i=><circle key={i} cx={45+i%3*2.5} cy={89.5+Math.floor(i/3)*2} r=".45" fill="#dbbe71"/>)}
    {side==='T'?<circle cx="18.975" cy="76.025" r="5" fill="#b9a572" stroke="#f0e5b5" strokeWidth=".2"/>:null}
    <text x="47.5" y="86" fill="#d8e2d1" fontSize="2" textAnchor="middle">ACID ALLOY / {side==='T'?'TOP':'BOTTOM'}</text>
   </svg>
   {children}
  </div>
  <span className="board-dimension mono">95 × 95 mm · {side==='T'?'正面':'背面'}</span>
 </div>;
}

export function LabSteps({items,current}:{items:string[];current:number}){
 return <ol className="lab-substeps" aria-label="当前环节进度" tabIndex={0}>{items.map((item,i)=><li key={item} aria-current={i===current?'step':undefined} className={i<current?'done':''}><span>{i<current?'✓':i+1}</span>{item}</li>)}</ol>;
}
