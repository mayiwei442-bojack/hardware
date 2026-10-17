import bpy, pathlib, hashlib, json
P=pathlib.Path(r'C:\Users\myw\Documents\ChatGPT\硬件\modeling')
D=P/'overclock_instrument'
source=P/'assets/OpenMicroKbd_AcidAlloy.blend'
target=P/'assets/OpenMicroKbd_OverclockInstrument.blend'
assert pathlib.Path(bpy.data.filepath)==source
assert not target.exists(), 'Target already exists; inspect before replacing'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
original_hash=hashlib.sha256((P/'assets/OpenMicroKbd.blend').read_bytes()).hexdigest()
names=list(bpy.data.objects.keys())
bpy.ops.wm.save_as_mainfile(filepath=str(target))
bpy.ops.omk.reset_controls();bpy.context.scene.frame_set(1)
def rgb(h):
 vals=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)
old_images=[]
def style(name,color,rough=.4,metal=0,art=None,newname=None):
 m=bpy.data.materials[name];nt=m.node_tree
 m.diffuse_color=(*rgb(color),1)
 bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=(*rgb(color),1)
 bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 for n in nt.nodes:
  if n.type=='MIX_RGB':n.inputs[1].default_value=(*rgb(color),1)
  if n.type=='TEX_IMAGE' and art:
   old_images.append(n.image)
   n.image=bpy.data.images.load(str(D/'textures'/art),check_existing=True);n.image.pack()
 m.name='OC | '+(newname or name.removeprefix('AA | '))
style('AA | acid yellow-green coating','#e3e9e5',.42,.12,'panel_print.png','ceramic white faceplate')
style('AA | graphite powder coat','#b9b7a9',.48,.12,newname='warm grey enclosure')
style('AA | front typography','#b9b7a9',.48,.12,'case_front_print.png','front instrument nameplate')
style('AA | side typography','#b9b7a9',.48,.12,'case_side_print.png','side signal graphic')
style('AA | satin machined alloy','#263943',.32,.65,'knob_print.png','anodized gain knob')
style('AA | ultraviolet soft-touch','#263943',.48,0,'joystick_print.png','vector joystick')
for sw in range(3,16):
 clear=8<=sw<=11
 color='#ff590f' if sw==3 else '#c0dfdf' if clear else '#263943' if sw in (13,14,15) else '#dfded1'
 style(f'AA | key {sw:02d}',color,.14 if clear else .40,0,f'key_{sw:02d}.png',f'key {sw:02d}')
for im in set(old_images):
 if im.users==0:bpy.data.images.remove(im)
led=bpy.data.objects['CTRL_LEDs'];led['color']=[.08,.8,1.];led['brightness']=.30
led.id_properties_ui('color').update(default=[.08,.8,1.]);led.id_properties_ui('brightness').update(default=.30);led.update_tag()
bpy.context.scene['design_variant']='03 / OVERCLOCK INSTRUMENT'
bpy.context.scene['keyprint_profile']='Codex CODEX_KEYS; same functions as Acid Alloy function_v2'
bpy.context.view_layer.update()
s=bpy.context.scene;s.camera=bpy.data.objects['CAM_Hero']
s.render.resolution_percentage=100;s.render.resolution_x=1800;s.render.resolution_y=1600;s.cycles.samples=96
s.render.filepath=str(D/'renders/01_overclock_hero.png');bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['CAM_final_top'];s.render.resolution_x=1600;s.render.resolution_y=1600
s.render.filepath=str(D/'renders/02_overclock_top.png');bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['CAM_Hero'];s.render.resolution_x=1800;s.render.resolution_y=1600
s.render.filepath=str(D/'renders/01_overclock_hero.png')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(target))
result={'file':str(target),'source_sha256':source_hash,'source_unchanged':source_hash==hashlib.sha256(source.read_bytes()).hexdigest(),'original_sha256':original_hash,'object_count':len(bpy.data.objects),'object_names_preserved':names==list(bpy.data.objects.keys()),'packed_images':len([im for im in bpy.data.images if im.packed_file]),'scope':'Material and surface artwork only; no geometry, parenting, device or interaction changes.'}
(D/'delivery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
