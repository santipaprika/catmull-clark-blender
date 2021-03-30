import bpy

def create_mesh(coords, faces, mesh_name):
    me = bpy.data.meshes.new(mesh_name)
    me.from_pydata(coords,[],faces)

    return me


def create_object_from_mesh(mesh, object_name, transform):
    ob = bpy.data.objects.new(object_name, mesh)
    ob.location = bpy.context.scene.cursor.location
    ob.matrix_world = transform
    bpy.context.scene.collection.objects.link(ob)

    return ob
