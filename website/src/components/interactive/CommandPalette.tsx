'use client';
import {useEffect,useRef,useState} from 'react';
export default function CommandPalette({onClose,onCommand}:{onClose:()=>void;onCommand:(s:string)=>void}){
 const dialog=useRef<HTMLDialogElement>(null);const [query,setQuery]=useState('');
 useEffect(()=>{const previous=document.activeElement as HTMLElement;dialog.current?.showModal();dialog.current?.querySelector<HTMLInputElement>('input')?.focus();return()=>{previous?.focus()}},[]);
 const commands=[['format','整理代码空白'],['new','新建会话笔记'],['terminal','切换终端']];
 return <dialog ref={dialog} className="command-dialog" aria-label="命令面板" onCancel={e=>{e.preventDefault();onClose()}} onClick={e=>{if(e.target===e.currentTarget)onClose()}}><div className="between mono"><span>命令面板</span><button onClick={onClose} aria-label="关闭命令面板">关闭 ×</button></div><input autoFocus aria-label="搜索命令" placeholder="输入命令…" value={query} onChange={e=>setQuery(e.target.value)}/><div className="command-list">{commands.filter(([,name])=>name.includes(query)).map(([id,name])=><button key={id} onClick={()=>onCommand(id)}>{name}<span>↵</span></button>)}{commands.every(([,name])=>!name.includes(query))?<p>未找到命令</p>:null}</div></dialog>;
}
