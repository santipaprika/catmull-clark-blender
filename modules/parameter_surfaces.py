from time import time
import bpy
from simple_subdivision import simple_subdivision
from catmull_clark_subdivision import catmull_clark_subdivision
from create_mesh import create_mesh, create_object_from_mesh


def create_subdivisions(me, num_subdivs, transform):
    me_simple = me
    me_catmull_clark = me
    for _ in range(num_subdivs):
        me_simple = simple_subdivision(me_simple)
        me_catmull_clark = catmull_clark_subdivision(me_catmull_clark)

    ob_simple = create_object_from_mesh(me_simple, "Subdivided Simple Object", transform)
    ob_catmull_clark = create_object_from_mesh(me_catmull_clark, "Subdivided Catmull Object", transform)

    ob_simple.hide_viewport = True
    ob_catmull_clark.hide_viewport = True

    return me_simple, me_catmull_clark

def get_coords_and_faces(me_simple, me_catmull_clark):
    coords_simple = [vertex.co for vertex in me_simple.vertices] 
    coords_catmull_clark = [vertex.co for vertex in me_catmull_clark.vertices] 
        
    faces_output = []
    for polygon in me_simple.polygons:
        faces_output.append(tuple(polygon.vertices))

    return coords_simple, coords_catmull_clark, faces_output


def create_interpolated_object(coords_simple, coords_catmull_clark, faces_output, t, transform):

    coords_output = [((1-t)*coord_simple + t*coord_catmull_clark)[:] for coord_simple, coord_catmull_clark in zip(coords_simple, coords_catmull_clark)]

    interp_mesh = create_mesh(coords_output, faces_output, "Interpolated Mesh")
    create_object_from_mesh(interp_mesh, "Subdivided Interpolated Object", transform)


def create_and_interpolate_subdivision(me, num_subdivs, t, transform):
    me_simple, me_catmull_clark = create_subdivisions(me, num_subdivs, transform)
    coords_simple, coords_catmull_clark, faces_output = get_coords_and_faces(me_simple, me_catmull_clark)
    create_interpolated_object(coords_simple, coords_catmull_clark, faces_output, t, transform)


def main():
    # Retrieve the active object (the last one selected)
    ob = bpy.context.active_object

    # Check that it is indeed a mesh
    if not ob or ob.type != 'MESH':
        print("Active object is not a MESH! Aborting...")
        return

    # If we are in edit mode, return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Retrieve the mesh data
    mesh = ob.data

    # Get current time
    t = time()

    # Function that does all the work
    create_and_interpolate_subdivision(mesh, 3, 0.5, ob.matrix_world)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()