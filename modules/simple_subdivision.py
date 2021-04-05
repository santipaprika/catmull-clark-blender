from time import time
import bpy
import mathutils
from create_mesh import create_mesh, create_object_from_mesh
import utils


def get_neighbor_contribution(vertex_edges, new_edge_vertices, boundary_edges_dict):
    new_vtx_contribution = mathutils.Vector([0,0,0])
    for edge_key in vertex_edges:
        if edge_key in boundary_edges_dict:
            new_vtx_contribution += new_edge_vertices[edge_key] * 1/4
        # else:
            # new_vtx_contribution += new_edge_vertices[edge_key] * 1/len(vertex_edges)/2
    
    return new_vtx_contribution


def compute_coords_faces(me, face_vertices, edge_vertices):
    vtx_idx_dict = {}
    vtx_last_idx = 0
    faces = []

    _, boundary_edges_dict = utils.get_manifolds(me)
    new_boundary_vertices = {}

    for edge in me.edges:
        if edge.key in boundary_edges_dict:
            for vertex_idx in edge.vertices:
                V = me.vertices[vertex_idx].co
                new_original_v = me.vertices[vertex_idx].co[:]
                vtx_last_idx += utils.add(new_original_v, vtx_idx_dict, vtx_last_idx)
                new_boundary_vertices[vertex_idx] = new_original_v


    for polygon in me.polygons:
        # new vtx 4
        face_vtx = face_vertices[polygon.index][:]
        vtx_last_idx += utils.add(face_vtx, vtx_idx_dict, vtx_last_idx)

        for loop_idx in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
            vertex_idx = me.loops[loop_idx].vertex_index
            prev_loop_idx = loop_idx-1 if loop_idx > polygon.loop_start else loop_idx+polygon.loop_total-1

            # new vtx 1
            prev_edge_vtx = edge_vertices[me.edges[me.loops[prev_loop_idx].edge_index].key]
            vtx_last_idx += utils.add(prev_edge_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 2
            if vertex_idx in new_boundary_vertices:
                loop_vtx = new_boundary_vertices[vertex_idx] 
            else:
                loop_vtx = me.vertices[vertex_idx].co[:]
                vtx_last_idx += utils.add(loop_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 3
            cur_edge_vtx = edge_vertices[me.edges[me.loops[loop_idx].edge_index].key]
            vtx_last_idx += utils.add(cur_edge_vtx, vtx_idx_dict, vtx_last_idx)

            faces.append((vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[loop_vtx], vtx_idx_dict[cur_edge_vtx], vtx_idx_dict[face_vtx]))

    return [*vtx_idx_dict], faces


def simple_subdivision(me, instantiate=False, transform=mathutils.Matrix.identity):
    # face centroids
    face_vertices = utils.compute_face_vertices(me)

    # edge midpoints
    edge_vertices = utils.compute_edge_vertices(me)

    # prepare data for blender mesh creation
    coords, faces = compute_coords_faces(me, face_vertices, edge_vertices)
    
    out_mesh = create_mesh(coords, faces, "SubdividedMesh")

    if instantiate:
        create_object_from_mesh(out_mesh, "CatmullSubdividedObject", transform)

    return out_mesh


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
    simple_subdivision(mesh, True, ob.matrix_world)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()
