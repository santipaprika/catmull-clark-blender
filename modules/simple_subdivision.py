from time import time
import bpy
import mathutils
from create_mesh import create_mesh, create_object_from_mesh
import utils


def compute_coords_faces(me, face_vertices, edge_vertices):
    vtx_idx_dict = {}
    vtx_last_idx = 0
    faces = []
    output_crease = {}

    _, boundary_edges_dict = utils.get_manifolds(me)
    new_boundary_vertices = {}
    new_crease_vertices = {}

    # compute new boundary vertices positions, which will be inserted afterwards in loops corresponding to these ones.
    # this has no visual effect, but is done to achieve the same vertex indices when performing the interpolation
    for edge in me.edges:
        if edge.key in boundary_edges_dict:
            for vertex_idx in edge.vertices:
                new_original_v = me.vertices[vertex_idx].co[:]
                vtx_last_idx += utils.add(new_original_v, vtx_idx_dict, vtx_last_idx)
                new_boundary_vertices[vertex_idx] = new_original_v

    # compute crease vertices positions (similar than boundary vertices)
    # this has no visual effect, but is to achieve the same vertex indices when performing the interpolation
    vertex_edges = utils.get_vertex_edges(me)
    crease = utils.get_crease_per_edge(me)
    for vertex in me.vertices:
        crease_edges = {vtx_edge:1 for vtx_edge in vertex_edges[vertex.index] if crease[vtx_edge] > 0}
        if len(crease_edges) < 2:
            continue
        new_original_v = me.vertices[vertex.index].co[:]
        vtx_last_idx += utils.add(new_original_v, vtx_idx_dict, vtx_last_idx)
        new_crease_vertices[vertex.index] = new_original_v


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

            # new vtx 2 (two first conditions are to match vertex indices in interpolation)
            if vertex_idx in new_boundary_vertices:
                loop_vtx = new_boundary_vertices[vertex_idx] 
            elif vertex_idx in new_crease_vertices:
                loop_vtx = new_crease_vertices[vertex_idx]
            else:
                loop_vtx = me.vertices[vertex_idx].co[:]
                vtx_last_idx += utils.add(loop_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 3
            cur_edge_vtx = edge_vertices[me.edges[me.loops[loop_idx].edge_index].key]
            vtx_last_idx += utils.add(cur_edge_vtx, vtx_idx_dict, vtx_last_idx)

            faces.append((vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[loop_vtx], vtx_idx_dict[cur_edge_vtx], vtx_idx_dict[face_vtx]))

            output_crease[(vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[loop_vtx])] = crease[me.edges[me.loops[prev_loop_idx].edge_index].key]
            output_crease[(vtx_idx_dict[loop_vtx], vtx_idx_dict[cur_edge_vtx])] = crease[me.edges[me.loops[loop_idx].edge_index].key]

    return [*vtx_idx_dict], faces, output_crease


def simple_subdivision(me, instantiate=False, transform=mathutils.Matrix.identity):
    # face centroids
    face_vertices = utils.compute_face_vertices(me)

    # edge midpoints
    edge_vertices = utils.compute_edge_vertices(me)

    # prepare data for blender mesh creation
    coords, faces, creases = compute_coords_faces(me, face_vertices, edge_vertices)
    
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
    simple_subdivision(mesh, True, ob.matrix_world)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time()-t))


if __name__ == "__main__":
    main()
