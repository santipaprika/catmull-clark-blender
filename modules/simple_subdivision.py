from time import time
import bpy
import mathutils
from manifolds import get_manifolds
from create_mesh import create_mesh


def average_vertices(me, vertices_idx):
    avg = mathutils.Vector([0,0,0])
    for vert_idx in vertices_idx:
        avg += me.vertices[vert_idx].co

    return (avg / len(vertices_idx))


def compute_face_vertices(me):
    face_vertices = []
    for polygon in me.polygons:
        face_vertices.append(average_vertices(me, polygon.vertices))

    return face_vertices


def compute_edge_vertices(me):
    edge_vertices = {}
    manifold_edges_polygon_dict = get_manifolds(me)
    for edge_key in manifold_edges_polygon_dict:
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co

        # new face verices (computed above)
        edge_vertices[edge_key] = ((vtx_A1 + vtx_A2)/2.0)[:]

    return edge_vertices

def add(vtx, vtx_idx_dict, vtx_last_idx):
    if vtx not in vtx_idx_dict:
        vtx_idx_dict[vtx] = vtx_last_idx
        return True
    return False

def compute_coords_faces(me, face_vertices, edge_vertices):
    vtx_idx_dict = {}
    vtx_last_idx = 0
    faces = []
    for polygon in me.polygons:
        # new vtx 4
        face_vtx = face_vertices[polygon.index][:]
        vtx_last_idx += add(face_vtx, vtx_idx_dict, vtx_last_idx)

        for loop_idx in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
            prev_loop_idx = loop_idx-1 if loop_idx > polygon.loop_start else loop_idx+polygon.loop_total-1

            # new vtx 1
            prev_edge_vtx = edge_vertices[me.edges[me.loops[prev_loop_idx].edge_index].key]
            vtx_last_idx += add(prev_edge_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 2
            loop_vtx = me.vertices[me.loops[loop_idx].vertex_index].co[:]
            vtx_last_idx += add(loop_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 3
            cur_edge_vtx = edge_vertices[me.edges[me.loops[loop_idx].edge_index].key]
            vtx_last_idx += add(cur_edge_vtx, vtx_idx_dict, vtx_last_idx)

            faces.append((vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[loop_vtx], vtx_idx_dict[cur_edge_vtx], vtx_idx_dict[face_vtx]))

    return [*vtx_idx_dict], faces


def simple_subdivision(me, transform):
    # face centroids
    face_vertices = compute_face_vertices(me)

    # edge midpoints
    edge_vertices = compute_edge_vertices(me)

    # prepare data for blender mesh creation
    coords, faces = compute_coords_faces(me, face_vertices, edge_vertices)
    
    return create_mesh(coords, faces, "SubdividedMesh", "SubdividedObject", transform)


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
    simple_subdivision(mesh, ob.matrix_world)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()
