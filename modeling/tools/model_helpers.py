import bpy, math, pathlib
from mathutils import Matrix, Vector
ROOT=pathlib.Path(r'C:\Users\myw\Documents\ChatGPT\硬件\modeling')

def material(name, color, metallic=0, rough=.4, transmission=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; m.diffuse_color=(*color,1)
    s=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if s is None:s=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None)
    if output is None:output=m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    if not output.inputs['Surface'].is_linked:m.node_tree.links.new(s.outputs['BSDF'],output.inputs['Surface'])
    s.inputs['Base Color'].default_value=(*color,1)
    s.inputs['Metallic'].default_value=metallic;s.inputs['Roughness'].default_value=rough
    s.inputs['Transmission Weight'].default_value=transmission
    return m

def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
    return c

def move_collection(o, name):
    c=collection(name)
    for old in list(o.users_collection):old.objects.unlink(o)
    c.objects.link(o)

def keep_parent(o, parent):
    bpy.context.view_layer.update();world=o.matrix_world.copy()
    o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=world
    bpy.context.view_layer.update()

def finish(o,name,mat,coll,parent=None,bevel=0):
    o.name=name;move_collection(o,coll)
    if mat:o.data.materials.clear();o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Edge radii','BEVEL');mod.width=bevel;mod.segments=3
    if parent:keep_parent(o,parent)
    return o

def cube(name,loc,dims,mat,coll,parent=None,bevel=.08):
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,mat,coll,parent,bevel)

def cylinder(name,loc,radius,depth,mat,coll,parent=None,axis='Z',vertices=48):
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object
    if axis=='X':o.rotation_euler.y=math.pi/2
    if axis=='Y':o.rotation_euler.x=math.pi/2
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return finish(o,name,mat,coll,parent,.045)

def empty(name,loc=(0,0,0),coll='10_Rig',parent=None):
    o=bpy.data.objects.get(name)
    if o is None:o=bpy.data.objects.new(name,None);collection(coll).objects.link(o)
    o.location=loc
    if parent:keep_parent(o,parent)
    return o

def remove_generated(names):
    for name in names:
        o=bpy.data.objects.get(name)
        if o:bpy.data.objects.remove(o,do_unlink=True)

def apply_boolean(obj,cutter,operation='DIFFERENCE'):
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    m=obj.modifiers.new('Mechanical opening','BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)

def capsule_loop(w,h,segments=24):
    r=h/2;d=(w-h)/2;out=[]
    for cx,start in ((d,-math.pi/2),(-d,math.pi/2)):
        for i in range(segments+1):
            a=start+i*math.pi/segments;out.append((cx+r*math.cos(a),r*math.sin(a)))
    return out

def capsule_tube(name,w,h,wi,hi,y0,y1,z,mat,coll,parent=None):
    outer=capsule_loop(w,h);inner=capsule_loop(wi,hi);n=len(outer)
    vs=[(x,y,z+zz) for y,loop in ((y0,outer),(y1,outer),(y0,inner),(y1,inner)) for x,zz in loop]
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),
                      (j,i,2*n+i,2*n+j),(n+i,n+j,3*n+j,3*n+i)])
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(vs,[],faces);me.update()
    o=bpy.data.objects.new(name,me);collection(coll).objects.link(o)
    return finish(o,name,mat,coll,parent,.025)

def save(name):
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'checkpoints'/name))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/MacroPad.blend'))

def camera(name,loc,target,scale=125):
    o=bpy.data.objects.get(name)
    if o is None:
        data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);collection('90_Studio').objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.type='ORTHO';o.data.ortho_scale=scale;o.data.clip_start=.1;o.data.clip_end=2000
    return o

def review_render(name,cam,size=(1300,1100)):
    s=bpy.context.scene;s.camera=cam;s.render.engine='BLENDER_WORKBENCH'
    s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL'
    s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
    s.render.resolution_x=size[0];s.render.resolution_y=size[1];s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.filepath=str(ROOT/'renders'/name)
    bpy.ops.render.render(write_still=True)
