import bpy, pathlib, json, hashlib, struct, math, re, sys, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path(r'C:\Users\myw\Documents\ChatGPT\硬件\modeling');D=P/'acid_alloy'
sys.path.insert(0,str(P/'tools'));import openmicro_controls as ui
assert pathlib.Path(bpy.data.filepath)==P/'assets/OpenMicroKbd_AcidAlloy.blend'
ui.set_demo(bpy.context,False);bpy.context.scene.frame_set(1);bpy.ops.omk.reset_controls();bpy.context.view_layer.update()
base=json.loads((D/'baseline.json').read_text())
report={'source_unchanged':hashlib.sha256((P/'assets/OpenMicroKbd.blend').read_bytes()).hexdigest()==base['source_sha256'],
        'missing_original_objects':sorted(set(base['objects'])-set(bpy.data.objects.keys())),
        'added_objects':sorted(set(bpy.data.objects.keys())-set(base['objects'])),
        'reparented_original_objects':[],'changed_original_meshes':[],
        'unexpected_geometry_changes':[],'changed_vertex_counts':[],'visibility_changes':[]}
for name,old in base['objects'].items():
    ob=bpy.data.objects.get(name)
    if ob is None:continue
    if (ob.parent.name if ob.parent else None)!=old['parent']:report['reparented_original_objects'].append(name)
    if ob.hide_render!=old['hide_render']:report['visibility_changes'].append(name)
    if ob.type=='MESH':
        sha=hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in ob.data.vertices)).hexdigest()
        if sha!=old['mesh_hash']:
            report['changed_original_meshes'].append(name)
            if not (re.match(r'SW\d+_(Cap$|Legend_)',name) or name=='OpenMicroRotator_SourceMesh'):
                report['unexpected_geometry_changes'].append(name)
        if len(ob.data.vertices)!=old['vertices']:report['changed_vertex_counts'].append(name)

def evaluated(ob):
    eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh()
    vs=[eo.matrix_world@v.co for v in me.vertices];fs=[list(p.vertices) for p in me.polygons]
    eo.to_mesh_clear();return vs,fs
def tree(ob):
    vs,fs=evaluated(ob);return BVHTree.FromPolygons(vs,fs)
def bounds(ob):
    eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());ps=[eo.matrix_world@Vector(c) for c in eo.bound_box]
    return [(min(p[i] for p in ps),max(p[i] for p in ps)) for i in range(3)]
def overlaps_bb(a,b):return all(a[i][0]<b[i][1] and b[i][0]<a[i][1] for i in range(3))
panel=bpy.data.objects['AA_CoverPanel'];pt=tree(panel);pb=bounds(panel)
report['panel_intersections_at_rest']=[]
for ob in bpy.data.objects:
    if ob==panel or ob.type!='MESH' or ob.hide_render or any(c.name in ('90_Studio','99_SourceReferences') for c in ob.users_collection):continue
    if overlaps_bb(pb,bounds(ob)):
        count=len(pt.overlap(tree(ob)))
        if count:report['panel_intersections_at_rest'].append({'object':ob.name,'triangle_pairs':count})
bm=bmesh.new();bm.from_mesh(panel.data)
report['panel_nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges)
seen=set();components=0
for v in bm.verts:
    if v in seen:continue
    components+=1;stack=[v];seen.add(v)
    while stack:
        cur=stack.pop()
        for edge in cur.link_edges:
            other=edge.other_vert(cur)
            if other not in seen:seen.add(other);stack.append(other)
report['panel_connected_components']=components;bm.free()

caps=[bpy.data.objects[f'SW{n:02d}_Cap'] for n in range(3,16)]
report['keys']=[];report['cap_clearance_samples']=[]
for num in range(3,16):
    ob=bpy.data.objects[f'SW{num:02d}_Cap'];ctrl=bpy.data.objects[f'CTRL_SW{num:02d}']
    before={x.name:x.matrix_world.translation.copy() for x in caps}
    bpy.ops.omk.toggle_key(target=ctrl.name);bpy.context.view_layer.update()
    delta={x.name:list(x.matrix_world.translation-before[x.name]) for x in caps}
    ok=all(abs(v[2]-(-3.2 if n==ob.name else 0))<.001 and abs(v[0])+abs(v[1])<.001 for n,v in delta.items())
    report['keys'].append({'key':num,'independent_press_pass':ok,'travel_mm':-delta[ob.name][2]})
    bpy.ops.omk.toggle_key(target=ctrl.name)
    fixed=[x for x in bpy.data.objects if x.type=='MESH' and not x.hide_render and x.name.startswith(f'SW{num:02d}_') and not ('_Cap' in x.name or '_Legend' in x.name or '_Stem' in x.name or '_Slider' in x.name or '_Cross' in x.name)]
    fixed += [bpy.data.objects['PCB_Main'],panel]
    fixed_trees={x.name:tree(x) for x in fixed}
    for press in (0,.25,.5,.75,1):
        ctrl['press']=press;ctrl.update_tag();bpy.context.view_layer.update();ct=tree(ob)
        hits=[name for name,t in fixed_trees.items() if ct.overlap(t)]
        report['cap_clearance_samples'].append({'key':num,'press':press,'intersections':hits})
    ctrl['press']=0.;ctrl.update_tag();bpy.context.view_layer.update()

joy=bpy.data.objects['CTRL_Joystick'];cap=bpy.data.objects['OpenMicroJoystickCap_SourceMesh'];report['joystick']=[]
obstacles=[panel]+caps
for x,y,p in [(0,0,0),(23,0,0),(-23,0,0),(0,23,0),(0,-23,0),(23,23,1),(-23,-23,1),(23,-23,1),(-23,23,1)]:
    joy['tilt_x_deg']=x;joy['tilt_y_deg']=y;joy['press']=p;joy.update_tag();bpy.context.view_layer.update();jt=tree(cap)
    report['joystick'].append({'pose':[x,y,p],'cap_intersections':[o.name for o in obstacles if jt.overlap(tree(o))]})
bpy.ops.omk.reset_controls();bpy.context.view_layer.update()
enc=bpy.data.objects['CTRL_Encoder'];knob=bpy.data.objects['OpenMicroRotator_SourceMesh'];report['encoder_panel']=[]
for angle in (0,30,60,90,120,180,270):
    enc['rotation_deg']=angle;enc['press']=1.;enc.update_tag();bpy.context.view_layer.update()
    report['encoder_panel'].append({'angle':angle,'intersections':len(tree(knob).overlap(pt))})
bpy.ops.omk.reset_controls();bpy.context.view_layer.update()

initial={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='MESH' and not o.hide_render}
root=bpy.data.objects['OMK_ROOT_CTRL'];report['explode']=[]
for amt in (0,.25,.5,.75,1):
    root['explode']=amt;root.update_tag();bpy.context.view_layer.update()
    report['explode'].append({'amount':amt,'panel_z_offset':panel.matrix_world.translation.z,'panel_intersections':[o.name for o in [bpy.data.objects['PCB_Main']]+caps if tree(panel).overlap(tree(o))]})
bpy.ops.omk.reset_controls();bpy.context.view_layer.update()
report['reset_max_matrix_error']=max(max(abs(o.matrix_world[i][j]-initial[o.name][i][j]) for i in range(4) for j in range(4)) for o in bpy.data.objects if o.name in initial)
report['invalid_drivers']=[o.name for o in bpy.data.objects if o.animation_data and any(not c.driver.is_valid for c in o.animation_data.drivers)]
report['packed_images']=[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE']
report['scope']='Preserved original object identities, parents and mesh vertex counts. Surface intersections sampled at listed poses; not a manufacturing-tolerance or continuous solid collision certification.'
(D/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
result={k:v for k,v in report.items() if k not in ('changed_original_meshes','cap_clearance_samples','keys','packed_images')}
result['key_pass_count']=sum(x['independent_press_pass'] for x in report['keys'])
result['cap_failing_samples']=[x for x in report['cap_clearance_samples'] if x['intersections']]
result['packed_image_count']=len(report['packed_images'])
