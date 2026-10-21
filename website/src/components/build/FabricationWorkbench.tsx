'use client';
import type {PcbState,SmtState} from '@/data/build';
import {smdParts} from '@/data/build';
import FilePicker from '../interactive/FilePicker';
import BoardView,{LabSteps} from './BoardView';

const colors=[['purple','紫色'],['green','绿色'],['black','黑色'],['blue','蓝色'],['white','白色']];
export function PcbWorkbench({value,onChange,onSubmit,done}:{value:PcbState;onChange:(v:PcbState,edit?:boolean)=>void;onSubmit:()=>void;done:boolean}){
 const edit=(patch:Partial<PcbState>)=>onChange({...value,...patch,reviewed:false,submitted:false},true);
 const estimate=(20+value.quantity*3.5+(value.finish==='ENIG'?30:0)).toFixed(2);
 return <div className="lab-panel fab-workbench">
  <div className="lab-panel-top"><span className="lab-badge">模拟订单</span><span className="mono">PCB 在线配置</span><span className="lab-live">{done?'订单已生成':'本地演示'}</span></div>
  <LabSteps items={['制造文件','基本信息','PCB 工艺','检查订单','提交']} current={done?5:value.reviewed?4:value.file?2:0}/>
  <div className="fab-order-layout"><div className="fab-order-main">
   <FilePicker label="Gerber / ZIP" kind="zip" value={value.file} preset="keyboard-gerbers.zip" onChange={file=>edit({file})}/>
   <section className="fab-form-section"><h4>基本信息<span>与项目制造文件一致</span></h4><div className="fab-fields">
    <div className="fab-field"><span>板材类别</span><strong>FR-4 玻纤板</strong></div><div className="fab-field"><span>板子层数</span><strong>4 层</strong></div><div className="fab-field"><span>成品尺寸</span><strong>95 × 95 mm</strong></div>
    <label>板子数量<select aria-label="板子数量" value={value.quantity} onChange={event=>edit({quantity:Number(event.target.value)})}>{[5,10,20,50].map(quantity=><option key={quantity} value={quantity}>{quantity} 片</option>)}</select></label>
   </div></section>
   <section className="fab-form-section"><h4>PCB 工艺<span>参数改变后需重新检查</span></h4><div className="fab-fields">
    <label>成品板厚<select value={value.thickness} onChange={event=>edit({thickness:event.target.value})}><option value="1.6">1.6 mm（项目规格）</option><option value="1.0">1.0 mm（不匹配）</option></select></label>
    <label>阻焊颜色<select aria-label="阻焊颜色" value={value.color} onChange={event=>edit({color:event.target.value})}>{colors.map(([id,label])=><option key={id} value={id}>{label}</option>)}</select></label>
    <label>焊盘表面处理<select value={value.finish} onChange={event=>edit({finish:event.target.value})}><option value="ENIG">沉金 ENIG（推荐）</option><option value="HASL">无铅喷锡</option></select></label>
    <div className="fab-field"><span>字符 / 外层铜厚</span><strong>白色 / 1 oz</strong></div>
   </div><p className="lab-hint">四层叠构 JLC04161H-7628；过孔盖油。TP1 是裸铜触摸区域，项目推荐沉金表面处理。真实下单需核对制板文件与厂家审核。</p>
   {value.thickness!=='1.6'?<p role="alert" className="error-text">板厚与项目 1.6 mm 规格不一致，请恢复后再检查订单。</p>:null}
   </section>
   <section className="fab-form-section"><h4>贴片与交付</h4><dl className="fab-summary"><div><dt>SMT 贴片</dt><dd>下一步上传 BOM 与坐标，单独确认</dd></div><div><dt>交付方式</dt><dd>仅生成演示订单，不收集地址、不支付</dd></div></dl></section>
  </div><aside className="fab-order-summary"><BoardView color={value.color}/><h4>订单摘要</h4><dl className="fab-summary"><div><dt>电路板</dt><dd>95 × 95 mm / 四层</dd></div><div><dt>数量</dt><dd>{value.quantity} 片</dd></div><div><dt>表面处理</dt><dd>{value.finish==='ENIG'?'沉金':'无铅喷锡'}</dd></div><div><dt>交期</dt><dd>以厂家审核为准</dd></div></dl><div className="demo-price"><span>演示估算 · 非实时报价</span><strong>¥ {estimate}</strong><small>示意计算，不代表嘉立创报价</small></div>
   <button className="btn" disabled={!value.file||value.thickness!=='1.6'||done} onClick={()=>onChange({...value,reviewed:true})}>检查 PCB 订单</button><button className="btn primary" disabled={!value.reviewed||done} onClick={onSubmit}>提交模拟 PCB 订单</button>
   <p className="lab-hint" role="status">{done?'✓ 演示 PCB 订单已生成，可继续 SMT。':value.reviewed?'✓ 文件与参数检查完成，可以模拟提交。':'上传文件并检查工艺后，才能提交。'}</p>
  </aside></div>
  <div className="lab-source">流程参考 <a href="https://www.jlc.com/portal/server_guide_19858.html" target="_blank" rel="noreferrer">嘉立创下单指南 ↗</a> · 本站为适配后的交互演示</div>
 </div>;
}

const groups=[
 {id:'U3',name:'STM32F072CBT6',footprint:'LQFP-48',ids:['U3']},
 {id:'U2',name:'AP2112K-3.3TRG1',footprint:'SOT-25',ids:['U2']},
 {id:'U1',name:'USBLC6-2SC6',footprint:'SOT-23-6',ids:['U1']},
 {id:'Y1',name:'ABM8-8.000MHZ',footprint:'3225',ids:['Y1']},
 {id:'D1',name:'1N4148W-7-F',footprint:'SOD-123',ids:smdParts.filter(p=>p.id.startsWith('D')).map(p=>p.id)},
 {id:'LED1',name:'SK6812MINI-E',footprint:'MINI-E',ids:smdParts.filter(p=>p.id.startsWith('LED')).map(p=>p.id)},
 {id:'C1',name:'电容 · 按项目 BOM',footprint:'0402 / 0603',ids:smdParts.filter(p=>p.id.startsWith('C')).map(p=>p.id)},
 {id:'R1',name:'电阻 · 按项目 BOM',footprint:'0402',ids:smdParts.filter(p=>p.id.startsWith('R')).map(p=>p.id)},
 {id:'J2',name:'SSW-103-22-SM-D-VS',footprint:'2 × 3 / 2.54 mm',ids:['J2']},
 {id:'J3',name:'TYPE-C-31-M-12',footprint:'USB-C',ids:['J3']},
];
export function SmtWorkbench({value,onChange,onSubmit,quantity,done,color}:{value:SmtState;onChange:(v:SmtState,edit?:boolean)=>void;onSubmit:()=>void;quantity:number;done:boolean;color:string}){
 const edit=(patch:Partial<SmtState>)=>onChange({...value,...patch,dfm:false,submitted:false,error:''},true);
 const selected=smdParts.find(p=>p.id===value.selected)||smdParts[0];
 const delta=value.rotations[selected.id]||0;
 return <div className="lab-panel smt-workbench">
  <div className="lab-panel-top"><span className="lab-badge">模拟订单</span><span className="mono">SMT 贴片配置</span><span className="lab-live">{done?'贴片已确认':value.dfm?'DFM 已通过':'等待确认'}</span></div>
  <LabSteps items={['关联 PCB','上传资料','物料匹配','贴装预览','DFM / 提交']} current={done?5:value.matched?4:value.parsed?2:1}/>
  <div className="smt-order-link"><span>已关联 PCB 演示订单</span><strong>95 × 95 mm · 四层 · {quantity} 片</strong><label>贴片数量<input aria-label="贴片数量" type="number" min="1" max={quantity} value={value.quantity} onChange={event=>edit({quantity:Number(event.target.value)})}/></label></div>
  <div className="file-pair"><FilePicker label="BOM / CSV" kind="bom" value={value.bom} preset="keyboard-bom.csv" onChange={bom=>edit({bom,parsed:false,matched:false,rotations:{}})}/><FilePicker label="CPL / CSV" kind="smt" value={value.cpl} preset="keyboard-smt.csv" onChange={cpl=>edit({cpl,parsed:false,matched:false,rotations:{}})}/></div>
  <p className="lab-hint">本工作台用项目随附 BOM / CPL 演示匹配与贴装。自选文件只作格式检查，不会被上传或用于真实采购。SW3–SW15、SW1 与 J1 不在 SMT 坐标中，留待手工装配。</p>
  {!value.parsed?<button className="btn primary" disabled={!value.bom||!value.cpl} onClick={()=>edit({parsed:true,selected:'U3',side:'B'})}>解析并匹配元件</button>:<>
   <div className="smt-matching"><div className="smt-materials"><div className="smt-table-heading"><h4>物料匹配</h4><span>{smdParts.length} 个贴装位置</span></div><div className="smt-table-scroll"><table><thead><tr><th>位号 / 型号</th><th>数量</th><th>匹配</th></tr></thead><tbody>{groups.map(group=><tr key={group.id} className={group.ids.includes(value.selected)?'selected':''}><td><button onClick={()=>{const part=smdParts.find(p=>p.id===group.id)!;onChange({...value,selected:group.id,side:part.side})}}><strong>{group.name}</strong><small>{group.ids.length>3?`${group.ids[0]} … ${group.ids.at(-1)}`:group.ids.join(', ')} · {group.footprint}</small></button></td><td>{group.ids.length}</td><td>{value.matched?'✓ 已确认':'待确认'}</td></tr>)}</tbody></table></div><button className="btn" disabled={value.matched||done} onClick={()=>edit({matched:true})}>确认物料匹配</button></div>
   <div className="smt-placement"><div className="board-tools"><strong>贴装预览</strong>{['T','B'].map(side=><button key={side} aria-pressed={value.side===side} onClick={()=>onChange({...value,side})}>{side==='T'?'正面':'背面'}</button>)}</div><BoardView side={value.side} color={color} rotations={value.rotations}>{smdParts.filter(p=>p.side===value.side).map(part=><button key={part.id} className={`smt-placement-dot ${value.selected===part.id?'selected':''}`} style={{left:`${part.x/95*100}%`,top:`${part.y/95*100}%`}} aria-label={`查看贴片 ${part.id}`} onClick={()=>onChange({...value,selected:part.id})}>{value.selected===part.id?<span>{part.id}</span>:null}</button>)}</BoardView><div className="placement-detail"><strong>{selected.id} / {selected.label}</strong><span className="mono">X {selected.x.toFixed(2)} · Y {(95-selected.y).toFixed(2)} mm</span><span>方向 {(selected.rotation+delta)%360}° · {selected.side==='T'?'顶层':'底层'}</span><div><button className="btn small" disabled={!value.matched||done} onClick={()=>edit({rotations:{...value.rotations,[selected.id]:(delta+90)%360}})}>旋转选中元件</button><button className="text-button" disabled={done} onClick={()=>edit({rotations:{}})}>复位贴装方向</button></div><small>屏幕预览以左上为原点；坐标文件以左下为原点。方向对照项目 CPL，非厂家最终贴装图。</small></div></div></div>
   <div className="smt-dfm"><div><h4>DFM 检查</h4><p className="lab-hint">演示检查：物料确认、贴片数量及相对 CPL 的方向。实际 DFM 由厂家执行。</p>{value.error?<p role="alert" className="error-text">{value.error}</p>:null}{value.dfm?<p role="status" className="accent">✓ 演示 DFM 通过：方向一致，数量有效。</p>:null}</div><div className="smt-submit"><button className="btn" disabled={!value.matched||done} onClick={()=>{const rotated=Object.entries(value.rotations).filter(([,rotation])=>rotation%360!==0).map(([id])=>id);const error=!Number.isInteger(value.quantity)||value.quantity<1||value.quantity>quantity?'贴片数量必须为整数，且不大于 PCB 片数。':rotated.length?`${rotated.join('、')} 的方向与项目坐标不一致，请复位贴装方向后重试。`:'';onChange({...value,error,dfm:!error})}}>运行 DFM 检查</button><button className="btn primary" disabled={!value.dfm||done} onClick={onSubmit}>提交模拟 SMT 订单</button></div></div>
  </>}
  {done?<p role="status" className="lab-message">✓ SMT 演示订单已确认，接下来安装通孔元件。</p>:null}
  <div className="lab-source">流程参考 <a href="https://www.jlc.com/portal/server_guide_19875.html" target="_blank" rel="noreferrer">嘉立创物料匹配与贴装预览 ↗</a></div>
 </div>;
}
