import bpy,json,math,sys
from mathutils import Matrix
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
import importlib, model_helpers
importlib.reload(model_helpers)
from model_helpers import *

steel=material('OMK Brushed stainless',(.52,.57,.60),.82,.26)
black=material('OMK Connector polymer',(.009,.013,.018),0,.38)
gold=material('OMK Contact gold',(.65,.37,.095),.82,.25)
potmat=material('OMK Potentiometer casing',(.018,.054,.04),0,.44)
source=json.loads((ROOT/'references/source_inventory.json').read_text(encoding='utf-8'))
fps={p['reference']:p for p in source['pcb']['footprints']}

# Replace generated connector proxies; original board and original CAD remain intact.
usb=bpy.data.objects['J3_USB_C_Assembly']
remove_generated([o.name for o in list(usb.children) if o.type=='MESH'])
usb.location=(0,45.64,-1.63)
can=capsule_tube('J03_USB_C_MetalShell',8.94,3.26,8.34,2.56,42.45,49.78,-1.63,steel,'07_Electronics',usb)
can['source']='HRO TYPE-C-31-M-12 drawing; 8.94mm shell width, 3.26mm height'
cube('J03_USB_C_RearInsulator',(0,42.8,-1.63),(8.22,.65,2.50),black,'07_Electronics',usb,.18)
cube('J03_USB_C_Tongue',(0,47.0,-1.63),(6.65,4.8,.55),black,'07_Electronics',usb,.10)
for side in (-1,1):
    for i in range(8):
        cube(f'J03_USB_C_Contact_{side}_{i+1:02d}',(-2.8+i*.8,48.9,-1.63+side*.292),(.24,1.05,.028),gold,'07_Electronics',usb,.01)
    for y in (42.51,46.69):
        cube(f'J03_USB_C_ShellTab_{side}_{y}',(side*4.32,y,-.65),(.48,1.4,2.1),steel,'07_Electronics',usb,.035)

# Legacy screw children retained absolute coordinates when they were parented.
for assembly in [o for o in bpy.data.objects if o.name.startswith('Fastener_Assembly_')]:
    for o in assembly.children:o.matrix_parent_inverse=assembly.matrix_world.inverted()

# An unsupported decorative inset was accidentally placed twice above the knob.
floating=bpy.data.objects.get('Knob_Top_Inset')
if floating:floating.hide_render=True;floating.hide_viewport=True

# The full package envelope is a reference, not solid material occupying the mechanism.
proxy=bpy.data.objects.get('RKJXV_BaseHousing_18p2x21p7')
if proxy:proxy.hide_render=True;proxy.hide_viewport=True;proxy['role']='Reference envelope only'
joy=empty('J01_MechanicalAssembly',(29.575,29.575,0),'06_Joystick')
for o in list(bpy.data.objects):
    if o.name.startswith('RKJXV_') and o.parent is None and o!=proxy:keep_parent(o,joy)
for name in ('CTRL_Joystick',):
    o=bpy.data.objects.get(name)
    if o and o.parent is None:keep_parent(o,joy)
x=y=29.575
cube('J01_LowerInsulator',(x,y,2.5),(15.6,17.4,1.8),black,'06_Joystick',joy,.35)
for sign in (-1,1):
    cube(f'J01_TopCrossbar_Y_{sign}',(x,y+sign*7.5,11.1),(15.4,1.2,.65),steel,'06_Joystick',joy,.13)
    cube(f'J01_TopCrossbar_X_{sign}',(x+sign*7.1,y,11.1),(1.2,13.8,.65),steel,'06_Joystick',joy,.13)
    for side in (-1,1):
        cube(f'J01_FrameLeg_{sign}_{side}',(x+sign*7.1,y+side*7.4,7.15),(1.1,1.25,7.3),steel,'06_Joystick',joy,.10)
cube('J01_Potentiometer_X',(x+8.8,y,6.3),(2.5,10.5,6.9),potmat,'06_Joystick',joy,.5)
cube('J01_Potentiometer_Y',(x,y+9.5,6.3),(10.5,2.5,6.9),potmat,'06_Joystick',joy,.5)
cylinder('J01_Pot_X_Rotor',(x+10.15,y,6.3),2.7,.45,black,'06_Joystick',joy,axis='X')
cylinder('J01_Pot_Y_Rotor',(x,y+10.85,6.3),2.7,.45,black,'06_Joystick',joy,axis='Y')
for o in bpy.data.objects:
    if o.name.startswith(('RKJXV_SideRail','RKJXV_EndRail','RKJXV_X_Yoke','RKJXV_Y_Yoke')):
        o.data.materials.clear();o.data.materials.append(steel)

# Rebuild encoder electrical leads on actual KiCad pads rather than visual offsets.
remove_generated([o.name for o in bpy.data.objects if o.name.startswith(('EC11_EncoderTerminal','EC11_SwitchTerminal','EC11_THT_Foot'))])
enc=empty('SW01_MechanicalAssembly',(-28.075,28.575,0),'05_Encoder')
for o in list(bpy.data.objects):
    if o.name.startswith('EC11_') and o.parent is None:keep_parent(o,enc)
for o in (bpy.data.objects.get('CTRL_Encoder'),):
    if o and o.parent is None:keep_parent(o,enc)
for pad in fps['SW1']['pads']:
    at=next(v for v in pad if isinstance(v,list) and v[0]=='at')
    px=-35.575+float(at[1]);py=31.075-float(at[2]);ref=pad[0]
    cylinder(f'SW01_Pad_{ref}_Lead',(px,py,.1),.35 if ref not in ('6','7') else .72,5.2,steel,'05_Encoder',enc,vertices=24)
    if ref in ('1','2','3','4','5'):
        bodyx=-32.4 if px < -28 else -23.7
        cube(f'SW01_Pad_{ref}_Bend',((px+bodyx)/2,py,2.6),(abs(px-bodyx)+.3,.65,.45),steel,'05_Encoder',enc,.055)

bpy.context.view_layer.update()
save('direct_01_connectors_mechanics.blend')
cam=camera('AUDIT_USB_Rear',(0,88,0),(0,46,-1.63),20)
review_render('direct_01_usb_rear.png',cam,(1300,750))
cam=camera('AUDIT_Overview',(110,-160,165),(0,0,4),132)
review_render('direct_01_mechanics_overview.png',cam)
save('direct_01_connectors_mechanics.blend')
result={'usb_shell_world':list(can.matrix_world.translation),'saved':bpy.data.filepath,'renders':['direct_01_usb_rear.png','direct_01_mechanics_overview.png']}
