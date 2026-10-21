"""Run through the official Blender MCP in the AcidAlloy source file.

Samples the existing DEMO_OMK_ROOT_CTRL at frames 240..285. Creates an
independent export scene; never saves or overwrites the source .blend.
"""
import bpy
import json
import re
import struct
import zipfile
import shutil
import tempfile
from pathlib import Path
from collections import defaultdict
from mathutils import Matrix, Vector
import numpy as np

BASE = Path(r'C:\Users\myw\Documents\ChatGPT\硬件')
OUT = BASE / 'website/public/assets'
DOWNLOADS = BASE / 'website/public/downloads'
OUT.mkdir(parents=True, exist_ok=True)
DOWNLOADS.mkdir(parents=True, exist_ok=True)
EXPORT_FILE = Path(tempfile.gettempdir())/'acid-alloy-hardware.glb'
source = bpy.data.objects['OMK_ROOT_CTRL'].users_scene[0]
bpy.context.window.scene = source
source_frame = source.frame_current
root = bpy.data.objects['OMK_ROOT_CTRL']
root_value = root['explode']
tracks = [(t, t.mute) for t in root.animation_data.nla_tracks]
def invisible_ink(o):
    materials = list(getattr(o.data, 'materials', []))
    return bool(materials) and all(m and m.use_nodes and
        any(n.type == 'BSDF_TRANSPARENT' for n in m.node_tree.nodes) and
        not any(n.type == 'BSDF_PRINCIPLED' for n in m.node_tree.nodes) for m in materials)

objects = [o for o in source.objects if o.type in {'MESH', 'CURVE', 'FONT'} and not invisible_ink(o)
           and not o.hide_render and not any(c.name in {'90_Studio', '99_SourceReferences'} for c in o.users_collection)]

def ancestors(o):
    names = [o.name]
    while o.parent:
        o = o.parent
        names.append(o.name)
    return names

def category(o):
    chain = ancestors(o)
    names = ' '.join(chain)
    cols = {c.name for c in o.users_collection}
    if o.name == 'AA_CoverPanel': return 'panel', 'panel'
    if o.name == 'Housing_Shell_V1': return 'enclosure', 'enclosure'
    if '04_Keycaps' in cols:
        match = re.search(r'SW\d+', o.name)
        return 'keycaps', 'keycap_' + (match.group() if match else 'other')
    if 'Encoder_KnobDetach' in chain: return 'knob', 'knob'
    if 'Joystick_CapDetach' in chain: return 'joystickCap', 'joystickCap'
    if 'TP1_ElectronicAssembly' in chain: return 'touch', 'touch'
    if '08_LEDs' in cols: return 'lighting', 'lighting'
    if '03_Switches' in cols:
        match = re.search(r'SW\d+', names)
        return 'switches', 'switch_' + (match.group() if match else 'other')
    if '05_Encoder' in cols: return 'encoder', 'encoder'
    if '06_Joystick' in cols: return 'joystick', 'joystick'
    if any(n.startswith('Fastener_Assembly') for n in chain): return 'fasteners', 'fasteners'
    return 'pcb', 'pcb'

def evaluate():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    return {o.name: o.evaluated_get(dg).matrix_world.copy() for o in objects}

# Read the original curve directly: the saved demo NLA strip has influence zero.
action = bpy.data.actions['DEMO_OMK_ROOT_CTRL']
curve = next(f for layer in action.layers for strip in layer.strips
             for bag in strip.channelbags for f in bag.fcurves if f.data_path == '["explode"]')
root['explode'] = 0.0
curve.update_autoflags(root)  # The saved integer flag otherwise quantizes explode to 0/1.
source.frame_set(240)
root['explode'] = 0.0
root.update_tag()
rest = evaluate()
samples = []
for frame in range(240, 286):
    root['explode'] = float(curve.evaluate(frame))
    root.update_tag()
    samples.append((frame - 239, float(root['explode']), evaluate()))
for track, muted in tracks: track.mute = muted
source.frame_set(source_frame)
root['explode'] = 0.0
root.update_tag()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

# Merge only surfaces which share both semantic identity and identical rig motion.
groups = defaultdict(list)
for o in objects:
    part, name = category(o)
    delta = samples[-1][2][o.name].translation - rest[o.name].translation
    key = (part, name, tuple(round(v, 4) for v in delta))
    groups[key].append(o)

material_cache = {}
def web_material(mat):
    if mat is None: return None
    if mat.name in material_cache: return material_cache[mat.name]
    copy = mat.copy()
    copy.name = 'WEB_' + mat.name
    material_cache[mat.name] = copy
    if not copy.use_nodes: return copy
    nodes = copy.node_tree.nodes
    principal = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    mix = next((n for n in nodes if n.type == 'MIX_RGB'), None)
    tex = next((n for n in nodes if n.type == 'TEX_IMAGE' and n.image), None)
    if principal and mix and tex:
        # Blender's glTF exporter cannot represent this alpha-over MIX_RGB chain.
        # Composite its exact base colour and print into a portable base-colour map.
        w, h = tex.image.size
        pixels = np.empty(w*h*4, dtype=np.float32)
        tex.image.pixels.foreach_get(pixels)
        pixels = pixels.reshape((h, w, 4))
        if principal.inputs['Transmission Weight'].is_linked:
            mask = bpy.data.images.new('WEB_TRANSMISSION_' + tex.image.name, width=w, height=h, alpha=True)
            mask.colorspace_settings.name = 'Non-Color'
            values = np.ones_like(pixels)
            values[:, :, :3] = 1-pixels[:, :, 3:4]
            mask.pixels.foreach_set(values.ravel())
            mask.pack()
            mask_node = nodes.new('ShaderNodeTexImage')
            mask_node.image = mask
            vector_link = next((l for l in copy.node_tree.links if l.to_node == tex and l.to_socket.name == 'Vector'),None)
            if vector_link: copy.node_tree.links.new(vector_link.from_socket,mask_node.inputs['Vector'])
            copy.node_tree.links.new(mask_node.outputs['Color'],principal.inputs['Transmission Weight'])
        base = np.array(mix.inputs[1].default_value[:3])
        base = np.where(base <= .0031308, base*12.92, 1.055*np.power(base, 1/2.4)-.055)
        alpha = pixels[:, :, 3:4]
        pixels[:, :, :3] = pixels[:, :, :3]*alpha + base*(1-alpha)
        pixels[:, :, 3] = 1
        image = bpy.data.images.new('WEB_' + tex.image.name, width=w, height=h, alpha=True)
        image.colorspace_settings.name = 'sRGB'
        image.pixels.foreach_set(pixels.ravel())
        image.pack()
        tex.image = image
        copy.node_tree.links.new(tex.outputs['Color'], principal.inputs['Base Color'])
    return copy

web = bpy.data.scenes.new('AcidAlloy_Web_Export')
web.unit_settings.system = 'NONE'
web.frame_start = 1
web.frame_end = 46
web.render.fps = 30
exported = []
report_groups = []
try:
    # Evaluated meshes preserve bevels, UV maps, material slots, and all original surfaces.
    for index, ((part, name, delta), members) in enumerate(groups.items()):
        copies = []
        for original in members:
            evaluated = original.evaluated_get(dg)
            mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=dg)
            if not len(mesh.vertices):
                bpy.data.meshes.remove(mesh)
                continue
            mesh.transform(Matrix.Scale(.02, 4) @ rest[original.name])
            for slot in range(len(mesh.materials)):
                if mesh.materials[slot]: mesh.materials[slot] = web_material(mesh.materials[slot])
            item = bpy.data.objects.new('WEB_SURFACE_' + original.name, mesh)
            web.collection.objects.link(item)
            copies.append(item)
        if not copies: continue
        if len(copies) > 1:
            with bpy.context.temp_override(scene=web, view_layer=web.view_layers[0], active_object=copies[0], object=copies[0], selected_objects=copies, selected_editable_objects=copies):
                bpy.ops.object.join()
        item = copies[0]
        item.data.validate(verbose=False)
        item.name = name + ('_underside' if name in {'pcb', 'lighting'} and delta[2] < 25 else '')
        item['part'] = part
        item['sourceObjects'] = len(members)
        vertices = [v.co for v in item.data.vertices]
        lo = Vector([min(v[a] for v in vertices) for a in range(3)])
        hi = Vector([max(v[a] for v in vertices) for a in range(3)])
        center = (lo + hi)*.5
        item.data.transform(Matrix.Translation(-center))
        for frame, amount, matrices in samples:
            offset = (matrices[members[0].name].translation - rest[members[0].name].translation)*.02
            item.location = center + offset
            item.keyframe_insert(data_path='location', frame=frame)
        exported.append(item)
        report_groups.append({'name':item.name, 'part':part, 'sources':len(members), 'vertices':len(item.data.vertices), 'delta_mm':list(delta)})
    bpy.context.window.scene = web
    with bpy.context.temp_override(scene=web, view_layer=web.view_layers[0]):
        web.frame_set(1)
        bpy.ops.export_scene.gltf(filepath=str(EXPORT_FILE), export_format='GLB',
            use_active_scene=True, export_extras=True, export_animations=True,
            export_animation_mode='SCENE', export_frame_range=True, export_force_sampling=True,
            export_optimize_animation_size=True, export_cameras=False, export_lights=False,
            export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
            export_draco_position_quantization=16, export_draco_normal_quantization=10,
            export_draco_texcoord_quantization=12,
            export_yup=True, export_image_format='AUTO')
    # Blender emits one clip per object; combine their synchronized channels losslessly.
    path = EXPORT_FILE
    binary = path.read_bytes()
    json_length = struct.unpack_from('<I', binary, 12)[0]
    document = json.loads(binary[20:20+json_length])
    animation = {'name':'HardwareExplode','channels':[],'samplers':[]}
    for clip in document.get('animations', []):
        offset = len(animation['samplers'])
        animation['samplers'].extend(clip['samplers'])
        for channel in clip['channels']:
            channel['sampler'] += offset
            animation['channels'].append(channel)
    document['animations'] = [animation]
    encoded = json.dumps(document,separators=(',',':')).encode('utf-8')
    encoded += b' ' * ((-len(encoded)) % 4)
    tail = binary[20+json_length:]
    path.write_bytes(struct.pack('<III',0x46546C67,2,20+len(encoded)+len(tail)) +
                     struct.pack('<II',len(encoded),0x4E4F534A) + encoded + tail)
    shutil.copyfile(path, OUT/'keyboard-exploded.glb')
    bpy.context.window.scene = source
    # Print meshes come from the actual supplied model, in millimetres, without ink geometry.
    def stl(obj_name, filename):
        o = bpy.data.objects[obj_name]
        mesh = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
        mesh.transform(rest[obj_name])
        bounds = [v.co for v in mesh.vertices]
        shift = Vector([(min(v.x for v in bounds)+max(v.x for v in bounds))*.5,
                        (min(v.y for v in bounds)+max(v.y for v in bounds))*.5,
                        min(v.z for v in bounds)])
        mesh.transform(Matrix.Translation(-shift))
        mesh.calc_loop_triangles()
        with (DOWNLOADS/filename).open('wb') as stream:
            stream.write(b'AcidAlloy Blender source mesh; units=mm'.ljust(80,b' '))
            stream.write(struct.pack('<I', len(mesh.loop_triangles)))
            for tri in mesh.loop_triangles:
                vals = list(tri.normal) + [a for vi in tri.vertices for a in mesh.vertices[vi].co]
                stream.write(struct.pack('<12fH', *vals, 0))
        bpy.data.meshes.remove(mesh)
    caps = []
    for num in range(3,16):
        filename = f'acid-alloy-keycap-SW{num:02d}.stl'
        stl(f'SW{num:02d}_Cap', filename)
        caps.append(filename)
    stl('AA_CoverPanel', 'acid-alloy-panel.stl')
    stl('OpenMicroRotator_SourceMesh', 'acid-alloy-knob.stl')
    stl('OpenMicroJoystickCap_SourceMesh', 'acid-alloy-joystick-cap.stl')
    readme = 'Units: millimetres. Exported from OpenMicroKbd_AcidAlloy.blend, evaluated mesh at rest.\n13 keycaps SW03-SW15. STL contains geometry only, without printed graphics or colours.\nThese are source model exports. Check slicing, wall thickness and fit before printing.\n'
    with zipfile.ZipFile(DOWNLOADS/'acid-alloy-keycaps.zip','w',zipfile.ZIP_DEFLATED) as z:
        for filename in caps: z.write(DOWNLOADS/filename, filename)
        z.writestr('README.txt', readme)
        z.write(BASE/'openmicrokbd-review/LICENSE', 'LICENSE.txt')
    fab = BASE/'openmicrokbd-review/hw/v1/fab'
    for name in ['openmicro-gerbers.zip','openmicro-bom.csv','openmicro-smt.csv']:
        shutil.copyfile(fab/name, DOWNLOADS/name)
    shutil.copyfile(BASE/'openmicrokbd-review/hw/v1/mechanical/OpenMicroKbkCase.3mf', DOWNLOADS/'OpenMicroKbkCase.3mf')
    shutil.copyfile(BASE/'openmicrokbd-review/LICENSE', DOWNLOADS/'LICENSE.txt')
    with zipfile.ZipFile(DOWNLOADS/'openmicro-pcb-fabrication.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ['openmicro-gerbers.zip','openmicro-bom.csv','openmicro-smt.csv','README.md']:
            z.write(fab/name, name)
        z.write(BASE/'openmicrokbd-review/LICENSE', 'LICENSE.txt')
    report = {'source':bpy.data.filepath, 'animation_source':'DEMO_OMK_ROOT_CTRL, frames 240..285',
              'clip':'HardwareExplode', 'frames':46, 'source_objects':len(objects), 'groups':report_groups,
              'samples':[{'frame':f, 'explode':a} for f,a,_ in samples],
              'glb_bytes':(OUT/'keyboard-exploded.glb').stat().st_size,
              'downloads':[p.name for p in DOWNLOADS.iterdir()]}
    (BASE/'modeling/references/hardware_web_export.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    result = report
finally:
    bpy.context.window.scene = source
    source.frame_set(source_frame)
    root['explode'] = root_value
    root.update_tag()
    bpy.context.view_layer.update()
