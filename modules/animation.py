from time import time
import bpy
from parameter_surfaces import create_interpolated_object, get_coords_and_faces, create_subdivisions
from bpy.app.handlers import persistent

@persistent
def animation_cbck(scn, depsgraph):

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
            out_obj = itm
            # uncomment next line if intended to render animation
            # itm = itm.evaluated_get(depsgraph)
            mesh = itm.data
    
    coords_simple, coords_catmull_clark, _ = get_coords_and_faces(me_simple, me_catmull_clark)
    coords_output = [((1-t)*coord_simple + t*coord_catmull_clark)[:] for coord_simple, coord_catmull_clark in zip(coords_simple, coords_catmull_clark)]
    
    for vert, coords in zip(mesh.vertices, coords_output):
        vert.co = coords

    # out_obj.select_set(True)
    # bpy.ops.object.shade_smooth()
    # out_obj.select_set(False)


def animate(me, num_subdivs, transform, shade_smooth=False):
    me_simple, me_catmull_clark = create_subdivisions(me, num_subdivs, transform)
    coords_simple, coords_catmull_clark, faces_output = get_coords_and_faces(me_simple, me_catmull_clark)
    create_interpolated_object(coords_simple, coords_catmull_clark, faces_output, 0, transform, shade_smooth)
    # bpy.app.handlers.frame_change_pre.append(animation_cbck)
    bpy.app.handlers.frame_change_post.append(animation_cbck)


def main(shade_smooth=False):
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

    ob.hide_render = True
    # Function that does all the work
    animate(mesh, 4, ob.matrix_world, shade_smooth)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()