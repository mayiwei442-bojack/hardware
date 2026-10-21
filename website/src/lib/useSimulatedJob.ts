'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
export function useSimulatedJob(){
 const [job,setJob]=useState<{label:string;token:number}|null>(null);const [progress,setProgress]=useState(0);const done=useRef<()=>void>(()=>{});
 const start=useCallback((label:string,onDone:()=>void)=>{done.current=onDone;setProgress(0);setJob({label,token:Date.now()})},[]);
 const cancel=useCallback(()=>{setJob(null);setProgress(0)},[]);
 useEffect(()=>{if(!job)return;let value=0;const timer=setInterval(()=>{value=Math.min(value+10,100);setProgress(value);if(value===100){clearInterval(timer);setJob(null);done.current()}},110);return()=>clearInterval(timer)},[job]);
 return {job,progress,start,cancel};
}
