import bpy 
from time import time
import mathutils

def get_manifolds(me):

    edge_polygons = {}

    for polygon in me.polygons:
        for edge_key in polygon.edge_keys:
            edge_polygons[edge_key] = [polygon.index] if edge_key not in edge_polygons else edge_polygons[edge_key] + [polygon.index]

    manifolds = {edge_key:faces for edge_key, faces in edge_polygons.items() if len(edge_polygons[edge_key]) == 2}

    return manifolds


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
    get_manifolds(mesh)

    # Report performance...
    print("Script took %6.2f secs.\n\n"%(time()-t))


if __name__ == "__main__":
    main()