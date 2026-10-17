import bpy,sys,json,importlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
import model_helpers
importlib.reload(model_helpers)
from model_helpers import *

def bounds(o):
    bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    pts=[ev.matrix_world@Vector(v) for v in ev.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
for num in range(3,16):
    ref=f'SW{num:02d}';ctrl=bpy.data.objects[f'CTRL_{ref}'];ctrl['press']=0;ctrl.update_tag();bpy.context.view_layer.update()
    slider=bpy.data.objects[ref+'_Stem_Slider'];box=bounds(slider);lo,hi=box[2]
    # Keep slider above the PCB at full travel. The original solid proxy crossed it.
    inv=slider.matrix_world.inverted()
    for v in slider.data.vertices:
        p=slider.matrix_world@v.co;p.z=5.04+(p.z-lo)/(hi-lo)*(7.02-5.04);v.co=inv@p
    slider.data.update()
    base=bpy.data.objects[ref+'_Base'];b=bounds(base);x=sum(b[0])/2;y=sum(b[1])/2
    cutter=cube('Switch travel cavity',(x,y,3.30),(4.6,4.6,3.0),None,'03_Switches',bevel=0)
    apply_boolean(base,cutter)
    base['mechanical_proxy']='Central travel pocket, 0.20 mm floor; outer package dimensions from Choc family'

def bvh(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons],all_triangles=False,epsilon=.00001)
    ev.to_mesh_clear();return tree
rows=[]
for num in range(3,16):
    ref=f'SW{num:02d}';ctrl=bpy.data.objects[f'CTRL_{ref}']
    for press in (0,.25,.5,.75,1):
        ctrl['press']=press;ctrl.update_tag();bpy.context.view_layer.update()
        moving=[bpy.data.objects[ref+s] for s in ('_Cap','_Stem_Cross','_Stem_Slider')]
        fixed=[bpy.data.objects[ref+s] for s in ('_Base','_Stem_Guide','_Top_Seat','_Locator_Post','_Shell_N','_Shell_E','_Shell_S','_Shell_W')]+[bpy.data.objects['PCB_Main']]
        overlaps=[]
        fixedtrees={o.name:bvh(o) for o in fixed}
        for o in moving:
            t=bvh(o)
            for name,t2 in fixedtrees.items():
                hits=t.overlap(t2)
                if hits:overlaps.append({'moving':o.name,'fixed':name,'triangles':len(hits)})
        rows.append({'key':ref,'press':press,'intersections':overlaps,'slider_z':bounds(moving[2])[2]})
    ctrl['press']=0;ctrl.update_tag()
bpy.context.view_layer.update()
report={'samples':rows,'sample_count':len(rows),'failing_samples':sum(bool(r['intersections']) for r in rows),'scope':'13 keys at five positions; evaluated moving surfaces versus base/guide/seat/locator/shell/PCB. Cap-to-stem attachment is intentional. Surface BVH does not prove solid containment clearance.'}
(ROOT/'references/key_clearance_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
save('direct_03_key_clearance.blend')
ctrl=bpy.data.objects['CTRL_SW09'];ctrl['press']=1;ctrl.update_tag();bpy.context.view_layer.update()
review_render('direct_03_key_pressed.png',camera('AUDIT_KeyTravel',(-27,-18,24),(-9.525,9.525,4),31),(1300,1000))
ctrl['press']=0;ctrl.update_tag();bpy.context.view_layer.update()
save('direct_03_key_clearance.blend')
result={'samples':len(rows),'failing_samples':report['failing_samples'],'first_failures':[r for r in rows if r['intersections']][:4]}
