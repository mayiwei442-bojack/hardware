"""Execute through Blender MCP. Records evidence without changing scene controls."""
import bpy
import datetime
import json
import pathlib
import re
from mathutils import Vector

WORK = pathlib.Path(r'C:\Users\myw\Documents\ChatGPT\硬件\modeling')
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene
source = json.loads((WORK/'references/source_inventory.json').read_text(encoding='utf-8-sig'))
footprints = {p['reference']: p for p in source['pcb']['footprints']}

def bounds(obj):
    evaluated = obj.evaluated_get(dg)
    points = [evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]

def object_evidence(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {'exists': False}
    info = {'exists': True, 'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
            'hide_render': obj.hide_render, 'world_position': list(obj.matrix_world.translation)}
    if obj.type == 'MESH':
        info.update(bounds_mm=bounds(obj), original_faces=len(obj.data.polygons),
                    materials=[s.material.name if s.material else None for s in obj.material_slots])
    return info

key_checks = []
for number in range(3, 16):
    ref = f'SW{number}'
    cap_name = f'SW{number:02d}_Cap'
    ctrl_name = f'CTRL_SW{number:02d}'
    info = object_evidence(cap_name)
    control = bpy.data.objects.get(ctrl_name)
    row = {'reference': ref, 'cap': info, 'control_exists': control is not None,
           'press_value': control.get('press') if control else None}
    if info['exists']:
        box = info['bounds_mm']
        center = [(axis[0]+axis[1])/2 for axis in box]
        at = footprints[ref]['at']
        target = (float(at[0]), -float(at[1]))
        row['xy_center_error_mm'] = ((center[0]-target[0])**2+(center[1]-target[1])**2)**0.5
    key_checks.append(row)

invalid_drivers = []
driver_count = 0
for obj in bpy.data.objects:
    if obj.animation_data:
        for curve in obj.animation_data.drivers:
            driver_count += 1
            if not curve.driver.is_valid:
                invalid_drivers.append({'object': obj.name, 'path': curve.data_path, 'index': curve.array_index})

led_names = sorted({m.group(0) for obj in bpy.data.objects
                    for m in [re.search(r'\bLED\d+\b', obj.name.replace('_', ' '))] if m})
usb_names = [obj.name for obj in bpy.data.objects if obj.type == 'MESH' and 'USB' in obj.name]
usb = {name: object_evidence(name) for name in usb_names}
usb_outside_board = [name for name, info in usb.items()
                     if info['bounds_mm'][1][0] > 55 or info['bounds_mm'][1][1] < -55]
report = {
    'observed_at': datetime.datetime.now().astimezone().isoformat(),
    'blend_path': bpy.data.filepath,
    'scene': scene.name,
    'unit_scale_m_per_blender_unit': scene.unit_settings.scale_length,
    'keys': key_checks,
    'key_count_found': sum(row['cap']['exists'] for row in key_checks),
    'key_control_count_found': sum(row['control_exists'] for row in key_checks),
    'drivers': {'count': driver_count, 'invalid': invalid_drivers},
    'identified_led_references': led_names,
    'expected_led_references': [f'LED{i}' for i in list(range(1,9))+list(range(17,30))],
    'usb': usb,
    'usb_far_outside_board': usb_outside_board,
    'pcb': object_evidence('PCB_Main'),
    'housing': object_evidence('Housing_Shell_V1'),
    'joystick_envelope_proxy': object_evidence('RKJXV_BaseHousing_18p2x21p7'),
    'scope': 'Snapshot evidence only. Does not move controls, prove collision-free motion, review images, reopen files, or certify overall completion.',
}
target = WORK/'references/live_scene_audit.json'
target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
result = {'report': str(target), 'keys': report['key_count_found'],
          'key_controls': report['key_control_count_found'],
          'invalid_drivers': invalid_drivers, 'usb_far_outside_board': usb_outside_board,
          'led_refs': led_names}
