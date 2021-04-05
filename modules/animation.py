from time import time
import bpy
from parameter_surfaces import create_and_interpolate_subdivision, get_coords_and_faces
from bpy.app.handlers import persistent

@persistent
def animation_cbck(scn):

    strt = scn.frame_start
    end = scn.frame_end
    num = end-strt
    curr = scn.frame_current
    t = float(curr-strt)/num

    for itm in bpy.data.objects:
        if "Simple" in itm.name:
            me_simple = itm.data
        if "Catmull" in itm.name:
            me_catmull_clark = itm.data
        if "Interpolated" in itm.name:
            mesh = itm.data
    
    coords_simple, coords_catmull_clark, _ = get_coords_and_faces(me_simple, me_catmull_clark)
    coords_output = [((1-t)*coord_simple + t*coord_catmull_clark)[:] for coord_simple, coord_catmull_clark in zip(coords_simple, coords_catmull_clark)]
    
    for vert, coords in zip(mesh.vertices, coords_output):
        vert.co = coords

    mesh.update()


def animate(me, num_subdivs, transform, shade_smooth=False):
    # this creates both the simple and catmull-clark subdivided objects, which will be hidden,
    # and a copy of the simple subdivided one that will be the target object to be interpolated.
    create_and_interpolate_subdivision(me, num_subdivs, 0, transform, shade_smooth)

    # register the animation callback
    bpy.app.handlers.frame_change_pre.append(animation_cbck)


def main(num_subdivisions=4, shade_smooth=False):
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
    animate(mesh, num_subdivisions, ob.matrix_world, shade_smooth)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()