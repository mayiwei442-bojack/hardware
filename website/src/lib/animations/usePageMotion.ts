'use client';
import {useEffect} from 'react';
import gsap from 'gsap';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
import type {ConnectedSceneController} from '../three/controller';
export function bindSceneScroll(element:Element,controller:ConnectedSceneController,enabled:boolean){
 if(!enabled)return()=>{};
 gsap.registerPlugin(ScrollTrigger);
 const trigger=ScrollTrigger.create({trigger:element,start:'top center',end:'bottom center',onUpdate:self=>controller.setProgress(self.progress)});
 return()=>trigger.kill();
}
export function usePageMotion(){useEffect(()=>{
 gsap.registerPlugin(ScrollTrigger);const media=gsap.matchMedia();
 media.add('(prefers-reduced-motion: no-preference)',()=>{
  gsap.utils.toArray<HTMLElement>('[data-reveal]').forEach(el=>gsap.from(el,{y:36,opacity:0,duration:.8,ease:'power3.out',scrollTrigger:{trigger:el,start:'top 92%',toggleActions:'play none none reverse'}}));
  gsap.utils.toArray<SVGPathElement>('.signal-path').forEach(path=>{const length=path.getTotalLength();gsap.fromTo(path,{strokeDasharray:length,strokeDashoffset:length},{strokeDashoffset:0,scrollTrigger:{trigger:path,start:'top 90%',end:'bottom 40%',scrub:1}})});
  gsap.utils.toArray<HTMLElement>('[data-count]').forEach(el=>{const value={n:0};gsap.to(value,{n:Number(el.dataset.count),duration:1.2,roundProps:'n',onUpdate:()=>{el.textContent=String(value.n)},scrollTrigger:{trigger:el,start:'top 90%',once:true}})});

 });
 return()=>media.revert();
},[])}
