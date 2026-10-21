'use client';
import {Suspense,useEffect,useMemo,useRef} from 'react';
import {Canvas,useFrame} from '@react-three/fiber';
import {OrbitControls,useGLTF} from '@react-three/drei';
import {AnimationMixer,Mesh,MeshStandardMaterial} from 'three';
import {clone} from 'three/addons/utils/SkeletonUtils.js';
import type {ModelAsset} from '@/data/assets';
import {assets} from '@/data/assets';
import type {ConnectedSceneController,InputController} from '@/lib/three/controller';
import AssetPlaceholder from '../placeholders/AssetPlaceholder';
type Props={asset:ModelAsset;controller?:ConnectedSceneController;inputs?:InputController;onLoaded:()=>void};
function LoadedModel({asset,controller,inputs,onLoaded}:Props){
 const {scene,animations}=useGLTF(asset.src!);const object=useMemo(()=>clone(scene),[scene]);
 const mixer=useMemo(()=>new AnimationMixer(object),[object]);const manual=useRef(false);
 useEffect(()=>{onLoaded();return()=>{mixer.stopAllAction();mixer.uncacheRoot(object)};},[mixer,object,onLoaded]);
 useEffect(()=>{
  if(!controller)return;
  const animation=animations.find(a=>a.name===asset.clips?.assembly);
  const sync=(progress:number)=>{if(animation){const action=mixer.clipAction(animation);action.play();action.paused=true;action.time=progress*animation.duration;mixer.update(0);manual.current=true;}};
  sync(controller.getProgress());const off=controller.subscribe(sync);
  const offClip=controller.subscribeClip(name=>{mixer.stopAllAction();manual.current=false;const clip=animations.find(a=>a.name===name);if(clip)mixer.clipAction(clip).reset().play();});
  return()=>{off();offClip()};
 },[controller,mixer,animations,asset.clips]);
 useEffect(()=>{
  // Optional textures are mapped to existing material names; no geometry is generated.
  if(assets.keycapTextures.status!=='ready'&&!asset.materials)return;
  let alive=true;const disposables:MeshStandardMaterial[]=[];
  import('three').then(({TextureLoader,SRGBColorSpace})=>{
   if(!alive)return;const loader=new TextureLoader();object.traverse(node=>{
    if(!(node instanceof Mesh))return;
    const materials=Array.isArray(node.material)?node.material:[node.material];
    node.material=materials.map(original=>{const url=assets.keycapTextures.status==='ready'?assets.keycapTextures.items[original.name]:undefined;const style=asset.materials?.[original.name];if(!url&&!style)return original;
     const mat=original.clone() as MeshStandardMaterial;disposables.push(mat);if(style?.color)mat.color.set(style.color);if(style?.roughness!==undefined)mat.roughness=style.roughness;if(style?.metalness!==undefined)mat.metalness=style.metalness;
     if(url)loader.load(url,texture=>{if(!alive){texture.dispose();return;}texture.colorSpace=SRGBColorSpace;texture.flipY=false;mat.map=texture;mat.needsUpdate=true;},undefined,()=>{});return mat;
    });
   });
  });
  return()=>{alive=false;disposables.forEach(m=>{if(assets.keycapTextures.items[m.name])m.map?.dispose();m.dispose()})};
 },[object,asset.materials]);
 useFrame((_,delta)=>{if(!manual.current)mixer.update(delta)});
 return <primitive object={object} scale={asset.scale} onClick={(event:{stopPropagation:()=>void;object:{name:string}})=>{const id=asset.nodeInputs?.[event.object.name];if(id&&inputs){event.stopPropagation();if(typeof id==='string')inputs.onKeyPress(id);else if(id.type==='key')inputs.onKeyPress(id.keyId);else if(id.type==='encoder')inputs.onEncoderRotate(id.delta);else if(id.type==='joystick')inputs.onJoystickMove(id.x,id.y);else inputs.onTouchPadAction(id.action)}}}/>;
}
export default function ModelScene(props:Props){
 const {asset}=props;
 return <Suspense fallback={<AssetPlaceholder label="三维模型" status="正在加载"/>}><Canvas camera={{position:asset.camera.position,fov:asset.camera.fov}} dpr={[1,1.5]}>
  <ambientLight intensity={asset.lighting.ambient}/><directionalLight position={[3,5,4]} intensity={asset.lighting.key} color={asset.lighting.color}/>
  <LoadedModel {...props}/><OrbitControls target={asset.camera.target} enablePan={false}/>
 </Canvas></Suspense>;
}
