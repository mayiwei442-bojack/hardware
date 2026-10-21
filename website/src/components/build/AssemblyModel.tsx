'use client';
import {Component,Suspense,useEffect,useMemo,useState,type ReactNode} from 'react';
import {Canvas} from '@react-three/fiber';
import {Bounds,OrbitControls,useGLTF} from '@react-three/drei';
import {clone} from 'three/addons/utils/SkeletonUtils.js';

function Model({installed,onReady}:{installed:string[];onReady:()=>void}){
 const {scene}=useGLTF('/assets/keyboard-exploded.glb','/draco/');
 const model=useMemo(()=>clone(scene),[scene]);
 useEffect(()=>{model.traverse(node=>{const part=node.userData.part;if(!part)return;node.visible=['pcb','touch','lighting'].includes(part)||(part==='switches'&&installed.includes(node.name.replace('switch_','')))||(part==='encoder'&&installed.includes('SW1'))||(part==='joystick'&&installed.includes('J1'));});onReady();},[model,installed,onReady]);
 return <Bounds fit clip observe margin={1.25}><primitive object={model} dispose={null}/></Bounds>;
}
class ModelBoundary extends Component<{children:ReactNode},{error:boolean}>{state={error:false};static getDerivedStateFromError(){return {error:true}}render(){return this.state.error?<p className="lab-hint">三维预览暂不可用，请使用安装视图继续操作。</p>:this.props.children}}
export default function AssemblyModel({installed}:{installed:string[]}){
 const [ready,setReady]=useState(false);
 return <div className="assembly-scene" data-loaded={ready}><ModelBoundary><Canvas camera={{position:[4,5,6],fov:38}} dpr={[1,1.5]}><ambientLight intensity={1.8}/><directionalLight position={[4,8,5]} intensity={3}/><Suspense fallback={null}><Model installed={installed} onReady={()=>setReady(true)}/></Suspense><OrbitControls makeDefault enablePan={false}/></Canvas></ModelBoundary></div>;
}
