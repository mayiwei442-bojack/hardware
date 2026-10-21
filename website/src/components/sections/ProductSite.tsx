'use client';
import {useState} from 'react';
import {assets} from '@/data/assets';
import {resources} from '@/data/product';
import {usePageMotion} from '@/lib/animations/usePageMotion';
import Navigation from '../ui/Navigation';
import {ExternalLink,SectionLabel} from '../ui/Primitives';
import OverviewHero from './OverviewHero';
import AssetPlaceholder from '../placeholders/AssetPlaceholder';
import Hardware from './Hardware';
import Workstation from './Workstation';
import BuildLab from './BuildLab';
function ProductImages(){const [failed,setFailed]=useState<string[]>([]);return <div className="product-images">{assets.productImages.status==='ready'&&assets.productImages.items.length?assets.productImages.items.map(item=>failed.includes(item.src)?<AssetPlaceholder key={item.src} label="产品图片" status="加载失败" compact/>:<img key={item.src} src={item.src} alt={item.alt} width={item.width} height={item.height} loading="lazy" onError={()=>setFailed(list=>[...list,item.src])}/>):<AssetPlaceholder label="产品图片" code="静帧" compact/>}</div>}
export default function ProductSite(){
 usePageMotion();
 return <><a href="#main" className="skip-link">跳转到内容</a><Navigation/><main id="main"><OverviewHero/><Hardware/><div className="signal-divider" aria-hidden="true"><span className="mono">输入信号</span><svg viewBox="0 0 1200 100" preserveAspectRatio="none"><path className="signal-path" d="M0 50H320L350 20L380 80L410 35L440 65L470 50H650L680 10L710 90L740 30L770 70L800 50H1200"/></svg><span className="mono">控制输出</span></div><Workstation/><BuildLab/><section id="resources" className="section resources-section"><SectionLabel n="05" label="项目资料"/><div className="section-heading" data-reveal><h2>项目制作<br/><span className="accent">所需资料。</span></h2><p>下载所需文件，<br/>按步骤完成制作。</p></div><div className="resource-grid">{[['01','项目仓库','项目仓库',resources.project],['02','电路板制造','Gerber 文件',resources.gerber],['03','元件清单','BOM 清单',resources.bom],['04','贴片坐标','SMT 坐标',resources.smt],['05','外壳模型','打印外壳',resources.shell],['06','控制器固件','控制器固件',resources.firmware]].map(([n,title,cn,url])=><ExternalLink key={n} href={url} className="resource-link"><span className="mono muted">{n}</span><span><strong>{title}</strong><small>{cn}</small></span></ExternalLink>)}</div><div className="resource-media"><ProductImages/><details className="asset-inventory"><summary>展示素材状态 <span className="mono">{[...Object.values(assets.models),assets.productImages,assets.keycapTextures].filter(asset=>asset.status==='pending').length.toString().padStart(2,'0')} 项待接入</span></summary><ul>{Object.values(assets.models).map(model=><li key={model.filename}><span>{model.filename}</span><span>{model.status==='pending'?'待接入':'已就绪'}</span></li>)}<li><span>产品图片</span><span>{assets.productImages.status==='pending'?'待接入':'已就绪'}</span></li><li><span>键帽贴图</span><span>{assets.keycapTextures.status==='pending'?'待接入':'已就绪'}</span></li></ul></details></div><footer className="footer"><a href="#overview" className="footer-logo">ACID ALLOY<span>AA / 013</span></a><div className="footer-credits"><span>设计与制作</span><ExternalLink href={resources.project}>mayiwei442-bojack</ExternalLink><span className="mono">版本 01 / 2026</span></div><a className="back-top" href="#overview" aria-label="返回顶部">↑</a></footer></section></main></>;
}
