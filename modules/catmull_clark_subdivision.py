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
    
    return new_vtx_contribution


def compute_catmull_edge_vertices(me, face_vertices):
    edge_vertices = {}
    manifold_edges_polygon_dict, boundary_edges_polygon_dict = utils.get_manifolds(me)

    for edge_key, faces in manifold_edges_polygon_dict.items():
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co

        # new face verices (computed above)
        vtx_F1, vtx_F2 = face_vertices[faces[0]], face_vertices[faces[1]]
        edge_vertices[edge_key] = ((vtx_A1 + vtx_A2 + vtx_F1 + vtx_F2)/4.0) 

    # BOUNDARY EDGES NEW VERTICES: Based on https://graphics.pixar.com/library/SEC/supplemental.pdf 
    for edge_key, faces in boundary_edges_polygon_dict.items():
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co
        edge_vertices[edge_key] = ((vtx_A1 + vtx_A2)/2.0)

    return edge_vertices


def compute_coords_faces(me, new_face_vertices, new_edge_vertices, vertex_faces, vertex_edges):
    vtx_idx_dict = {}
    vtx_last_idx = 0
    faces = []

    _, boundary_edges_dict = utils.get_manifolds(me)
    new_boundary_vertices = {}

    # compute new boundary vertices positions, which will be inserted afterwards in loops corresponding to these ones.
    for edge in me.edges:
        if edge.key in boundary_edges_dict:
            for vertex_idx in edge.vertices:
                V = me.vertices[vertex_idx].co
                new_original_v = (V * 1/2 + get_neighbor_contribution(vertex_edges[vertex_idx], new_edge_vertices, boundary_edges_dict))[:]
                vtx_last_idx += utils.add(new_original_v, vtx_idx_dict, vtx_last_idx)
                new_boundary_vertices[vertex_idx] = new_original_v


    for polygon in me.polygons:
        # new vtx 4 (face vtx)
        face_vtx = new_face_vertices[polygon.index][:]
        vtx_last_idx += utils.add(face_vtx, vtx_idx_dict, vtx_last_idx)

        for loop_idx in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
            vertex_idx = me.loops[loop_idx].vertex_index
            prev_loop_idx = loop_idx-1 if loop_idx > polygon.loop_start else loop_idx+polygon.loop_total-1

            # new vtx 1 (edge vtx)
            prev_edge_vtx = new_edge_vertices[me.edges[me.loops[prev_loop_idx].edge_index].key][:]
            vtx_last_idx += utils.add(prev_edge_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 2 (move original vertex)
            cur_new_edge_vertices = [new_edge_vertices[i] for i in vertex_edges[vertex_idx]]
            m = len(cur_new_edge_vertices)
            V = me.vertices[vertex_idx].co

            # if it is a boundary vertex, compute new coordinates based on https://graphics.pixar.com/library/SEC/supplemental.pdf 
            if me.edges[me.loops[prev_loop_idx].edge_index].key in boundary_edges_dict or \
                me.edges[me.loops[loop_idx].edge_index].key in boundary_edges_dict:
                new_original_vtx = (V * 1/2 + get_neighbor_contribution(vertex_edges[vertex_idx], new_edge_vertices, boundary_edges_dict))[:]
                vtx_last_idx += utils.add(new_original_vtx, vtx_idx_dict, vtx_last_idx)
                
            else:
                # if the vertex is boundary, do not compute new position, and use boundary position computed above
                if vertex_idx in new_boundary_vertices:
                    new_original_vtx = new_boundary_vertices[vertex_idx]
                else:
                    cur_new_face_vertices = [new_face_vertices[i] for i in vertex_faces[vertex_idx]]
                    F = utils.average_vertices_coords(cur_new_face_vertices)
                    R = utils.average_vertices_coords(cur_new_edge_vertices)
                    new_original_vtx = ((F + 2*R + (m-3)*V) / m)[:]
                    vtx_last_idx += utils.add(new_original_vtx, vtx_idx_dict, vtx_last_idx)


            # new vtx 3 (edge vtx)
            cur_edge_vtx = new_edge_vertices[me.edges[me.loops[loop_idx].edge_index].key][:]
            vtx_last_idx += utils.add(cur_edge_vtx, vtx_idx_dict, vtx_last_idx)

            faces.append((vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[new_original_vtx], vtx_idx_dict[cur_edge_vtx], vtx_idx_dict[face_vtx]))

    return [*vtx_idx_dict], faces


def catmull_clark_subdivision(me, instantiate=False, transform=mathutils.Matrix.identity):
    # face centroids
    face_vertices = utils.compute_face_vertices(me)

    # edge midpoints
    edge_vertices = compute_catmull_edge_vertices(me, face_vertices)

    vertex_faces = utils.get_vertex_faces(me)
    vertex_edges = utils.get_vertex_edges(me)

    # prepare data for blender mesh creation
    coords, faces = compute_coords_faces(me, face_vertices, edge_vertices, vertex_faces, vertex_edges)
    
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
    catmull_clark_subdivision(mesh, True, ob.matrix_world)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()
