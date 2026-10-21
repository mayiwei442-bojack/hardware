export default function AssetPlaceholder({label='三维模型',code='AA–013',compact=false,status='待接入'}:{label?:string;code?:string;compact?:boolean;status?:string}){
 return <div className={`asset-placeholder ${compact?'compact':''}`} role="img" aria-label={`${label} / ${status}`}>
  <div className="asset-top mono"><span>{code}</span><span className="asset-status"><i/>{status}</span></div>
  <div className="registration" aria-hidden="true"><span/><span/><span/><span/><div className="target-line horizontal"/><div className="target-line vertical"/></div>
  <div className="asset-center"><span className="asset-symbol" aria-hidden="true">⌖</span><span className="mono">{label} / {status}</span><small>{status==='加载失败'?'资源暂时无法加载':status==='正在加载'?'正在载入展示资源':'展示资源待接入'}</small></div>
  <div className="asset-bottom mono"><span>ACID ALLOY</span><span>视图 / {code}</span></div>
 </div>;
}
