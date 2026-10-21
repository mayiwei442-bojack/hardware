import bpy,sys,json
from mathutils import Vector
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
from model_helpers import *
import keyboard_controls as ui
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=360;scene.render.fps=30
ui.set_demo(bpy.context,False);bpy.ops.omk.reset_controls()
def k(obj,prop,frame,value):
    obj[prop]=value;obj.keyframe_insert(data_path=f'["{prop}"]',frame=frame,group='keyboard Demo')
for obj,fields in ui.available_controls():
    for prop in fields:
        value=obj[prop]
        if hasattr(value,'to_list'):value=value.to_list()
        k(obj,prop,1,value);k(obj,prop,360,value)
for index,(num,label) in enumerate(ui.KEYS):
    obj=bpy.data.objects[f'CTRL_SW{num:02d}'];start=12+index*5
    for fr,v in ((start,0),(start+2,1),(start+4,0)):k(obj,'press',fr,v)
enc=bpy.data.objects['CTRL_Encoder']
for fr,v in ((82,0),(102,120),(118,-60),(135,0)):k(enc,'rotation_deg',fr,v)
for fr,v in ((109,0),(113,1),(119,0)):k(enc,'press',fr,v)
joy=bpy.data.objects['CTRL_Joystick']
for fr,x,y,p in ((140,0,0,0),(150,23,0,0),(162,-23,0,0),(174,0,23,0),(186,0,-23,0),(196,16,16,1),(207,0,0,0)):
    for prop,val in [('tilt_x_deg',x),('tilt_y_deg',y),('press',p)]:k(joy,prop,fr,val)
touch=bpy.data.objects['TP1_ElectronicAssembly']
for fr,v in ((209,0),(213,1),(218,0)):k(touch,'touch',fr,v)
led=bpy.data.objects['CTRL_LEDs']
for fr,color,bright in ((210,[.015,.5,1.],.65),(220,[1.,.08,.015],.9),(229,[.2,1.,.05],.75),(239,[.015,.5,1.],.65)):
    k(led,'color',fr,color);k(led,'brightness',fr,bright)
root=bpy.data.objects['OMK_ROOT_CTRL']
for fr,v in ((240,0),(285,1),(315,1),(355,0)):k(root,'explode',fr,v)
cam=camera('CAM_Demo',(118,-160,165),(0,0,3),143);cam.data.type='PERSP';cam.data.lens=50
for fr,loc,target in ((1,(118,-160,165),(0,0,3)),(235,(118,-160,165),(0,0,3)),(285,(165,-240,210),(0,0,48)),(315,(165,-240,210),(0,0,48)),(355,(118,-160,165),(0,0,3)),(360,(118,-160,165),(0,0,3))):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.keyframe_insert(data_path='location',frame=fr);cam.keyframe_insert(data_path='rotation_euler',frame=fr)
objects=[obj for obj,fields in ui.available_controls()]+[cam]
for obj in objects:
    ad=obj.animation_data;action=ad.action
    action.name='DEMO_'+obj.name
    track=ad.nla_tracks.new();track.name='keyboard Demo'
    strip=track.strips.new(action.name,1,action)
    if action.slots and hasattr(strip,'action_slot'):strip.action_slot=action.slots[0]
    strip.blend_type='REPLACE';strip.extrapolation='NOTHING';track.mute=True
    ad.action=None
for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for fr,name in ((1,'REST'),(12,'13 KEYS'),(82,'ENCODER'),(140,'JOYSTICK'),(210,'TOUCH + RGB'),(240,'EXPLODE'),(315,'REASSEMBLE')):scene.timeline_markers.new(name,frame=fr)
ui.set_demo(bpy.context,False);scene.frame_set(1);bpy.ops.omk.reset_controls()
scene.camera=bpy.data.objects['CAM_Hero']
save('direct_07_demo_controls.blend')
result={'duration_seconds':12,'animated_objects':len(objects),'demo_tracks_default':'muted for manual interaction','frame_range':[1,360]}
