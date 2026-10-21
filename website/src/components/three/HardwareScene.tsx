'use client';

import {Suspense,useEffect,useMemo,useRef} from 'react';
import {Canvas,useFrame,useThree,type ThreeEvent} from '@react-three/fiber';
import {Environment,Lightformer,OrbitControls,useGLTF} from '@react-three/drei';
import {AnimationMixer,Box3,MathUtils,Mesh,PerspectiveCamera,Vector3,type AnimationAction,type Material,type MeshStandardMaterial,type Object3D} from 'three';
import type {OrbitControls as OrbitControlsImpl} from 'three-stdlib';
import {clone} from 'three/addons/utils/SkeletonUtils.js';
import {hardwareParts,type HardwarePartId,type PartSelection} from '@/data/hardware';
import type {ConnectedSceneController} from '@/lib/three/controller';

type Props={controller:ConnectedSceneController;selected:PartSelection|null;onSelect:(selection:PartSelection)=>void;onLoaded:()=>void;onComplete:(complete:boolean)=>void;onFocusReady:(ready:boolean)=>void;reduced:boolean;active:boolean;attempt:number};
type Surface={mesh:Mesh;materials:{material:Material;opacity:number;transparent:boolean;depthWrite:boolean}[];group:Object3D};
const URL='/assets/keyboard-exploded.glb';
const direction=new Vector3(1.3,1.3,1.9).normalize();
const worldUp=new Vector3(0,1,0);
const right=new Vector3().crossVectors(worldUp,direction).normalize();
const up=new Vector3().crossVectors(direction,right).normalize();

// Fit every corner in the camera's view, including portrait screens.
function fitDistance(box:Box3,aspect:number,fov:number,fill:number){
 const center=box.getCenter(new Vector3());
 const tangent=Math.tan(MathUtils.degToRad(fov*.5));
 let distance=0;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
  const corner=new Vector3(x,y,z).sub(center);
  const depth=corner.dot(direction);
  distance=Math.max(distance,depth+Math.abs(corner.dot(right))/(tangent*aspect*fill),depth+Math.abs(corner.dot(up))/(tangent*fill));
 }
 return Math.max(.5,distance);
}

function Instrument({controller,selected,onSelect,onLoaded,onComplete,onFocusReady,reduced,active,attempt}:Props){
 const {scene,animations}=useGLTF(attempt?`${URL}?retry=${attempt}`:URL,'/draco/');
 const {camera,size,gl,invalidate}=useThree();
 const controls=useRef<OrbitControlsImpl>(null);
 const model=useMemo(()=>clone(scene),[scene]);
 const mixer=useMemo(()=>new AnimationMixer(model),[model]);
 const action=useRef<AnimationAction|null>(null);
 const progress=useRef(controller.getProgress());
 const completed=useRef(false);
 const bounds=useRef<{assembled:Box3;exploded:Box3}|null>(null);
 const selection=useRef<Object3D|null>(null);
 const isolated=useRef<Object3D|null>(null);
 const wasSelected=useRef(false);
 const fade=useRef(1);
 const viewShift=useRef(0);
 const move=useRef<{from:Vector3;target:Vector3;elapsed:number}|null>(null);
 const focus=useRef<{center:Vector3;box:Box3}|null>(null);
 const scratch=useMemo(()=>({center:new Vector3(),position:new Vector3()}),[]);
 const surfaces=useMemo(()=>{
  const result:Surface[]=[];
  model.traverse(node=>{
   if(!(node instanceof Mesh))return;
   let group:Object3D=node;
   while(group.parent&&group.parent!==model&&!group.userData.part)group=group.parent;
   const source=Array.isArray(node.material)?node.material:[node.material];
   const materials=source.map(original=>{
    const material=original.clone();
    // The original transmission is retained; a local studio environment lights it.
    if('envMapIntensity' in material)(material as MeshStandardMaterial).envMapIntensity=1.3;
    return {material,opacity:material.opacity,transparent:material.transparent,depthWrite:material.depthWrite};
   });
   node.material=Array.isArray(node.material)?materials.map(m=>m.material):materials[0].material;
   result.push({mesh:node,materials,group});
  });
  return result;
 },[model]);

 useEffect(()=>{
  const clip=animations.find(clip=>clip.name==='HardwareExplode');
  if(!clip)throw new Error('HardwareExplode animation is missing');
  const animation=mixer.clipAction(clip);
  animation.play();animation.paused=true;
  action.current=animation;
  animation.time=0;mixer.update(0);model.updateMatrixWorld(true);
  const assembled=new Box3().setFromObject(model);
  animation.time=clip.duration;mixer.update(0);model.updateMatrixWorld(true);
  const exploded=new Box3().setFromObject(model);
  bounds.current={assembled,exploded};
  animation.time=progress.current*clip.duration;mixer.update(0);
  onLoaded();invalidate();
  return()=>{mixer.stopAllAction();mixer.uncacheRoot(model);action.current=null;};
 },[animations,mixer,model,onLoaded,invalidate]);
 useEffect(()=>()=>{surfaces.forEach(surface=>surface.materials.forEach(m=>m.material.dispose()));},[surfaces]);
 useEffect(()=>{
  selection.current=selected?model.getObjectByName(selected.node)||null:null;
  onFocusReady(false);
  if(selection.current){
   isolated.current=selection.current;
   const animation=action.current;
   if(animation){animation.time=animation.getClip().duration;mixer.update(0);model.updateMatrixWorld(true);}
   const box=new Box3().setFromObject(selection.current);
   focus.current={box,center:box.getCenter(new Vector3())};
  }else focus.current=null;
  if(selected||wasSelected.current){
   move.current={from:camera.position.clone(),target:controls.current?.target.clone()||new Vector3(),elapsed:0};
   if(controls.current)controls.current.enabled=false;
  }
  wasSelected.current=!!selected;
  invalidate();
 },[selected,model,camera,mixer,onFocusReady,invalidate]);
 useEffect(()=>{gl.domElement.style.cursor=selected?'grab':'auto';return()=>{gl.domElement.style.cursor='auto';};},[selected,gl]);

 useFrame((_,delta)=>{
  if(!active||!action.current||!bounds.current||!controls.current)return;
  const orbit=controls.current;
  const targetProgress=controller.getProgress();
  progress.current=reduced?targetProgress:MathUtils.damp(progress.current,targetProgress,9,Math.min(delta,.25));
  if(Math.abs(progress.current-targetProgress)<.00015)progress.current=targetProgress;
  action.current.time=progress.current*action.current.getClip().duration;
  mixer.update(0);model.updateMatrixWorld(true);
  const done=progress.current>.999;
  if(done!==completed.current){completed.current=done;onComplete(done);}

  const isolate=selection.current;
  fade.current=reduced?(isolate?0:1):MathUtils.damp(fade.current,isolate?0:1,7,Math.min(delta,.25));
  for(const surface of surfaces){
   const keep=surface.group===isolated.current;
   surface.mesh.visible=keep||fade.current>.008;
   const multiplier=keep?1:fade.current;
   for(const original of surface.materials){
    const material=original.material;
    const transparent=multiplier<.995||original.transparent;
    if(material.transparent!==transparent){material.transparent=transparent;material.needsUpdate=true;}
    material.opacity=original.opacity*multiplier;
    material.depthWrite=multiplier<.995?false:original.depthWrite;
   }
  }

  const perspective=camera as PerspectiveCamera;
  const shiftTarget=isolate?1:0;
  viewShift.current=reduced?shiftTarget:MathUtils.damp(viewShift.current,shiftTarget,7,Math.min(delta,.25));
  const mobile=size.width<760;
  const verticalShift=mobile?MathUtils.lerp(progress.current*.065,.14,viewShift.current):0;
  if(viewShift.current>.001||verticalShift>.001){
   perspective.setViewOffset(size.width,size.height,mobile?0:size.width*.08*viewShift.current,size.height*verticalShift,size.width,size.height);
  }else if(perspective.view?.enabled)perspective.clearViewOffset();

  const {assembled,exploded}=bounds.current;
  const center=scratch.center;
  center.copy(assembled.getCenter(scratch.position)).lerp(exploded.getCenter(new Vector3()),progress.current);
  const assembledDistance=fitDistance(assembled,size.width/size.height,perspective.fov,.79);
  const explodedDistance=fitDistance(exploded,size.width/size.height,perspective.fov,size.width<760?.78:.81);
  let distance=MathUtils.lerp(assembledDistance,explodedDistance,progress.current);
  if(focus.current){center.copy(focus.current.center);distance=fitDistance(focus.current.box,size.width/size.height,perspective.fov,size.width<760?.58:.62);}
  const position=scratch.position.copy(direction).multiplyScalar(distance).add(center);
  if(move.current){
   const transition=move.current;
   transition.elapsed+=delta;
   const time=reduced?1:Math.min(1,transition.elapsed/.95);
   const eased=time*time*time*(time*(time*6-15)+10);
   camera.position.lerpVectors(transition.from,position,eased);
   orbit.target.lerpVectors(transition.target,center,eased);
   orbit.update();
   if(time===1){move.current=null;orbit.enabled=!!isolate;onFocusReady(!!isolate);}
  }else if(!isolate){
   camera.position.copy(position);orbit.target.copy(center);orbit.update();
  }else orbit.enabled=true;
 });

 const hit=(event:ThreeEvent<MouseEvent>)=>{
  if(selected||!completed.current||event.delta>5)return;
  let node:Object3D|null=event.object;
  while(node&&!node.userData.part)node=node.parent;
  const part=node?.userData.part as HardwarePartId|undefined;
  if(node&&part&&hardwareParts[part]){event.stopPropagation();onSelect({part,node:node.name});}
 };

 return <>
  <primitive object={model} dispose={null} onClick={hit} onPointerOver={()=>{if(completed.current&&!selected)gl.domElement.style.cursor='pointer';}} onPointerOut={()=>{gl.domElement.style.cursor=selected?'grab':'auto';}}/>
  <OrbitControls ref={controls} makeDefault enablePan={false} enableZoom={false} enableDamping dampingFactor={.09} rotateSpeed={.7} enabled={false}/>
 </>;
}

export default function HardwareScene(props:Props){
 return <Canvas camera={{position:[4,4,6],fov:36,near:.01,far:100}} dpr={[1,1.5]} frameloop={props.active?'always':'demand'} gl={{antialias:true,alpha:true,powerPreference:'high-performance'}}>
  <ambientLight intensity={.4}/><directionalLight position={[3,6,5]} intensity={2.4} color="#edf7e5"/><directionalLight position={[-5,2,-3]} intensity={1.2} color="#beb2ff"/>
  <Suspense fallback={null}>
   <Environment resolution={128}>
    <Lightformer intensity={1.8} color="#f4ffea" position={[0,5,-3]} rotation={[Math.PI/2,0,0]} scale={[8,6,1]}/>
    <Lightformer intensity={1.2} color="#e9e7ff" position={[-4,1,1]} rotation={[0,Math.PI/2,0]} scale={[4,7,1]}/>
    <Lightformer intensity={1.5} color="#f4fff0" position={[4,3,4]} rotation={[0,-Math.PI/3,0]} scale={[3,7,1]}/>
   </Environment>
   <Instrument {...props}/>
  </Suspense>
 </Canvas>;
}
