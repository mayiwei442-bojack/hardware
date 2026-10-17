import bpy,math,sys
from mathutils import Vector
sys.path.insert(0,r'C:\Users\myw\Documents\ChatGPT\硬件\modeling\tools')
from model_helpers import *
def loop(width,r,z):
    h=width/2;vs=[]
    for cx,cy,start in ((h-r,h-r,0),(-h+r,h-r,90),(-h+r,-h+r,180),(h-r,-h+r,270)):
        for j in range(16):
            a=math.radians(start+j*90/15);vs.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    return vs
for num in range(3,16):
    ref=f'SW{num:02d}';cap=bpy.data.objects[ref+'_Cap'];ctrl=bpy.data.objects['CTRL_'+ref]
    ctrl['press']=0;ctrl.update_tag();bpy.context.view_layer.update()
    oldpts=[cap.matrix_world@v.co for v in cap.data.vertices]
    x=(min(p.x for p in oldpts)+max(p.x for p in oldpts))/2;y=(min(p.y for p in oldpts)+max(p.y for p in oldpts))/2
    specs=[(17.2,2.3,6.02),(17.0,2.2,6.47),(16.4,2.1,9.72),(15.7,1.95,10.27),(13.6,1.7,10.1),(15.5,.45,9.65),(15.7,.45,6.02)]
    vs=[];faces=[]
    for w,r,z in specs:vs.extend(loop(w,r,z))
    n=64
    for l in (0,1,2,3):
        for i in range(n):j=(i+1)%n;faces.append((l*n+i,l*n+j,(l+1)*n+j,(l+1)*n+i))
    top=len(vs);vs.append((0,0,9.97))
    for i in range(n):faces.append((4*n+i,4*n+(i+1)%n,top))
    # Underside is an open shell, joined at the skirt; ceiling remains above switch at full travel.
    for i in range(n):
        j=(i+1)%n;faces.append((6*n+i,6*n+j,j,i));faces.append((5*n+i,5*n+j,6*n+j,6*n+i))
    ceiling=len(vs);vs.append((0,0,9.65))
    for i in range(n):faces.append((5*n+(i+1)%n,5*n+i,ceiling))
    inv=cap.matrix_world.inverted();verts=[inv@Vector((x+a,y+b,z)) for a,b,z in vs]
    old=cap.data;me=bpy.data.meshes.new(ref+'_HollowCapMesh');me.from_pydata(verts,[],faces);me.update()
    for mat in old.materials:me.materials.append(mat)
    cap.data=me
    cap['geometry_note']='Open 15.7 mm inner skirt, ceiling 9.65 mm; top dished surface retained. Cap-to-cross engagement 0.13 mm.'
    # Keep crown flat shading to retain the shallow dish; side loops smooth.
    for p in me.polygons:p.use_smooth=p.index<4*n

save('direct_04_hollow_keycaps.blend')
result={'rebuilt_caps':13}
