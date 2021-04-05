from time import time
import bpy
import mathutils
from create_mesh import create_mesh, create_object_from_mesh
import utils


def compute_catmull_edge_vertices(me, face_vertices):
    edge_vertices = {}
    manifold_edges_polygon_dict, boundary_edges_polygon_dict = utils.get_manifolds(me)
    crease = utils.get_crease_per_edge(me)

    for edge_key, faces in manifold_edges_polygon_dict.items():
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co
        edge_vertices_weight = 1/4 + crease[edge_key]/4 

        # new face verices (computed above)
        vtx_F1, vtx_F2 = face_vertices[faces[0]], face_vertices[faces[1]]
        face_vertices_weight = 1/4 - crease[edge_key]/4

        # this is the average of the four vertices computed above if crease = 0
        edge_vertices[edge_key] = ((vtx_A1 + vtx_A2)*edge_vertices_weight + (vtx_F1 + vtx_F2)*face_vertices_weight) 

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
    crease = utils.get_crease_per_edge(me)
    output_crease = {}
    new_crease_vertices = {}

    # compute new boundary vertices positions, which will be inserted afterwards in loops corresponding to these ones.
    for edge in me.edges:
        if edge.key in boundary_edges_dict:
            for vertex_idx in edge.vertices:
                V = me.vertices[vertex_idx].co
                new_original_v = (V * 1/2 + utils.get_neighbor_contribution(vertex_edges[vertex_idx], new_edge_vertices, boundary_edges_dict))[:]
                vtx_last_idx += utils.add(new_original_v, vtx_idx_dict, vtx_last_idx)
                new_boundary_vertices[vertex_idx] = new_original_v
    
    # compute crease vertices positions (similar than boundary vertices)
    for vertex in me.vertices:
        crease_edges = {vtx_edge:1 for vtx_edge in vertex_edges[vertex.index] if crease[vtx_edge] > 0}
        if len(crease_edges) < 2:
            continue
        V = me.vertices[vertex.index].co
        new_original_v = (V * 1/2 + utils.get_neighbor_contribution(vertex_edges[vertex.index], new_edge_vertices, crease_edges, 1/len(crease_edges)/2))[:]
        vtx_last_idx += utils.add(new_original_v, vtx_idx_dict, vtx_last_idx)
        new_crease_vertices[vertex.index] = new_original_v


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
            # if the vertex has boundary edges, do not compute new position, and use boundary position computed above
            if vertex_idx in new_boundary_vertices:
                new_original_vtx = new_boundary_vertices[vertex_idx]
            # same for creases
            elif vertex_idx in new_crease_vertices:
                new_original_vtx = new_crease_vertices[vertex_idx]
            # otherwise, compute the default inner vertex catmull-clark position
            else:
                cur_new_edge_vertices = [new_edge_vertices[i] for i in vertex_edges[vertex_idx]]
                m = len(cur_new_edge_vertices)
                V = me.vertices[vertex_idx].co
                cur_new_face_vertices = [new_face_vertices[i] for i in vertex_faces[vertex_idx]]
                F = utils.average_vertices_coords(cur_new_face_vertices)
                R = utils.average_vertices_coords(cur_new_edge_vertices)
                new_original_vtx = ((F + R*1.3 + (m-2.3)*V) / m)[:]
                if crease[me.edges[me.loops[loop_idx].edge_index].key] > 0.9 and crease[me.edges[me.loops[prev_loop_idx].edge_index].key] > 0.9:
                    new_original_vtx = R/2 + V/2
                vtx_last_idx += utils.add(new_original_vtx, vtx_idx_dict, vtx_last_idx)


            # new vtx 3 (edge vtx)
            cur_edge_vtx = new_edge_vertices[me.edges[me.loops[loop_idx].edge_index].key][:]
            vtx_last_idx += utils.add(cur_edge_vtx, vtx_idx_dict, vtx_last_idx)

            output_crease[(vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[new_original_vtx])] = crease[me.edges[me.loops[prev_loop_idx].edge_index].key]
            output_crease[(vtx_idx_dict[new_original_vtx], vtx_idx_dict[cur_edge_vtx])] = crease[me.edges[me.loops[loop_idx].edge_index].key]

            faces.append((vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[new_original_vtx], vtx_idx_dict[cur_edge_vtx], vtx_idx_dict[face_vtx]))

    return [*vtx_idx_dict], faces, output_crease


def catmull_clark_subdivision(me, instantiate=False, transform=None):
    # face centroids
    face_vertices = utils.compute_face_vertices(me)

    # edge midpoints
    edge_vertices = compute_catmull_edge_vertices(me, face_vertices)

    vertex_faces = utils.get_vertex_faces(me)
    vertex_edges = utils.get_vertex_edges(me)

    # prepare data for blender mesh creation
    coords, faces, creases = compute_coords_faces(me, face_vertices, edge_vertices, vertex_faces, vertex_edges)
    
    out_mesh = create_mesh(coords, faces, "SubdividedMesh")

    # add creases
    for edge in out_mesh.edges:
        if edge.key in creases:
            edge.crease = creases[edge.key]

    out_mesh.update()

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
