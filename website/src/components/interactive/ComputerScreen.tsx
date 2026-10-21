'use client';

import {useEffect,useRef,useState,type Dispatch} from 'react';
import {motion,useReducedMotion} from 'motion/react';
import {codexKeys,demoSessions,shortcutApps,shortcutExamples} from '@/data/trial';
import type {Mode,WorkstationAction,WorkstationState} from '@/lib/input';

export type ScreenView='ready'|'encoder'|'joystick'|'touch'|Mode|`K${string}`;
type Props={state:WorkstationState;dispatch:Dispatch<WorkstationAction>;view:ScreenView;onKey:(id:string)=>void;onView:(view:ScreenView)=>void;onMode:(mode:Mode)=>void;onReset:()=>void;vector:{x:number;y:number}};
type StateProps=Pick<Props,'state'|'dispatch'>;

function KeyChord({value}:{value:string}){
 return <span className="key-chord" aria-label={value}>{value.split(' + ').map((key,index)=><kbd key={index}>{key}</kbd>)}</span>;
}

function Commands({state,onKey,onClose}:Pick<Props,'state'|'onKey'>&{onClose:()=>void}){
 const [search,setSearch]=useState('');const input=useRef<HTMLInputElement>(null);
 useEffect(()=>{const previous=document.activeElement;input.current?.focus();return()=>{if(previous instanceof HTMLElement&&previous.isConnected)previous.focus()}},[]);
 const commands=codexKeys.filter(key=>['K02','K10','K12','K13'].includes(key.id)&&key.action.includes(search));
 return <div className="screen-commands" role="region" aria-label="Codex 命令菜单示例" onKeyDown={event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();onClose()}}}>
  <label className="sr-only" htmlFor="try-command-search">搜索命令</label><input ref={input} id="try-command-search" value={search} onChange={event=>setSearch(event.target.value)} placeholder="搜索原项目支持的操作…"/>
  <div>{commands.map(key=><button key={key.id} onClick={()=>onKey(key.id)}><span>{key.action}</span><KeyChord value={key[state.platform]}/></button>)}</div>
  {commands.length===0?<p>未找到命令</p>:null}<p>Codex 命令入口示意 · Escape 返回会话。</p>
 </div>;
}

function ChatPreview({state,onKey}:Pick<Props,'state'|'onKey'>){
 const session=demoSessions[state.session];
 return <div className="codex-chat-preview">
  <div className="preview-topline"><span>Codex / 示例会话</span><span>{state.newChat?'新会话':'0'+(state.session+1)}</span></div>
  <h4>{state.newChat?'开始新的会话':session.name}</h4>
  <p>{state.newChat?'输入新的问题，开始下一项工作。':session.message}</p>
  {!state.newChat&&state.session===0?<div className={'demo-request '+state.request}>
   <span>示例请求</span><p>查看制造资料，继续检查装配。</p>
   {state.request==='pending'?<div><button onClick={()=>onKey('K08')}>Enter · 确认</button><button onClick={()=>onKey('K09')}>Esc · 拒绝</button></div>:<strong>{state.request==='approved'?'示例请求已确认':'示例请求已拒绝'}</strong>}
  </div>:null}
  <div className="chat-composer-placeholder">{state.newChat?'在 Codex 中输入消息…':'继续当前对话…'}<span aria-hidden="true">↵</span></div>
 </div>;
}

function CodexDemo({state,view,onKey,onView}:Pick<Props,'state'|'view'|'onKey'|'onView'>){
 const key=codexKeys.find(item=>item.id===view);
 return <div className="codex-demo">
  {key?<div className="binding-card"><div className="preview-topline"><span>目标软件 / Codex</span><span>{key.id}</span></div><KeyChord value={key[state.platform]}/><p>{key.description}</p></div>:null}
  {view==='K07'?<Commands state={state} onKey={onKey} onClose={()=>onView('CODEX')}/>
   :view==='K01'?<div className="session-examples">{demoSessions.map((session,index)=><button key={session.name} aria-pressed={!state.newChat&&state.session===index} onClick={()=>onKey('K0'+(index+3))}><span className="mono">0{index+1}</span><span>{session.name}<small>{index===0?(state.request==='pending'?'等待你的确认':'请求已处理'):session.detail}</small></span><span>↗</span></button>)}</div>
   :view==='K08'||view==='K09'?<ChatPreview state={{...state,session:0,newChat:false}} onKey={onKey}/>
   :view==='K10'?<div className="feature-preview"><span className="feature-symbol" aria-hidden="true">&gt;_</span><h4>{state.terminalOpen?'终端面板已展开 · 示例':'终端面板已收起 · 示例'}</h4><p>在 Codex 会话中查看终端。再次按下终端键即可切换显示。</p><span className="screen-help">此处展示面板操作，不运行终端命令。</span></div>
   :view==='K11'?<div className="feature-preview"><span className="feature-symbol" aria-hidden="true">◎</span><h4>用语音输入下一条消息</h4><p>在 Codex 中打开听写入口 → 说出需求 → 检查输入文字。</p><span className="screen-help">此处展示快捷键用途，不调用麦克风或生成转写结果。</span></div>
   :view==='K12'?<div className="side-conversation-preview"><div><small>当前会话 · 示例</small><h4>检查键盘装配</h4><p>保留手头正在处理的上下文。</p></div>{state.sideOpen?<div><small>侧边会话 · 示例</small><h4>追问一个细节</h4><p>同时查看另一段对话。</p></div>:<p className="screen-help">侧边会话已收起。再次按 K12 展开示例。</p>}</div>
   :view==='K13'?<div className="feature-preview"><span className="feature-symbol" aria-hidden="true">⌘</span><h4>在 Codex 中选择模型</h4><p>按下模型键打开选择器，再在目标应用中完成选择。</p><span className="screen-help">可用模型与选项以 Codex 当前界面为准。</span></div>
   :<ChatPreview state={state} onKey={onKey}/>}
 </div>;
}

function MediaDemo({state,dispatch}:StateProps){
 const lesson=state.mediaScene==='lesson';
 return <div className="media-demo" data-scene={state.mediaScene} data-playing={state.playing}>
  <div className="scene-picker" role="group" aria-label="触摸板使用场景">
   <button aria-pressed={!lesson} onClick={()=>dispatch({type:'scene',scene:'music'})}>工作时听音乐</button>
   <button aria-pressed={lesson} onClick={()=>dispatch({type:'scene',scene:'lesson'})}>跟着教程操作</button>
  </div>
  <div className="media-story"><small>{lesson?'场景 02 / 边看边做':'场景 01 / 专注工作'}</small><h4>{lesson?'暂停这一帧，动手跟着做。':'临时回个话，音乐一触即停。'}</h4><p>{lesson?'看教程时，轻触暂停，留住当前步骤；操作完成后再轻触继续。':'写代码或整理资料时，轻触暂停背景音乐；处理完事情，再轻触继续。'}</p></div>
  <div className={'media-player-example '+(lesson?'lesson-player':'music-player')}>
   <div className="player-context"><span>{lesson?'教程播放器':'音乐播放器'} / 本页示例</span><span className={state.playing?'playback-on':''}>{state.playing?'播放中':'已暂停'}</span></div>
   {lesson?<div className="lesson-frame"><div className="lesson-step"><span className="mono">STEP 02</span><strong>调整视图，检查装配</strong><span>教程画面示意</span></div><div className="lesson-play-symbol" aria-hidden="true">{state.playing?'Ⅱ':'▶'}</div></div>
    :<div className="music-track"><div className={'album-disc '+(state.playing?'spinning':'')} aria-hidden="true"><i/></div><div><span className="mono">FOCUS / 01</span><h5>工作歌单</h5><p>{state.playing?'背景音乐播放状态示例':'已暂停，可以先处理手边的事'}</p></div></div>}
   <div className="player-controls"><button className="media-play-button" aria-label={state.playing?'暂停示例媒体':'播放示例媒体'} onClick={()=>dispatch({type:'play'})}>{state.playing?'Ⅱ 暂停':'▶ 继续'}</button><span className="media-playback-label" aria-live="polite">{lesson?(state.playing?'继续看下一步':'已暂停，照着当前步骤操作'):(state.playing?'继续专注手头工作':'暂时停下，稍后继续')}</span></div>
  </div>
  <div className="touch-action-flow"><span>轻触左侧触摸板</span><b aria-hidden="true">→</b><span>播放 / 暂停</span><b aria-hidden="true">→</b><strong>{state.playing?'再触可暂停':'再触可继续'}</strong></div>
  <div className="media-volume"><span>旋钮控制音量</span><output aria-label="演示音量">{state.muted?'静音':state.volume+'%'}</output><button aria-pressed={state.muted} onClick={()=>dispatch({type:'mute'})}>{state.muted?'取消静音':'按压静音'}</button></div>
  <p className="screen-help media-boundary">单区轻触，默认发送播放／暂停媒体键；由支持媒体键的当前播放器响应。本页只演示状态，不播放音视频。</p>
 </div>;
}

function Shortcuts({state,dispatch}:StateProps){
 const examples=shortcutExamples.filter(example=>example.app===state.shortcutApp);
 const active=examples.find(example=>example.id===state.lastShortcut);
 return <div className="shortcut-demo">
  <div className="shortcut-targets" role="group" aria-label="选择目标软件示例">{shortcutApps.map(app=><button key={app.id} aria-pressed={state.shortcutApp===app.id} onClick={()=>dispatch({type:'shortcut-app',app:app.id})}><span aria-hidden="true">{app.icon}</span>{app.name}</button>)}</div>
  <p className="shortcut-context">目标软件需在前台：<strong>{examples[0].target}</strong></p>
  <div className="shortcut-examples">{examples.map(example=><button key={example.id} aria-pressed={active?.id===example.id} onClick={()=>dispatch({type:'shortcut',id:example.id})}><span>{example.action}</span><KeyChord value={example[state.platform]}/><small>点击查看按键反馈 ↗</small></button>)}</div>
  <div className="shortcut-feedback" role="status">{active?<><span>本页按键反馈</span><KeyChord value={active[state.platform]}/><h4>{active.target} · {active.action}</h4><p>{active.result}</p></>:<><span>一颗按键，一组快捷键。</span><h4>先选软件，再试一个操作。</h4><p>在配套软件中，将设备按键绑定到上面的组合键。</p></>}</div>
  <p className="screen-help">这些示例来自原项目预设。本页展示按键用途，不启动或控制已安装的应用；实际效果取决于目标软件的焦点和快捷键设置。</p>
 </div>;
}

function NavigationDemo({state,vector}:Pick<Props,'state'|'vector'>){
 return <div className="navigation-demo"><div className="navigation-intro"><KeyChord value="↑ + ↓ + ← + →"/><p>默认映射为方向键，用于在列表或选项之间导航。</p></div><ol className="navigation-grid" aria-label="方向键导航示例">{Array.from({length:9},(_,index)=>{const selected=Math.floor(index/3)===state.navigation.row&&index%3===state.navigation.col;return <li key={index} aria-current={selected?'true':undefined} className={selected?'selected':''}><span className="mono">0{index+1}</span><span>{selected?'当前选中':'选项'}</span></li>})}</ol><p className="screen-help">最近输入：{vector.x<0?'←':vector.x>0?'→':''}{vector.y<0?'↑':vector.y>0?'↓':''} · 拨动左侧摇杆，观察选中项移动。</p></div>;
}

export default function ComputerScreen({state,dispatch,view,onKey,onView,onMode,onReset,vector}:Props){
 const reduced=useReducedMotion();const key=codexKeys.find(item=>item.id===view);
 const title=key?.action??({ready:'从一个真实的输入开始',CODEX:'Codex 会话示例',MEDIA:'媒体控制',SHORTCUTS:'应用快捷键',encoder:'旋钮 · 音量与静音',touch:'触摸板 · 播放与暂停',joystick:'摇杆 · 方向键导航'}[view as Exclude<ScreenView,`K${string}`>]);
 return <div className="try-computer-column">
  <div className="computer-bezel"><div className="computer-screen" role="region" aria-label="电脑显示屏" data-screen={view}>
   <div className="screen-system-bar"><span><i/>AA / 桌面工作台</span><span className="mono">网页演示</span></div>
   <div className="screen-mode-bar"><div role="tablist" aria-label="功能示例">{(['CODEX','MEDIA','SHORTCUTS'] as Mode[]).map((mode,index)=><button key={mode} role="tab" aria-selected={state.mode===mode} onClick={()=>onMode(mode)}><span className="mono">0{index+1}</span>{['Codex','媒体','快捷键'][index]}</button>)}</div><span className="screen-mode-marker" aria-hidden="true">⌘</span></div>
   <div className="trial-platform" role="group" aria-label="快捷键平台"><span>组合键</span><button aria-pressed={state.platform==='windows'} onClick={()=>dispatch({type:'platform',platform:'windows'})}>Windows / Linux</button><button aria-pressed={state.platform==='mac'} onClick={()=>dispatch({type:'platform',platform:'mac'})}>macOS</button></div>
   <motion.div className="monitor-view" key={view} initial={{opacity:0}} animate={{opacity:1}} transition={{duration:reduced?0:.13}}>
    <div className="screen-view-heading"><span className="mono">{key?key.id:'AA / 013'}</span><h3>{title}</h3><span className="screen-heading-line"/></div>
    {view==='ready'?<div className="screen-idle"><div className="idle-cross" aria-hidden="true">⌖</div><p>一个动作，<br/>少一次鼠标切换。</p><div className="idle-key-labels"><button onClick={()=>onKey('K02')}>新建 Codex 会话 ↗</button><button onClick={()=>onMode('MEDIA')}>看看触摸板能做什么 ↗</button></div><small>按键使用 Codex 模板；旋钮、摇杆和触摸板使用默认映射。</small></div>:null}
    {view==='CODEX'||key?<CodexDemo state={state} view={view} onKey={onKey} onView={onView}/>:null}
    {view==='MEDIA'||view==='touch'||view==='encoder'?<MediaDemo state={state} dispatch={dispatch}/>:null}
    {view==='SHORTCUTS'?<Shortcuts state={state} dispatch={dispatch}/>:null}
    {view==='joystick'?<NavigationDemo state={state} vector={vector}/>:null}
   </motion.div>
   <div className="screen-bottom-line"><span>本页示例 · 未连接设备或应用</span><span>原项目映射</span></div>
  </div><div className="monitor-chin"><span>ACID ALLOY</span><i/></div></div><div className="computer-stand" aria-hidden="true"/>
  <div className="computer-status"><div className="work-status" role="status">{state.status}</div><button onClick={onReset} aria-label="复位试用">↺ 复位</button></div>
 </div>;
}
