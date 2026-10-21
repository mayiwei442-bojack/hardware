'use client';
import dynamic from 'next/dynamic';
import {Component,useCallback,useState,type ReactNode} from 'react';
import {assets,type ModelId} from '@/data/assets';
import type {ConnectedSceneController,InputController} from '@/lib/three/controller';
import AssetPlaceholder from '../placeholders/AssetPlaceholder';
const ModelScene=dynamic(()=>import('./ModelScene'),{ssr:false,loading:()=> <AssetPlaceholder label="三维模型" status="正在加载"/>});
class AssetBoundary extends Component<{children:ReactNode;retry:()=>void},{error:boolean}>{
 state={error:false};static getDerivedStateFromError(){return {error:true}}
 render(){return this.state.error?<div className="asset-error"><AssetPlaceholder status="加载失败"/><button className="btn small" onClick={this.props.retry}>重新加载</button></div>:this.props.children;}
}
export default function ModelSlot({id,controller,inputs,compact=false}:{id:ModelId;controller?:ConnectedSceneController;inputs?:InputController;compact?:boolean}){
 const asset=assets.models[id];const [attempt,setAttempt]=useState(0);const [loaded,setLoaded]=useState(false);const onLoaded=useCallback(()=>setLoaded(true),[]);
 // This gate prevents mounting Canvas, loading Three or requesting a model while pending.
 if(asset.status!=='ready'||!asset.src)return <AssetPlaceholder code={id==='keyboard'?'AA–013':({keyboard:'键盘',keyboardExploded:'键盘拆解视图',computer:'电脑',printer:'打印机',smtMachine:'SMT 贴片机',pcb:'PCB'}[id])} compact={compact}/>;
 return <div className="model-slot" data-loaded={loaded}><AssetBoundary key={attempt} retry={()=>setAttempt(v=>v+1)}><ModelScene asset={asset} controller={controller} inputs={inputs} onLoaded={onLoaded}/></AssetBoundary></div>;
}
