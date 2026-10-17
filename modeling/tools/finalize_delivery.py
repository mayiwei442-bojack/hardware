"""Finalize delivery metadata after manual visual and live Blender review."""
import datetime
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
def read(rel):
    return json.loads((root / rel).read_text(encoding='utf-8-sig'))

struct = read('references/final_structural_audit.json')
interaction = read('references/interaction_demo_audit.json')
reopen = read('references/reopen_audit.json')
clearance = read('references/key_clearance_audit.json')
mechanical = read('references/final_mechanical_pending.json')
rig = read('references/exploded_rig_audit.json')
gui = read('references/gui_click_audit.json')
playback = read('references/playback_audit.json')
assert struct['source_footprint_count'] == len(struct['coverage']) == 88
assert not struct['missing'] and struct['max_xy_error_mm'] < .001
assert not struct['visible_model_objects_outside_root']
assert len(interaction['keys']) == 13 and all(x['pass'] for x in interaction['keys'])
assert interaction['reset_max_matrix_error'] == 0 and not interaction['invalid_drivers']
assert reopen['all_keys_pass'] and reopen['addon_enabled'] and reopen['embedded_control_script']
assert not reopen['missing_libraries'] and not reopen['invalid_drivers']
assert clearance['sample_count'] == 65 and clearance['failing_samples'] == 0
assert mechanical['usb_shell_case_intersections'] == 0
assert all(not x['cap_intersections'] for x in mechanical['joystick'])
assert rig['round_trip_matrix_max_error'] == 0 and rig['layer_drivers_valid']
assert gui['mouse_clicked_star_press'] == 1
assert playback['advanced_frame'] > 1 and not playback['playing_after_stop']

final_views = ['hero','night','exploded','top','front','right','rear','usb',
               'pcb_top','pcb_bottom','demo_014','demo_113','demo_196',
               'demo_220','demo_285','controls_ui_pressed']
direct_views = ['01_usb_rear','01_mechanics_overview','02_electronics_top',
                '02_electronics_bottom','03_key_pressed','05_exploded',
                '06_materials_lights_corrected','06_lights_apertures']
renders = [f'renders/final_{v}.png' for v in final_views]
renders += [f'renders/direct_{v}.png' for v in direct_views]
required = ['assets/OpenMicroKbd.blend','操作说明.md','验收报告.md','资料整理.md',
            '建模计划.md','工作日志.md','tools/openmicro_controls.py',
            'references/appearance_multiview_v2.png'] + renders
for rel in required:
    assert (root / rel).is_file() and (root / rel).stat().st_size > 0, rel

progress = read('progress.json')
progress['phase'] = 'complete'
progress['completed_batches'] = [
    '01_source_cad_baseline','02_shell_pcb_assembly',
    '03_13_choc_switches_and_keycaps','04_ec11_rkjxv_controls',
    '05_internal_electronics_21_leds','06_materials_interaction_exploded_rig',
    '07_demo_reopen_visual_acceptance_delivery']
progress['next_action'] = '交付完成；在Blender打开主文件，N侧栏选择OpenMicroKbd。'
progress['known_issues'] = []
progress['limitations'] = [
    'MakerWorld网页访问受限；使用已读取的用户仓库、V1 CAD/PCB、厂商图和官网照片。',
    'Choc以CPG1353家族参考建模；17.2 mm帽宽、曲面及部分内部结构为视觉近似。',
    'EC11E15244A5准确按压行程未确认，0.50 mm为演示代理。',
    '电子器件按封装族简化，触摸高亮和RGB是动画演示，不提供电气仿真。',
    '碰撞检查为记录范围内的离散表面检查，非连续实体或制造公差证明。',
    '12秒示范保存在blend中，未另行导出MP4。']
for rel in renders:
    entry = 'modeling/' + rel
    if entry not in progress['render_paths']:
        progress['render_paths'].append(entry)
reviews = [
    ('direct_01_hardware_corrected', '实看USB和机械总览；双重平移、悬空圆片、摇杆实心包络已修复。'),
    ('direct_02_electronics', '实看PCB上下表面；88源位号全部对应，21灯和简化器件可辨。'),
    ('direct_03_key_pressed', '实看重建内腔后的按下透明键，65个行程采样0失败。'),
    ('direct_05_exploded', '修复驱动变量后重新渲染实看，PCB/机构/帽/内部器件分层，复位误差0。'),
    ('direct_06_materials', '首轮过曝不通过；调低棚灯并补21个PCB光孔后重渲染实看通过。'),
    ('final_hero_night', '实际查看日间/夜间；13键布局清楚、透明帽与棕轴可见、灯光可辨。'),
    ('final_orthographic_usb', '实看顶/前/右/后与USB特写，尺寸层位、后侧胶囊口对准。'),
    ('final_pcb_top_bottom', '实看正反面，器件封装和布局可识别；最终再次实看底面。'),
    ('final_exploded', '实际查看全部解构层，最终交付复核再次实看。'),
    ('final_demo_frames', '实看14/113/196/220/285帧，覆盖按键、旋钮、摇杆、RGB触摸及解构。'),
    ('final_gui_reopen', '实际重开文件、鼠标点击星形按钮并实看截图；播放推进至27帧，停止复位。'),
    ('delivery_repeat', '再次实看整机、爆炸图、PCB底面；MCP重跑13键、旋钮、摇杆、灯光、解构、动画采样及复位均通过。')]
for view, result in reviews:
    if not any(x['view'] == view for x in progress['visual_reviews']):
        progress['visual_reviews'].append({'view':view,'result':result})
progress['complete'] = True
progress['audit_complete'] = True
progress['updated_at'] = datetime.datetime.now().astimezone().isoformat()
progress['acceptance_report'] = 'modeling/验收报告.md'
progress['blend_file'] = 'modeling/assets/OpenMicroKbd.blend'
(root/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

required += ['progress.json']
required += ['references/' + name for name in (
    'final_structural_audit.json','interaction_demo_audit.json','reopen_audit.json',
    'key_clearance_audit.json','final_mechanical_pending.json','exploded_rig_audit.json',
    'gui_click_audit.json','playback_audit.json','live_scene_audit.json')]
manifest = {'created_at':progress['updated_at'], 'files':[]}
for rel in required:
    data = (root/rel).read_bytes()
    manifest['files'].append({'path':rel,'size_bytes':len(data),
                              'sha256':hashlib.sha256(data).hexdigest()})
(root/'references/delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'complete':True,'batches':len(progress['completed_batches']),
                  'manifest_files':len(manifest['files']),
                  'blend_sha256':manifest['files'][0]['sha256']}))
