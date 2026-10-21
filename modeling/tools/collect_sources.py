"""Inventory authoritative source CAD and PCB files; never modify them."""
import csv, hashlib, json, pathlib, re, zipfile
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[2]
REPO=ROOT/'device'
OUT=ROOT/'modeling/references'
OUT.mkdir(parents=True,exist_ok=True)

def bounds(vertices):
    lo=[min(v[i] for v in vertices) for i in range(3)]
    hi=[max(v[i] for v in vertices) for i in range(3)]
    return {'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]}

inventory=[]
meshes=[]
paths=list((REPO/'hw/v1/mechanical').glob('*.3mf'))+[pathlib.Path('D:/App/keyboard.3mf')]
for path in paths:
    item={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':[]}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.endswith('.model'):continue
            root=ET.fromstring(z.read(name)); ns={'m':root.tag.split('}')[0][1:]}
            for obj in root.findall('.//m:object',ns):
                vs=[[float(v.attrib[k]) for k in ('x','y','z')] for v in obj.findall('m:mesh/m:vertices/m:vertex',ns)]
                ts=[[int(t.attrib[k]) for k in ('v1','v2','v3')] for t in obj.findall('m:mesh/m:triangles/m:triangle',ns)]
                record={'id':obj.get('id'),'name':obj.get('name'),'entry':name,'unit':root.get('unit','millimeter'), 'components':[dict(c.attrib) for c in obj.findall('m:components/m:component',ns)]}
                if vs:
                    record.update(bounds=bounds(vs),vertices=len(vs),triangles=len(ts))
                    meshes.append({'source':path.name,**record,'vertex_data':vs,'triangle_data':ts})
                item['objects'].append(record)
            item.setdefault('build_items',[]).extend(dict(x.attrib) for x in root.findall('m:build/m:item',ns))
    inventory.append(item)
with zipfile.ZipFile('D:/App/keyboard.zip') as z:
    archive=[{'entry':i.filename,'bytes':i.file_size,'sha256':hashlib.sha256(z.read(i)).hexdigest()} for i in z.infolist() if not i.is_dir()]

text=(REPO/'hw/v1/pcb/keyboard.kicad_pcb').read_text(encoding='utf-8')
tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text)
stack=[]; tree=None
for token in tokens:
    if token=='(':
        v=[]
        if stack:stack[-1].append(v)
        stack.append(v)
    elif token==')':tree=stack.pop()
    else:
        if token.startswith('"'):
            try:token=json.loads(token)
            except json.JSONDecodeError:token=token[1:-1]
        stack[-1].append(token)
def field(node,key):return next((v[1:] for v in node if isinstance(v,list) and v and v[0]==key),[])
fps=[]
for fp in tree:
    if not isinstance(fp,list) or not fp or fp[0]!='footprint':continue
    props={x[1]:x[2] for x in fp if isinstance(x,list) and x and x[0]=='property'}
    fps.append({'reference':props.get('Reference'),'value':props.get('Value'),'footprint':fp[1], 'at':field(fp,'at'),'layer':field(fp,'layer'),'pads':[x[1:] for x in fp if isinstance(x,list) and x and x[0]=='pad'], 'graphics':[x for x in fp if isinstance(x,list) and x and x[0] in ('fp_line','fp_rect','fp_circle','fp_arc')], 'models':[x for x in fp if isinstance(x,list) and x and x[0]=='model']})
edges=[x for x in tree if isinstance(x,list) and x and x[0] in ('gr_line','gr_arc','gr_rect') and field(x,'layer')==['Edge.Cuts']]
with (REPO/'hw/v1/fab/keyboard-pos-all.csv').open(encoding='utf-8-sig',newline='') as f:positions=list(csv.DictReader(f))
data={'inventory':inventory,'provided_zip':archive,'pcb':{'thickness_mm':1.6,'footprints':fps,'edge_cuts':edges,'placements':positions}}
(OUT/'source_inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'source_meshes.json').write_text(json.dumps(meshes,separators=(',',':')),encoding='utf-8')
print(json.dumps({'sources':[{'file':pathlib.Path(x['file']).name,'meshes':[{'id':y['id'],'bounds':y.get('bounds')} for y in x['objects'] if 'bounds'in y]} for x in inventory], 'footprints':len(fps),'outline':edges,'controls':[{'ref':f['reference'],'at':f['at'],'graphics':f['graphics']} for f in fps if f['reference'] in ('SW1','J1')]},ensure_ascii=False,indent=2))
