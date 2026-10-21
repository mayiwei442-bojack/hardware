'use client';
import {useEffect,useState} from 'react';
import {sections} from '@/data/product';
export default function Navigation(){
 const [active,setActive]=useState('overview');const [open,setOpen]=useState(false);
 useEffect(()=>{const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting)setActive(e.target.id)},{rootMargin:'-15% 0px -60% 0px',threshold:0});sections.forEach(([id])=>{const el=document.getElementById(id);if(el)observer.observe(el)});return()=>observer.disconnect()},[]);
 useEffect(()=>{if(!open)return;const close=(e:KeyboardEvent)=>{if(e.key==='Escape')setOpen(false)};window.addEventListener('keydown',close);return()=>window.removeEventListener('keydown',close)},[open]);
 return <header className="site-header"><nav aria-label="主导航" className={open?'nav-links is-open':'nav-links'}>{sections.map(([id,n,label])=><a key={id} href={`#${id}`} aria-current={active===id?'location':undefined} onClick={()=>setOpen(false)}><span>{n}</span>{label}</a>)}</nav><span className="header-edition mono">版本 01</span><button className="mobile-menu" aria-expanded={open} aria-label={open?'收起导航':'展开导航'} onClick={()=>setOpen(!open)}>{open?'关闭 −':'目录 +'}</button></header>;
}
