"""OpenMicroKbd controls. Run in Blender Text Editor, or install as a local add-on.

Uses the existing rig's properties. Does not build, reparent, or replace geometry.
"""
import bpy

bl_info = {
    'name': 'OpenMicroKbd Controls',
    'author': 'OpenMicroKbd modeling project',
    'version': (1, 0, 0),
    'blender': (5, 1, 0),
    'location': '3D View > Sidebar > OpenMicroKbd',
    'description': 'Individual keys, encoder, joystick, lighting and exploded view',
    'category': '3D View',
}

KEYS = (
    (3, '星形'), (4, '笑脸'), (8, '透明 1'), (9, '透明 2'),
    (10, '透明 3'), (11, '透明 4'), (12, '四方格'), (13, '对勾'),
    (14, '叉号'), (15, '终端'), (5, '麦克风'), (6, '礼花'), (7, '直升机'),
)

def available_controls():
    for number in range(3, 16):
        obj = bpy.data.objects.get(f'CTRL_SW{number:02d}')
        if obj is not None and 'press' in obj:
            yield obj, ('press',)
    for name, fields in (
        ('CTRL_Encoder', ('rotation_deg', 'press')),
        ('CTRL_Joystick', ('tilt_x_deg', 'tilt_y_deg', 'press')),
        ('CTRL_LEDs', ('brightness', 'color')),
        ('TP1_ElectronicAssembly', ('touch',)),
        ('OMK_ROOT_CTRL', ('explode',)),
    ):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            existing = tuple(field for field in fields if field in obj)
            if existing:
                yield obj, existing

def refresh(context):
    context.view_layer.update()
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

def draw_property(layout, obj, field, label, slider=False):
    if obj is not None and field in obj:
        layout.prop(obj, f'["{field}"]', text=label, slider=slider)

class OMK_OT_toggle_key(bpy.types.Operator):
    bl_idname = 'omk.toggle_key'
    bl_label = '按下 / 松开'
    bl_description = '切换这个按键的按下状态'
    bl_options = {'REGISTER', 'UNDO'}
    target: bpy.props.StringProperty()

    def execute(self, context):
        allowed = {f'CTRL_SW{i:02d}' for i in range(3, 16)}
        if self.target not in allowed:
            return {'CANCELLED'}
        obj = bpy.data.objects.get(self.target)
        if obj is None or 'press' not in obj:
            self.report({'WARNING'}, '未找到按键控制')
            return {'CANCELLED'}
        obj['press'] = 0.0 if float(obj['press']) >= 0.5 else 1.0
        obj.update_tag()
        refresh(context)
        return {'FINISHED'}

class OMK_OT_reset_controls(bpy.types.Operator):
    bl_idname = 'omk.reset_controls'
    bl_label = '全部复位'
    bl_description = '恢复所有按键、旋钮、摇杆、解构和灯光的默认姿态；保留动画关键帧'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_demo(context, False)
        for obj, fields in available_controls():
            for field in fields:
                if field in ('press', 'rotation_deg', 'tilt_x_deg', 'tilt_y_deg', 'explode', 'touch'):
                    obj[field] = 0.0
                else:
                    metadata = obj.id_properties_ui(field).as_dict()
                    if 'default' in metadata:
                        obj[field] = metadata['default']
                    elif field == 'brightness':
                        obj[field] = 1.0
            obj.update_tag()
        refresh(context)
        return {'FINISHED'}

def set_demo(context, enabled):
    for obj in bpy.data.objects:
        if obj.animation_data:
            for track in obj.animation_data.nla_tracks:
                if track.name == 'OpenMicroKbd Demo':
                    track.mute = not enabled
    context.scene['omk_demo_enabled'] = enabled
    cam = bpy.data.objects.get('CAM_Demo' if enabled else 'CAM_Hero')
    if cam:context.scene.camera = cam
    if not enabled and context.screen and context.screen.is_animation_playing:
        bpy.ops.screen.animation_cancel(restore_frame=False)

class OMK_OT_demo(bpy.types.Operator):
    bl_idname = 'omk.demo'
    bl_label = '播放 / 停止示范'
    bl_description = '播放按键、旋钮、摇杆、灯光与分层示范；停止后回到手动控制'
    def execute(self, context):
        enabled = not context.scene.get('omk_demo_enabled', False)
        set_demo(context, enabled)
        if enabled:
            context.scene.frame_set(1)
            if context.screen and not context.screen.is_animation_playing:bpy.ops.screen.animation_play()
        else:bpy.ops.omk.reset_controls()
        refresh(context)
        return {'FINISHED'}

class OMK_OT_keyframe_controls(bpy.types.Operator):
    bl_idname = 'omk.keyframe_controls'
    bl_label = '记录当前姿态'
    bl_description = '在当前帧为所有已有交互控制添加关键帧'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        total = 0
        for obj, fields in available_controls():
            for field in fields:
                obj.keyframe_insert(data_path=f'["{field}"]', frame=context.scene.frame_current,
                                    group='OpenMicroKbd')
                total += 1
        self.report({'INFO'}, f'已记录 {total} 项控制')
        return {'FINISHED'}

class OMK_PT_controls(bpy.types.Panel):
    bl_label = 'OpenMicroKbd'
    bl_idname = 'OMK_PT_controls'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'OpenMicroKbd'

    @classmethod
    def poll(cls, context):
        return bpy.data.objects.get('CTRL_SW03') is not None

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator('omk.reset_controls', icon='LOOP_BACK')
        row.operator('omk.keyframe_controls', text='记录姿态', icon='KEY_HLT')
        layout.operator('omk.demo', icon='PLAY', depress=context.scene.get('omk_demo_enabled', False))
        box = layout.box()
        box.label(text='按键')
        for number, label in KEYS:
            obj = bpy.data.objects.get(f'CTRL_SW{number:02d}')
            if obj is None or 'press' not in obj:
                continue
            row = box.row(align=True)
            active = float(obj['press']) >= 0.5
            button = row.operator('omk.toggle_key', text=label, depress=active)
            button.target = obj.name
            draw_property(row, obj, 'press', '行程', slider=True)
        obj = bpy.data.objects.get('CTRL_Encoder')
        if obj is not None:
            box = layout.box()
            box.label(text='旋钮')
            draw_property(box, obj, 'rotation_deg', '旋转角度')
            draw_property(box, obj, 'press', '按下', slider=True)
        obj = bpy.data.objects.get('CTRL_Joystick')
        if obj is not None:
            box = layout.box()
            box.label(text='摇杆')
            draw_property(box, obj, 'tilt_x_deg', 'X 轴倾角')
            draw_property(box, obj, 'tilt_y_deg', 'Y 轴倾角')
            draw_property(box, obj, 'press', '按下', slider=True)
        obj = bpy.data.objects.get('CTRL_LEDs')
        if obj is not None:
            box = layout.box()
            box.label(text='灯光')
            draw_property(box, obj, 'brightness', '亮度', slider=True)
            draw_property(box, obj, 'color', '颜色')
        obj = bpy.data.objects.get('TP1_ElectronicAssembly')
        if obj is not None:
            box = layout.box()
            box.label(text='触摸区演示')
            draw_property(box, obj, 'touch', '触摸反馈', slider=True)
        obj = bpy.data.objects.get('OMK_ROOT_CTRL')
        if obj is not None and 'explode' in obj:
            box = layout.box()
            box.label(text='分层展示')
            draw_property(box, obj, 'explode', '解构', slider=True)

CLASSES = (OMK_OT_toggle_key, OMK_OT_reset_controls, OMK_OT_demo, OMK_OT_keyframe_controls, OMK_PT_controls)

def unregister():
    for cls in reversed(CLASSES):
        registered = getattr(bpy.types, cls.__name__, None)
        if registered is not None:
            bpy.utils.unregister_class(registered)

def register():
    unregister()
    for cls in CLASSES:
        bpy.utils.register_class(cls)

if __name__ == '__main__':
    register()
