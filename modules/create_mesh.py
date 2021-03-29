import bpy

def create_mesh(coords, faces, mesh_name, object_name, transform):
    me = bpy.data.meshes.new(mesh_name)

    ob = bpy.data.objects.new(object_name, me)
    ob.location = bpy.context.scene.cursor.location
    ob.matrix_world = transform
    bpy.context.scene.collection.objects.link(ob)

    me.from_pydata(coords,[],faces)

    return me
