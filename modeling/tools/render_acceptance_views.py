import bpy,sys,math
from mathutils import Vector
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
from model_helpers import *
import openmicro_controls as ui
ui.set_demo(bpy.context,False);bpy.ops.omk.reset_controls()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=48
def render(name,cam,size):
    s.camera=cam;s.render.resolution_x=size[0];s.render.resolution_y=size[1];s.render.filepath=str(ROOT/'renders'/name);bpy.ops.render.render(write_still=True)
for name,loc,target,scale,size in [
 ('final_top.png',(0,0,180),(0,0,0),114,(1200,1200)),
 ('final_front.png',(0,-180,8),(0,0,8),120,(1400,650)),
 ('final_right.png',(180,0,8),(0,0,8),120,(1400,650)),
 ('final_rear.png',(0,180,8),(0,0,8),120,(1400,650)),
 ('final_usb.png',(0,90,-1.6),(0,47,-1.6),18,(1100,700))]:
    render(name,camera('CAM_'+name[:-4],loc,target,scale),size)

hidden={}
for cn in ['01_Housing','03_Switches','04_Keycaps','05_Encoder','06_Joystick','09_Fasteners']:
    for ob in bpy.data.collections[cn].objects:hidden[ob.name]=ob.hide_render;ob.hide_render=True
render('final_pcb_top.png',bpy.data.objects['AUDIT_Top'],(1400,1400))
ground=bpy.data.objects['Studio_Ground'];old=ground.hide_render;ground.hide_render=True
data=bpy.data.lights.new('Audit_Underside_Light','AREA');data.energy=200000;data.size=100
ob=bpy.data.objects.new('Audit_Underside_Light',data);collection('90_Studio').objects.link(ob);ob.location=(0,-35,-100);ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
render('final_pcb_bottom.png',bpy.data.objects['AUDIT_Bottom'],(1400,1400))
bpy.data.objects.remove(ob,do_unlink=True);bpy.data.lights.remove(data);ground.hide_render=old
for n,hide in hidden.items():bpy.data.objects[n].hide_render=hide

ui.set_demo(bpy.context,True)
for frame in (14,113,196,220,285):
    s.frame_set(frame);bpy.context.view_layer.update()
    render(f'final_demo_{frame:03d}.png',bpy.data.objects['CAM_Demo'],(1200,1000))
ui.set_demo(bpy.context,False);s.frame_set(1);bpy.ops.omk.reset_controls()
s.camera=bpy.data.objects['CAM_Hero'];s.render.resolution_x=1400;s.render.resolution_y=1200;s.cycles.samples=96
save('direct_10_acceptance_views.blend')
result={'render_count':12,'reset':True}
