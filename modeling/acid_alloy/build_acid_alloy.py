import bpy, math, json, pathlib, sys, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

P=pathlib.Path(r'C:\Users\myw\Documents\ChatGPT\硬件\modeling')
D=P/'acid_alloy';TARGET=P/'assets/MacroPad_AcidAlloy.blend'
assert pathlib.Path(bpy.data.filepath)==TARGET
assert 'AA_CoverPanel' not in bpy.data.objects, 'Already built; inspect before repeating'
sys.path.insert(0,str(P/'tools'))
import keyboard_controls as ui
ui.set_demo(bpy.context,False);bpy.context.scene.frame_set(1);bpy.ops.omk.reset_controls()
baseline_names=set(bpy.data.objects.keys())

def rgb(hexcolor):
    vals=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)
def mat(name,color,rough=.35,metal=0,trans=0,art=None):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb(color),1)
    nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*rgb(color),1)
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    bs.inputs['Transmission Weight'].default_value=trans;bs.inputs['IOR'].default_value=1.48
    bs.inputs['Coat Weight'].default_value=.18 if trans else .08
    if art:
        img=bpy.data.images.load(str(D/'textures'/art),check_existing=True);img.pack()
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;tex.extension='CLIP'
        uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='AA_PrintUV';nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(*rgb(color),1)
        nt.links.new(tex.outputs['Alpha'],mix.inputs[0]);nt.links.new(tex.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
        if trans:
            mul=nt.nodes.new('ShaderNodeMath');mul.operation='SUBTRACT';mul.inputs[0].default_value=1
            nt.links.new(tex.outputs['Alpha'],mul.inputs[1]);nt.links.new(mul.outputs[0],bs.inputs['Transmission Weight'])
    return m
def assign(o,m):
    o.data.materials.clear();o.data.materials.append(m)
    for f in o.data.polygons:f.material_index=0
def project_uv(o,cx=0,cy=0,w=100,h=100,axes=(0,1),top_only=False):
    uv=o.data.uv_layers.get('AA_PrintUV') or o.data.uv_layers.new(name='AA_PrintUV')
    for face in o.data.polygons:
        for li in face.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=((co[axes[0]]-cx)/w+.5,(co[axes[1]]-cy)/h+.5) if not top_only or face.normal.z>.6 else (-5,-5)

acid=mat('AA | acid yellow-green coating','#d0ef19',.30,art='panel_print.png')
graphite=mat('AA | graphite powder coat','#252a30',.40,.15)
front=mat('AA | front typography','#252a30',.40,.15,art='case_front_print.png')
side=mat('AA | side typography','#252a30',.40,.15,art='case_side_print.png')
silver=mat('AA | satin machined alloy','#bfc8cc',.23,.92,art='knob_print.png')
purple=mat('AA | ultraviolet soft-touch','#843bde',.32,art='joystick_print.png')
ink_acid=mat('AA | acid screen ink','#d0ef19',.46)
ink_dark=mat('AA | charcoal screen ink','#161a1e',.46)
ink_white=mat('AA | pale screen ink','#e6e9dd',.46)

shell=bpy.data.objects['Housing_Shell_V1'];assign(shell,graphite)
shell.data.materials.append(front);shell.data.materials.append(side)
uv=shell.data.uv_layers.new(name='AA_PrintUV')
for f in shell.data.polygons:
    pts=[shell.data.vertices[i].co for i in f.vertices]
    c=sum(pts,Vector())/len(pts)
    idx=1 if f.normal.y<-.5 and c.y<-46 else 2 if f.normal.x>.5 and c.x>46 else 0
    f.material_index=idx
    for li in f.loop_indices:
        co=shell.data.vertices[shell.data.loops[li].vertex_index].co
        uv.data[li].uv=(co.x/100+.5,(co.z+11)/12.6) if idx==1 else (co.y/100+.5,(co.z+11)/12.6) if idx==2 else (-5,-5)

# Keep every original key cap, its cavity and movement relationship.
key_centers={}
for num in range(3,16):
    ob=bpy.data.objects[f'SW{num:02d}_Cap']
    cx=(min(v.co.x for v in ob.data.vertices)+max(v.co.x for v in ob.data.vertices))/2
    cy=(min(v.co.y for v in ob.data.vertices)+max(v.co.y for v in ob.data.vertices))/2
    key_centers[num]=(cx,cy)
    trans=1 if 8<=num<=11 else 0
    color='#d0ef19' if num==3 else '#843bde' if num==4 else '#bfd673' if num in (8,11) else '#b3bdc2' if trans else '#20252b'
    material=mat(f'AA | key {num:02d}',color,.12 if trans else .34,0,trans,f'key_{num:02d}.png')
    assign(ob,material);project_uv(ob,cx,cy,17.2,17.2,top_only=True)
    # Retain original function marks as small secondary glyphs, projected onto cap.
    dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
    tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons]);ev.to_mesh_clear()
    for glyph in [g for g in bpy.data.objects if g.name.startswith(f'SW{num:02d}_Legend_') and g.type=='MESH']:
        assign(glyph,ink_dark if num==3 else ink_white if num==4 else ink_acid)
        points=[glyph.matrix_world@v.co for v in glyph.data.vertices]
        zmin=min(v.z for v in points);zmax=max(v.z for v in points);inv=glyph.matrix_world.inverted()
        for v,pt in zip(glyph.data.vertices,points):
            pt.x=cx+(pt.x-cx)*.38-4.4;pt.y=cy+(pt.y-cy)*.38-5.1
            hit=tree.ray_cast(Vector((pt.x,pt.y,20)),Vector((0,0,-1)))
            if hit[0] is not None:pt.z=hit[0].z+.008+.012*(pt.z-zmin)/max(zmax-zmin,.00001)
            v.co=inv@pt
        glyph.data.update()

# Change only the exterior of the existing knob; shaft/socket geometry is retained.
knob=bpy.data.objects['keyboardRotator_SourceMesh']
for v in knob.data.vertices:
    x,y,z=v.co;r=math.hypot(x,y)
    if r>5.8 and z>3:
        a=math.atan2(y,x);sector=(a+math.pi/6)%(math.pi/3)-math.pi/6
        target=7.5*(.28+.72*math.cos(math.pi/6)/math.cos(sector))
        factor=min(1,(r-5.8)/.9)*min(1,(z-3)/4)
        rr=r*(1-factor)+target*factor;v.co.x=x*rr/r;v.co.y=y*rr/r
knob.data.update();assign(knob,silver);project_uv(knob,0,0,15,15,top_only=True)
joy=bpy.data.objects['keyboardJoystickCap_SourceMesh'];assign(joy,purple);project_uv(joy,0,0,18,18,top_only=True)

# One new connected cover, including its integral perimeter return.
def loop(w,h,r,z,cx=0,cy=0,n=16):
    vs=[]
    for x,y,start in ((w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)):
        for i in range(n):
            a=math.radians(start+90*i/(n-1));vs.append((cx+x+r*math.cos(a),cy+y+r*math.sin(a),z))
    return vs
N=64
vs=loop(99.4,99.4,8.2,1.65)+loop(99.4,99.4,8.2,5.8)+loop(95.6,95.6,6.3,1.65)+loop(95.6,95.6,6.3,4.6)
faces=[]
for i in range(N):
    j=(i+1)%N
    faces.extend([(i,j,N+j,N+i),(2*N+j,2*N+i,3*N+i,3*N+j),(j,i,2*N+i,2*N+j)])
faces += [tuple(range(N,2*N)),tuple(reversed(range(3*N,4*N)))]
mesh=bpy.data.meshes.new('AA_CoverPanel_mesh');mesh.from_pydata(vs,[],faces);mesh.update()
panel=bpy.data.objects.new('AA_CoverPanel',mesh);bpy.data.collections['01_Housing'].objects.link(panel)
panel.parent=bpy.data.objects['OMK_ROOT_CTRL']
def recalc(o):
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
recalc(panel)
def cut_rect(cx,cy,w,h,r):
    verts=loop(w,h,r,-2,cx,cy,12)+loop(w,h,r,30,cx,cy,12);n=len(verts)//2
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new('AA_temporary_cut');me.from_pydata(verts,[],fs);me.update()
    cutter=bpy.data.objects.new('AA_temporary_cut',me);bpy.context.scene.collection.objects.link(cutter)
    mod=panel.modifiers.new('Opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=panel;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(me)
for num,(cx,cy) in key_centers.items():cut_rect(cx,cy,17.9,17.9,2.55)
cut_rect(-28.075,28.575,17.4,17.4,8.69)
cut_rect(30.5,30.1,20.6,22.5,1.1)
cut_rect(-28.575,-28.575,12.4,12.4,6.19)
for x in (-42.5,42.5):
    for y in (-42.5,42.5):cut_rect(x,y,5.5,5.5,2.74)
for n in range(1,9):
    parent=bpy.data.objects[f'LED{n}_ElectronicAssembly'];x,y=parent.matrix_world.translation.xy
    cut_rect(x,y,7.4 if abs(y)>40 else 4.2,4.2 if abs(y)>40 else 7.4,.8)
recalc(panel);assign(panel,acid);project_uv(panel)
bevel=panel.modifiers.new('Soft manufactured edges','BEVEL');bevel.width=.14;bevel.segments=3
panel['description']='Single-piece acid-yellow cover with integrated return, key travel wells, LED windows and accessible touch opening.'
panel['key_opening_mm']=17.9;panel['top_z_mm']=5.8;panel['nominal_cap_skirt_gap_mm']=.35
f=panel.driver_add('location',2);dr=f.driver;v=dr.variables.new();v.name='amount';v.type='SINGLE_PROP';v.targets[0].id=bpy.data.objects['OMK_ROOT_CTRL'];v.targets[0].data_path='["explode"]';dr.expression='52*amount'

led=bpy.data.objects['CTRL_LEDs'];led['color']=[.70,1.0,.06];led['brightness']=.42
led.id_properties_ui('color').update(default=[.70,1.0,.06]);led.id_properties_ui('brightness').update(default=.42);led.update_tag()
# The existing printed labels retain geometry; the black PCB and every internal device remain intact.
scene=bpy.context.scene;scene['design_variant']='ACID / ALLOY — Experimental Control System'
scene['design_constraint']='Original 1239 scene objects retained; only AA_CoverPanel added. Exterior finish and printed markings changed.'
scene.camera=bpy.data.objects['CAM_Hero'];scene.render.engine='CYCLES';scene.cycles.samples=48
scene.render.resolution_x=1500;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(D/'renders/01_acid_hero.png')
bpy.context.view_layer.update()
new=set(bpy.data.objects.keys())-baseline_names;missing=baseline_names-set(bpy.data.objects.keys())
assert new=={'AA_CoverPanel'} and not missing,(new,missing)
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET))
result={'saved':str(TARGET),'new_objects':list(new),'missing_objects':list(missing),'object_count':len(bpy.data.objects),'panel_vertices':len(panel.data.vertices)}
(D/'build_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
