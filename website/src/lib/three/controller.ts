export type TouchAction = 'tap'|'left'|'right';
export interface InputController {
 onKeyPress:(keyId:string)=>void;
 onEncoderRotate:(delta:number)=>void;
 onEncoderPress?:()=>void;
 onJoystickMove:(x:number,y:number)=>void;
 onTouchPadAction:(action:TouchAction)=>void;
}
export interface SceneController { setProgress:(progress:number)=>void; resetAssembly:()=>void; playClip:(name:string)=>void; stop:()=>void; }
export function createSceneController():SceneController & {subscribe:(fn:(progress:number)=>void)=>()=>void;getProgress:()=>number;subscribeClip:(fn:(name:string|null)=>void)=>()=>void} {
 let progress=0; const listeners=new Set<(p:number)=>void>();const clips=new Set<(n:string|null)=>void>();
 const setProgress=(value:number)=>{progress=Math.max(0,Math.min(1,value));listeners.forEach(fn=>fn(progress));};
 return {setProgress,resetAssembly:()=>setProgress(0),getProgress:()=>progress,subscribe:fn=>{listeners.add(fn);return()=>{listeners.delete(fn)};},subscribeClip:fn=>{clips.add(fn);return()=>{clips.delete(fn)};},playClip:name=>clips.forEach(fn=>fn(name)),stop:()=>clips.forEach(fn=>fn(null))};
}
export type ConnectedSceneController=ReturnType<typeof createSceneController>;
