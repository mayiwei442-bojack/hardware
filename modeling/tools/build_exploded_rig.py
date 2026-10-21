import bpy,sys,json
from mathutils import Matrix
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
from model_helpers import *
root=bpy.data.objects['OMK_ROOT_CTRL'];root['explode']=0.0
root.id_properties_ui('explode').update(min=0,max=1,description='0 assembled; 1 layered exploded view')
bpy.context.view_layer.update()
before={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type in {'MESH','CURVE','FONT','LIGHT'}}
def layer(name,offset,parent=root):
    ob=empty(name,coll='10_Rig');keep_parent(ob,parent)
    fc=ob.driver_add('location',2);d=fc.driver;d.type='SCRIPTED'
    v=d.variables.new();v.name='amount';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["explode"]'
    d.expression=f'{offset}*amount'
    ob['exploded_offset_mm']=offset;return ob
pcb=layer('LAYER_02_PCB',38)
bottom=layer('LAYER_01_UndersideElectronics',18)
switch=layer('LAYER_03_SwitchMechanisms',65)
screws=layer('LAYER_05_Fasteners',115)
keep_parent(bpy.data.objects['Housing_Shell_V1'],root)
for o in list(bpy.data.collections['02_PCB'].objects):
    if o.parent is None:keep_parent(o,pcb)
for o in list(bpy.data.objects):
    if o.name.endswith('_ElectronicAssembly'):
        keep_parent(o,bottom if o.get('pcb_side')=='B.Cu' else pcb)
    elif o.name.startswith('Fastener_Assembly_'):keep_parent(o,screws)
keep_parent(bpy.data.objects['J3_USB_C_Assembly'],bottom)
keep_parent(bpy.data.objects['SW01_MechanicalAssembly'],switch)
keep_parent(bpy.data.objects['J01_MechanicalAssembly'],switch)
for num in range(3,16):
    ref=f'SW{num:02d}';keep_parent(bpy.data.objects[ref+'_Assembly'],switch)
    caplayer=layer(ref+'_CapDetach',30,bpy.data.objects[ref+'_KeyMotion'])
    # Its local rest transform must be identity, regardless of the parent assembly origin.
    caplayer.location=(0,0,0)
    for o in list(bpy.data.collections['04_Keycaps'].objects):
        if o.name.startswith(ref+'_'):keep_parent(o,caplayer)
for part,pivot,name in (('keyboardRotator_SourceMesh','EC11_PressSlide','Encoder_KnobDetach'),('keyboardJoystickCap_SourceMesh','RKJXV_PressMotion','Joystick_CapDetach')):
    offset=layer(name,30,bpy.data.objects[pivot]);offset.location=(0,0,0)
    keep_parent(bpy.data.objects[part],offset)
# Shaft follows axial press as well as both gimbal rotations.
stem=bpy.data.objects.get('RKJXV_Stem')
if stem:keep_parent(stem,bpy.data.objects['RKJXV_PressMotion'])
keep_parent(bpy.data.objects['CTRL_LEDs'],root)
bpy.context.view_layer.update()
errors={n:max(abs(before[n][i][j]-bpy.data.objects[n].matrix_world[i][j]) for i in range(4) for j in range(4)) for n in before}
changed={k:v for k,v in errors.items() if v>.001}
root['explode']=1;root.update_tag();bpy.context.view_layer.update()
review_render('direct_05_exploded.png',camera('AUDIT_Exploded',(150,-235,178),(0,0,48),205),(1500,1600))
root['explode']=0;root.update_tag();bpy.context.view_layer.update()
reset={n:max(abs(before[n][i][j]-bpy.data.objects[n].matrix_world[i][j]) for i in range(4) for j in range(4)) for n in before}
report={'rest_transform_changes':changed,'round_trip_max_matrix_error':max(reset.values()),'layer_offsets':{o.name:o['exploded_offset_mm'] for o in bpy.data.objects if 'exploded_offset_mm' in o},'object_count':len(before)}
(ROOT/'references/exploded_rig_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
save('direct_05_exploded_rig.blend')
result=report
