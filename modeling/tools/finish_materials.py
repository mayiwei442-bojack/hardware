import bpy,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
from model_helpers import *

# Consistent physical shaders, independent of the Workbench display color.
settings={
 'Housing | printed white polymer':((.82,.84,.85),0,.38,0),
 'Control | warm white printed resin':((.86,.84,.78),0,.34,0),
 'Keycap | warm white polymer':((.89,.90,.86),0,.31,0),
 'Keycap | sunflower yellow polymer':((.95,.61,.022),0,.30,0),
 'Keycap | clear polycarbonate':((.96,.985,1),0,.075,1),
 'PCB | matte black solder mask':((.008,.012,.016),.05,.36,0),
 'Choc | charcoal housing':((.023,.033,.034),0,.37,0),
 'Choc | black polymer':((.012,.018,.023),0,.40,0),
 'Choc | tactile brown polymer':((.24,.083,.025),0,.31,0),
 'Keycap | printed charcoal legends':((.008,.011,.012),0,.48,0),
 'Fastener stainless':((.52,.56,.60),.88,.23,0),
 'Control | brushed nickel':((.51,.54,.56),.83,.27,0),
}
for name,(color,metal,rough,trans) in settings.items():
    m=material(name,color,metal,rough,trans)
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Alpha'].default_value=1;bs.inputs['IOR'].default_value=1.58 if trans else 1.46
    if trans:m.diffuse_color=(*color,.25)

# Very fine printed polymer grain: scale uses object coordinates in millimeters.
for name in ('Housing | printed white polymer','Control | warm white printed resin'):
    m=bpy.data.materials[name];nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=22
    coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.018
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

# Rebuild the star as an outline and the terminal as a framed prompt, matching the photograph.
ink=bpy.data.materials['Keycap | printed charcoal legends']
def stroke(name,pts,parent,width=.14,closed=False):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=width;cu.bevel_resolution=3
    sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):p.co=(*co,1)
    sp.use_cyclic_u=closed;ob=bpy.data.objects.new(name,cu);collection('04_Keycaps').objects.link(ob);cu.materials.append(ink);keep_parent(ob,parent)
    return ob
remove_generated(['SW03_Legend_Star','SW15_Legend_Terminal'])
x,y=-9.525,28.575
pts=[(x+(3.3 if i%2==0 else 1.5)*math.cos(math.pi/2+i*math.pi/5),y+(3.3 if i%2==0 else 1.5)*math.sin(math.pi/2+i*math.pi/5),10.1) for i in range(10)]
stroke('SW03_Legend_StarOutline',pts,bpy.data.objects['SW03_CapDetach'],.17,True)
x,y=28.575,-9.525;p=bpy.data.objects['SW15_CapDetach']
stroke('SW15_Legend_TerminalFrame',[(x-3.7,y-2.8,10.1),(x+3.7,y-2.8,10.1),(x+3.7,y+2.8,10.1),(x-3.7,y+2.8,10.1)],p,.14,True)
stroke('SW15_Legend_Prompt',[(x-2.25,y+1.25,10.1),(x-.75,y,10.1),(x-2.25,y-1.25,10.1)],p,.20)
stroke('SW15_Legend_Cursor',[(x+.2,y-1.3,10.1),(x+2.35,y-1.3,10.1)],p,.18)
bpy.context.view_layer.update()
for num in range(3,16):
    ref=f'SW{num:02d}';cap=bpy.data.objects[ref+'_Cap']
    ev=cap.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
    for ob in list(bpy.data.objects):
        if not ob.name.startswith(ref+'_Legend_'):continue
        if ob.type=='CURVE':
            bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object
        if ob.type!='MESH':continue
        # Apply appearance modifiers before projecting the marking to the cap.
        for mod in list(ob.modifiers):
            bpy.context.view_layer.objects.active=ob
            bpy.ops.object.modifier_apply(modifier=mod.name)
        pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=min(p.z for p in pts);hi=max(p.z for p in pts)
        inv=ob.matrix_world.inverted()
        for v,p in zip(ob.data.vertices,pts):
            hit=tree.ray_cast(Vector((p.x,p.y,20)),Vector((0,0,-1)))
            if hit[0] is not None:
                p.z=hit[0].z+.008+.012*(p.z-lo)/max(hi-lo,.0001);v.co=inv@p
        ob.data.update();ob['legend_finish']='Surface printed mark, 0.02 mm visual thickness'

# Visible touch feedback is an animation aid, not a claim of a physical indicator.
touchmat=bpy.data.materials['OMK Exposed copper'].copy();touchmat.name='OMK Touch copper feedback'
touchob=bpy.data.objects['TP1_CapacitiveTouch_Copper'];touchob.data.materials.clear();touchob.data.materials.append(touchmat)
bs=next(n for n in touchmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(.1,.5,1,1)
fc=bs.inputs['Emission Strength'].driver_add('default_value');dr=fc.driver;v=dr.variables.new();v.name='touch';v.type='SINGLE_PROP';v.targets[0].id=bpy.data.objects['TP1_ElectronicAssembly'];v.targets[0].data_path='["touch"]';dr.expression='touch*2'

groundmat=material('Studio charcoal',(.032,.043,.055),.1,.5)
cube('Studio_Ground',(0,0,-11.22),(1500,1500,.2),groundmat,'90_Studio',bevel=0)
for name,loc,energy,size in [('Studio_Key',(-85,-90,160),1800000,110),('Studio_Fill',(125,-20,85),1000000,95),('Studio_Rim',(-20,100,145),2000000,80)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);collection('90_Studio').objects.link(ob);ob.location=loc;ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
for name in ('REF_Fill','REF_Softbox'):
    ob=bpy.data.objects.get(name)
    if ob:ob.hide_render=True
scene=bpy.context.scene
world=scene.world or bpy.data.worlds.new('Studio World');scene.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.12,.16,.21,1);bg.inputs['Strength'].default_value=.25
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU'
scene.view_settings.view_transform='AgX'
scene.camera=camera('CAM_Hero',(118,-160,165),(0,0,3),143)
scene.render.resolution_x=1400;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'renders/direct_06_materials_lights.png')
save('direct_06_materials_lights.blend')
bpy.ops.render.render(write_still=True)
result={'render':scene.render.filepath,'engine':scene.render.engine,'device':scene.cycles.device}
