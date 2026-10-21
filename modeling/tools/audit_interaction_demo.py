import bpy,sys,json,math
from mathutils import Vector
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
from model_helpers import *
import keyboard_controls as ui
ui.set_demo(bpy.context,False);bpy.ops.omk.reset_controls();bpy.context.view_layer.update()
caps=[bpy.data.objects[f'SW{i:02d}_Cap'] for i in range(3,16)]
keys=[]
for num in range(3,16):
    before={o.name:o.matrix_world.translation.copy() for o in caps}
    op=bpy.ops.omk.toggle_key(target=f'CTRL_SW{num:02d}')
    bpy.context.view_layer.update()
    delta={o.name:list(o.matrix_world.translation-before[o.name]) for o in caps}
    expected=f'SW{num:02d}_Cap'
    ok=all(abs(d[2]-(-3.2 if n==expected else 0))<.001 and abs(d[0])+abs(d[1])<.001 for n,d in delta.items())
    keys.append({'key':num,'operator':list(op),'pass':ok,'pressed_delta_mm':delta[expected]})
    bpy.ops.omk.toggle_key(target=f'CTRL_SW{num:02d}')
root=bpy.data.objects['OMK_ROOT_CTRL'];enc=bpy.data.objects['CTRL_Encoder'];joy=bpy.data.objects['CTRL_Joystick'];led=bpy.data.objects['CTRL_LEDs']
baseline={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='MESH' and not o.hide_render}
enc['rotation_deg']=120.;enc['press']=1.;enc.update_tag();joy['tilt_x_deg']=23.;joy['tilt_y_deg']=23.;joy['press']=1.;joy.update_tag();root['explode']=1.;root.update_tag()
led['brightness']=1.;led['color']=[1.,.1,.02];led.update_tag();bpy.context.view_layer.update()
manual={'encoder_rotation_deg':math.degrees(bpy.data.objects['EC11_RotationPivot'].rotation_euler.z),'encoder_press_mm':bpy.data.objects['EC11_PressSlide'].location.z,'joystick_axis_deg':[math.degrees(bpy.data.objects['RKJXV_X_GimbalPivot'].rotation_euler.x),math.degrees(bpy.data.objects['RKJXV_Y_GimbalPivot'].rotation_euler.y)],'led_energy':bpy.data.lights['LED1_Light'].energy,'led_color':list(bpy.data.lights['LED1_Light'].color)}
bpy.ops.omk.reset_controls();bpy.context.view_layer.update()
reset=max(max(abs(o.matrix_world[i][j]-baseline[o.name][i][j]) for i in range(4) for j in range(4)) for o in bpy.data.objects if o.name in baseline)

ui.set_demo(bpy.context,True);snapshots=[]
for fr in (1,14,104,113,150,174,196,220,285,360):
    bpy.context.scene.frame_set(fr);bpy.context.view_layer.update()
    snapshots.append({'frame':fr,'star_press':bpy.data.objects['CTRL_SW03']['press'],'encoder_deg':enc['rotation_deg'],'encoder_press':enc['press'],'joystick':[joy['tilt_x_deg'],joy['tilt_y_deg'],joy['press']],'explode':root['explode'],'pcb_world_z':bpy.data.objects['PCB_Main'].matrix_world.translation.z,'led_color':list(led['color'])})
ui.set_demo(bpy.context,False);bpy.context.scene.frame_set(1);bpy.ops.omk.reset_controls()
drivers=[]
for datablocks in (bpy.data.objects,bpy.data.lights):
    for ob in datablocks:
        if ob.animation_data:
            drivers.extend({'id':ob.name,'path':f.data_path,'valid':f.driver.is_valid} for f in ob.animation_data.drivers)
report={'keys':keys,'manual_controls':manual,'reset_max_matrix_error':reset,'demo_snapshots':snapshots,'invalid_drivers':[x for x in drivers if not x['valid']],'scope':'Operators, evaluated transforms, animation sample frames and light data. Does not substitute for rendered motion and GUI review.'}
(ROOT/'references/interaction_demo_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
save('direct_08_interaction_verified.blend')
result=report
