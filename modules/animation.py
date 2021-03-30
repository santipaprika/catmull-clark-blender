from time import time
import bpy
from parameter_surfaces import create_interpolated_object, get_coords_and_faces, create_subdivisions

def animation_cbck(scn):
    if bpy.context.object:
        bpy.context.object.select_set(False)

    strt = scn.frame_start
    end = scn.frame_end
    num = end-strt
    curr = scn.frame_current
    t = float(curr-strt)/num

    for itm in bpy.data.objects:
        if "Simple" in itm.name:
            me_simple = itm.data
            transform = itm.matrix_world
        if "Catmull" in itm.name:
            me_catmull_clark = itm.data
        if "Interpolated" in itm.name:
            mesh = itm.data
            itm.select_set(True)
            bpy.ops.object.delete()
            bpy.data.meshes.remove(mesh)
    
    coords_simple, coords_catmull_clark, faces_output = get_coords_and_faces(me_simple, me_catmull_clark)
    create_interpolated_object(coords_simple, coords_catmull_clark, faces_output, t, transform)


def animate(me, num_subdivs, transform):
    create_subdivisions(me, num_subdivs, transform)
    bpy.app.handlers.frame_change_pre.append(animation_cbck)


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
    animate(mesh, 4, ob.matrix_world)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()