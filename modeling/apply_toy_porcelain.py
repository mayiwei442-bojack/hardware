import bpy,pathlib,hashlib,json
P=pathlib.Path(r'C:\Users\myw\Documents\ChatGPT\硬件\modeling')
assert variant in ('rebel_toy','electric_porcelain')
toy=variant=='rebel_toy';D=P/variant
source=P/'assets/MacroPad_AcidAlloy.blend'
target=P/'assets'/('MacroPad_RebelToy.blend' if toy else 'MacroPad_ElectricPorcelain.blend')
assert not target.exists(),'Target exists; inspect before overwrite'
assert not bpy.data.is_dirty,'Current scene has unsaved changes'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
names=set(bpy.data.objects.keys())
bpy.ops.wm.save_as_mainfile(filepath=str(target))
bpy.ops.omk.reset_controls();bpy.context.scene.frame_set(1)
def rgb(h):
 vals=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)
old=[]
def style(name,color,art=None,rough=None,metal=0):
 m=bpy.data.materials[name];nt=m.node_tree
 m.diffuse_color=(*rgb(color),1)
 bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=(*rgb(color),1)
 bs.inputs['Roughness'].default_value=rough if rough is not None else (.3 if toy else .21)
 bs.inputs['Metallic'].default_value=metal
 bs.inputs['Coat Weight'].default_value=.22 if toy else .42
 bs.inputs['Coat Roughness'].default_value=.17 if toy else .12
 for n in nt.nodes:
  if n.type=='MIX_RGB':n.inputs[1].default_value=(*rgb(color),1)
  if n.type=='TEX_IMAGE' and art:
   old.append(n.image);n.image=bpy.data.images.load(str(D/'textures'/art),check_existing=True);n.image.pack()
 m.name=('RT | ' if toy else 'EP | ')+name.removeprefix('AA | ')
shell='#7444c5' if toy else '#e4efed'
style('AA | acid yellow-green coating','#ffdf73' if toy else '#edf4f4','panel_print.png')
style('AA | graphite powder coat',shell)
style('AA | front typography',shell,'case_front_print.png')
style('AA | side typography',shell,'case_side_print.png')
style('AA | satin machined alloy','#a5e8b2' if toy else '#123b9b','knob_print.png')
style('AA | ultraviolet soft-touch','#ff7bad' if toy else '#edf4f4','joystick_print.png')
colors={3:'#a5e8b2',4:'#f23b82',5:'#a5e8b2',6:'#7444c5',7:'#ffdf73',8:'#bbdfe1',9:'#e7b8dc',10:'#e4d8a6',11:'#b4e1cc',12:'#ffaf6d',13:'#a5e8b2',14:'#7444c5',15:'#f23b82'}
for sw in range(3,16):
 clear=8<=sw<=11
 color=colors[sw] if toy else '#123b9b' if sw in (3,15) else '#c4e9ef' if clear else '#edf4f4'
 style(f'AA | key {sw:02d}',color,f'key_{sw:02d}.png',rough=.13 if clear else None)
for im in set(old):
 if im.users==0:bpy.data.images.remove(im)
led=bpy.data.objects['CTRL_LEDs'];color=[1.,.25,.5] if toy else [.1,.7,1.]
led['color']=color;led['brightness']=.28
led.id_properties_ui('color').update(default=color);led.id_properties_ui('brightness').update(default=.28);led.update_tag()
s=bpy.context.scene;s['design_variant']='04 / REBEL TOY' if toy else '02 / ELECTRIC PORCELAIN'
bpy.context.view_layer.update()
s.camera=bpy.data.objects['CAM_Hero'];s.render.resolution_percentage=100;s.render.resolution_x=1800;s.render.resolution_y=1600;s.cycles.samples=96
s.render.filepath=str(D/'renders/01_hero.png');bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['CAM_final_top'];s.render.resolution_x=1600;s.render.resolution_y=1600
s.render.filepath=str(D/'renders/02_top.png');bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['CAM_Hero'];s.render.resolution_x=1800;s.render.resolution_y=1600;s.render.filepath=str(D/'renders/01_hero.png')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(target))
result={'file':str(target),'source_sha256':source_hash,'source_unchanged':source_hash==hashlib.sha256(source.read_bytes()).hexdigest(),'object_count':len(bpy.data.objects),'object_names_preserved':names==set(bpy.data.objects.keys()),'packed_images':len([i for i in bpy.data.images if i.packed_file]),'scope':'Only appearance materials, print artwork and manual default light color modified. Geometry and interaction unchanged.'}
(D/'delivery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
