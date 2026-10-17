"""Recognizable packages from v1 KiCad positions; not manufacturing models."""
import bpy,json,math,sys,importlib
from mathutils import Matrix
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
import model_helpers
importlib.reload(model_helpers)
from model_helpers import *

source=json.loads((ROOT/'references/source_inventory.json').read_text(encoding='utf-8-sig'))
fps={p['reference']:p for p in source['pcb']['footprints']}
black=material('OMK IC epoxy',(.013,.015,.018),0,.44)
ceramic=material('OMK MLCC ceramic',(.32,.18,.078),0,.48)
silver=material('OMK Solder tin',(.55,.58,.62),.8,.29)
copper=material('OMK Exposed copper',(.56,.245,.082),.78,.31)
white=material('OMK LED ceramic',(.8,.79,.70),0,.37)
ink=material('OMK Silkscreen',(.72,.74,.72),0,.6)
steel=material('OMK Crystal lid',(.48,.51,.54),.85,.27)

ctrl=empty('CTRL_LEDs')
ctrl['brightness']=.65;ctrl.id_properties_ui('brightness').update(min=0,max=1,description='LED intensity, 0 = off')
ctrl['color']=[.015,.5,1.0];ctrl.id_properties_ui('color').update(min=0,max=1,subtype='COLOR')
em=material('OMK LED emission',(.015,.5,1.0),0,.3)
bs=next(n for n in em.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
def drive(owner,path,expr,prop,index=None):
    fc=owner.driver_add(path) if index is None else owner.driver_add(path,index)
    dr=fc.driver;dr.type='SCRIPTED';dr.expression=expr
    v=dr.variables.new();v.name='v';v.type='SINGLE_PROP';v.targets[0].id=ctrl;v.targets[0].data_path=prop
drive(bs.inputs['Emission Strength'],'default_value','18*v','["brightness"]')
for i in range(3):
    drive(bs.inputs['Emission Color'],'default_value','v',f'["color"][{i}]',i)
    drive(bs.inputs['Base Color'],'default_value','v',f'["color"][{i}]',i)

def child(o,parent):
    o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4)
    return o
def part(name,loc,dims,mat,ass,coll='07_Electronics',bevel=.035):
    return child(cube(name,loc,dims,mat,coll,bevel=bevel),ass)
def label(name,body,loc,size,ass,bottom=False,coll='07_Electronics'):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=0
    ob=bpy.data.objects.new(name,cu);collection(coll).objects.link(ob);ob.location=loc
    if bottom:ob.rotation_euler.x=math.pi
    cu.materials.append(ink);child(ob,ass);return ob
def getv(p,k,default=None):return next((v[1:] for v in p if isinstance(v,list) and v[0]==k),default)
def assembly(ref,coll='07_Electronics'):
    f=fps[ref];a=f['at'];o=empty(ref+'_ElectronicAssembly',(float(a[0]),-float(a[1]),0),coll)
    o.rotation_euler.z=math.radians(float(a[2]) if len(a)>2 else 0)
    o['reference']=ref;o['value']=f['value'];o['source_footprint']=f['footprint'];o['pcb_side']=f['layer'][0]
    o['geometry_fidelity']='Package family approximation; source PCB placement and pad coordinates'
    return o

# Circular touch copper is exactly 9 mm in the source footprint.
touch=assembly('TP1');child(cylinder('TP1_CapacitiveTouch_Copper',(0,0,1.635),4.5,.07,copper,'07_Electronics',vertices=96),touch)
touch['touch']=0.0;touch.id_properties_ui('touch').update(min=0,max=1,description='Visual touch activation')

ledrefs=[];built=[]
for ref,f in fps.items():
    if ref.startswith(('SW','H')) or ref in ('J1','J3','TP1'):continue
    is_led=ref.startswith('LED');coll='08_LEDs' if is_led else '07_Electronics'
    ass=assembly(ref,coll);bottom=f['layer'][0]=='B.Cu';sgn=-1 if bottom else 1;surface=0 if bottom else 1.6
    # Pads use the footprint's local coordinates and its full assembly rotation.
    for pad in f['pads']:
        pos=getv(pad,'at');size=getv(pad,'size')
        if pos is None or size is None:continue
        px,py=float(pos[0]),-float(pos[1]);sx,sy=map(float,size[:2])
        part(f'{ref}_Pad_{pad[0]}',(px,py,surface+sgn*.065),(sx,sy,.13),silver,ass,coll,.025)
    if is_led:
        ledrefs.append(ref)
        # Reverse mount: body on populated side, emitting face through Edge.Cuts.
        part(ref+'_CeramicBody',(0,0,surface+sgn*.68),(3.2,2.8,1.20),white,ass,coll,.15)
        part(ref+'_Lens',(0,0,surface-sgn*.07),(2.45,2.1,.18),em,ass,coll,.15)
        for pad in f['pads']:
            pos=getv(pad,'at');px,py=float(pos[0]),-float(pos[1])
            part(f'{ref}_Lead_{pad[0]}',(px*.77,py,surface+sgn*.2),(1.55,.55,.25),silver,ass,coll,.025)
        label(ref+'_Reference',ref,(0,-2.5,surface+sgn*.015),.8,ass,bottom,coll)
        data=bpy.data.lights.new(ref+'_Light','AREA');data.shape='RECTANGLE';data.size=2.4;data.size_y=2.0
        data.energy=22000;data.color=(.015,.5,1.0)
        lamp=bpy.data.objects.new(ref+'_Light',data);collection(coll).objects.link(lamp)
        lamp.location=(0,0,surface-sgn*.25)
        if bottom:lamp.rotation_euler.x=math.pi
        child(lamp,ass)
        # Coordinates are numeric millimeters; power includes the scene's geometric scale.
        drive(data,'energy','22000*v','["brightness"]')
        for i in range(3):drive(data,'color','v',f'["color"][{i}]',i)
    elif ref.startswith(('C','R','D')):
        if ref.startswith('D'):dims=(2.7,1.6,1.0);mat=black
        elif '0603' in f['footprint']:dims=(1.6,.8,.7);mat=ceramic
        else:dims=(1.0,.5,.5);mat=ceramic if ref.startswith('C') else black
        part(ref+'_Body',(0,0,surface+sgn*(dims[2]/2+.04)),dims,mat,ass,bevel=.06)
        for side in (-1,1):part(f'{ref}_Endcap_{side}',(side*(dims[0]/2-.10),0,surface+sgn*(dims[2]/2+.04)),(.21,dims[1]+.015,dims[2]+.015),silver,ass,bevel=.025)
        if ref.startswith('D'):part(ref+'_CathodeBand',(-.85,0,surface+sgn*1.05),(.22,1.45,.015),ink,ass,bevel=.005)
    elif ref in ('U1','U2','U3'):
        dims=(7,7,1.35) if ref=='U3' else (1.6,2.9,1.1)
        part(ref+'_Package',(0,0,-dims[2]/2-.12),dims,black,ass,bevel=.12)
        for pad in f['pads']:
            pos=getv(pad,'at');px,py=float(pos[0]),-float(pos[1])
            # Short gull-wing leads rise from exact pads to the package wall.
            if abs(px)>abs(py):loc=(px*.92,py,-.28);dim=(abs(px)*.23+.2,.23,.4)
            else:loc=(px,py*.92,-.28);dim=(.23,abs(py)*.23+.2,.4)
            part(f'{ref}_Lead_{pad[0]}',loc,dim,silver,ass,bevel=.04)
        label(ref+'_Marking','STM32\nF072CBT6' if ref=='U3' else ('AP2112' if ref=='U2' else 'USBLC6'),(0,0,-dims[2]-.13),.72 if ref=='U3' else .30,ass,True)
        child(cylinder(ref+'_Pin1Mark',(-dims[0]/2+.6,-dims[1]/2+.6,-dims[2]-.14),.2,.014,ink,'07_Electronics',vertices=24),ass)
    elif ref=='Y1':
        part('Y1_CeramicBase',(0,0,-.18),(3.2,2.5,.3),black,ass)
        part('Y1_MetalCan',(0,0,-.62),(3.1,2.4,.7),steel,ass,bevel=.20)
        label('Y1_Marking','8.000',(0,0,-.985),.55,ass,True)
    elif ref=='J2':
        body=part('J2_SWD_SocketBody',(0,0,-2.1),(7.62,5.08,4.0),black,ass,bevel=.12)
        for ix in (-1,0,1):
            for iy in (-1,1):
                # Six physically open sockets, each with recessed metal contacts.
                cutter=cube('Socket cutter',(ix*2.54,iy*1.27,-2.6),(1.05,1.05,3.8),None,coll,bevel=0)
                child(cutter,ass);bpy.context.view_layer.update();apply_boolean(body,cutter)
                part(f'J2_Contact_{ix}_{iy}',(ix*2.54,iy*1.27,-1.05),(.83,.83,.3),copper,ass,bevel=.04)
        label('J2_Reference','SWD',(0,3.1,-.018),.85,ass,True)
    built.append(ref)

# Gold annuli convey plated through holes without recreating circuit routing.
for ref,f in fps.items():
    if not (ref.startswith(('SW','H')) or ref=='J1'):continue
    a=f['at'];angle=math.radians(float(a[2]) if len(a)>2 else 0);c,s=math.cos(angle),math.sin(angle)
    for pad in f['pads']:
        if pad[1]!='thru_hole':continue
        pos=getv(pad,'at');size=getv(pad,'size');drill=getv(pad,'drill')
        if not pos or not size or not drill or drill[0]=='oval':continue
        x,y=float(pos[0]),-float(pos[1]);wx=float(a[0])+x*c-y*s;wy=-float(a[1])+x*s+y*c
        rr=float(size[0])/2;ri=float(drill[0])/2
        if rr<=ri:continue
        for z,side in ((1.611,'F'),(-.011,'B')):
            vs=[];faces=[];n=32
            for radius in (rr,ri):
                vs.extend([(wx+radius*math.cos(i*2*math.pi/n),wy+radius*math.sin(i*2*math.pi/n),z) for i in range(n)])
            for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
            me=bpy.data.meshes.new('Plated annulus');me.from_pydata(vs,[],faces);me.update()
            ob=bpy.data.objects.new(f'{ref}_PTH_{pad[0]}_{side}',me);collection('02_PCB').objects.link(ob);me.materials.append(copper)

bpy.context.view_layer.update()
save('direct_02_electronics.blend')
review_render('direct_02_electronics_top.png',camera('AUDIT_Top',(0,0,150),(0,0,0),115),(1200,1200))
shell=bpy.data.objects['Housing_Shell_V1'];old=shell.hide_render;shell.hide_render=True
review_render('direct_02_electronics_bottom.png',camera('AUDIT_Bottom',(0,0,-160),(0,0,0),115),(1400,1400))
shell.hide_render=old
save('direct_02_electronics.blend')
report={'built_component_refs':built,'led_refs':ledrefs,'touch_diameter_mm':9,'source':'source_inventory.json','status':'Geometry created; visual and lighting acceptance pending'}
(ROOT/'references/electronics_build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
result=report
