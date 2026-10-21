export type ModelId = 'keyboard'|'keyboardExploded'|'computer'|'printer'|'smtMachine'|'pcb';
export type ModelAsset = { kind:'model'; status:'pending'|'ready'; src:string|null; filename:string; camera:{position:[number,number,number]; target:[number,number,number]; fov:number}; scale:number; lighting:{ambient:number; key:number; color:string}; clips?:{assembly?:string; demo?:string}; materials?:Record<string,{color?:string;roughness?:number;metalness?:number}>; nodeInputs?:Record<string,string|{type:'key';keyId:string}|{type:'encoder';delta:number}|{type:'joystick';x:number;y:number}|{type:'touch';action:'tap'|'left'|'right'}> };
const model = (filename:string):ModelAsset => ({kind:'model',status:'pending',src:null,filename,camera:{position:[0,2,4],target:[0,0,0],fov:36},scale:1,lighting:{ambient:.7,key:3,color:'#f0f1ec'}});
const exploded:ModelAsset={...model('keyboard-exploded.glb'),status:'ready',src:'/assets/keyboard-exploded.glb',clips:{assembly:'HardwareExplode'}};
// A file path alone never starts a scene: set status to ready after supplying a real asset.
export const assets = {
 overviewImage:{src:'/assets/acid-alloy-keyboard-cutout.png',alt:'酸性合金键盘：酸绿面板、深色键帽与紫色摇杆',width:1330,height:1182},
 models:{keyboard:model('keyboard.glb'),keyboardExploded:exploded,computer:model('computer.glb'),printer:model('printer.glb'),smtMachine:model('smt-machine.glb'),pcb:model('pcb.glb')} satisfies Record<ModelId,ModelAsset>,
 productImages:{status:'pending' as 'pending'|'ready',items:[] as {src:string;alt:string;width:number;height:number}[]},
 keycapTextures:{status:'pending' as 'pending'|'ready',items:{} as Record<string,string>},
};
