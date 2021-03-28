import bpy
from time import time
import mathutils
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../modules")
from manifolds import get_manifolds


def simple_subdivision(me):
    # face centroids
    face_vtx = []
    for polygon in me.polygons:
        centroid = mathutils.Vector([0,0,0])
        for vert_idx in polygon.vertices:
            centroid += me.vertices[vert_idx].co

        face_vtx.append(centroid / len(me.vertices))

    # edge midpoints
    manifold_edges_polygon_dict = get_manifolds(me)
    for edge_key, faces in manifold_edges_polygon_dict:
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co

        # new face verices (computed above)
        vtx_F1, vtx_F2 = face_vtx[faces[0]].co, face_vtx[faces[1]].co
        edge_vtx = (vtx_A1 + vtx_A2 + vtx_F1 + vtx_F2)
        



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
    centroid = simple_subdivision(mesh)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()
