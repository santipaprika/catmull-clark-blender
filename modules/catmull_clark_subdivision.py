from time import time
import bpy
import mathutils
from manifolds import get_manifolds
from create_mesh import create_mesh, create_object_from_mesh
from simple_subdivision import compute_face_vertices, add


def average_vertices_coords(vertices_coords):
    cum_sum = mathutils.Vector([0,0,0])
    for vertex_coords in vertices_coords:
        cum_sum += vertex_coords

    return (cum_sum / len(vertices_coords))


def compute_catmull_edge_vertices(me, face_vertices):
    edge_vertices = {}
    manifold_edges_polygon_dict = get_manifolds(me)
    for edge_key, faces in manifold_edges_polygon_dict.items():
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co

        # new face verices (computed above)
        vtx_F1, vtx_F2 = face_vertices[faces[0]], face_vertices[faces[1]]
        edge_vertices[edge_key] = ((vtx_A1 + vtx_A2 + vtx_F1 + vtx_F2)/4.0)

    return edge_vertices


# V:{F}
def get_vertex_faces(me):
    vertex_faces = [[] for i in range(len(me.vertices))]
    for polygon in me.polygons:
        for vertex_idx in polygon.vertices:  
            vertex_faces[vertex_idx].append(polygon.index)
    
    return vertex_faces

# V:{E}
def get_vertex_edges(me):
    vertex_edges = [[] for i in range(len(me.vertices))]
    for edge in me.edges:
        for vertex_idx in edge.vertices:  
            vertex_edges[vertex_idx].append(edge.key)
    
    return vertex_edges


def compute_coords_faces(me, new_face_vertices, new_edge_vertices, vertex_faces, vertex_edges):
    vtx_idx_dict = {}
    vtx_last_idx = 0
    faces = []
    for polygon in me.polygons:
        # new vtx 4 (face vtx)
        face_vtx = new_face_vertices[polygon.index][:]
        vtx_last_idx += add(face_vtx, vtx_idx_dict, vtx_last_idx)

        for loop_idx in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
            prev_loop_idx = loop_idx-1 if loop_idx > polygon.loop_start else loop_idx+polygon.loop_total-1

            # new vtx 1 (edge vtx)
            prev_edge_vtx = new_edge_vertices[me.edges[me.loops[prev_loop_idx].edge_index].key][:]
            vtx_last_idx += add(prev_edge_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 2 (move original vertex)
            V = me.vertices[me.loops[loop_idx].vertex_index].co
            cur_new_face_vertices = [new_face_vertices[i] for i in vertex_faces[me.loops[loop_idx].vertex_index]]
            F = average_vertices_coords(cur_new_face_vertices)
            cur_new_edge_vertices = [new_edge_vertices[i] for i in vertex_edges[me.loops[loop_idx].vertex_index]]
            R = average_vertices_coords(cur_new_edge_vertices)
            m = len(cur_new_edge_vertices)
            new_original_vtx = ((F + 2*R + (m-3)*V) / m)[:]

            vtx_last_idx += add(new_original_vtx, vtx_idx_dict, vtx_last_idx)

            # new vtx 3 (edge vtx)
            cur_edge_vtx = new_edge_vertices[me.edges[me.loops[loop_idx].edge_index].key][:]
            vtx_last_idx += add(cur_edge_vtx, vtx_idx_dict, vtx_last_idx)

            faces.append((vtx_idx_dict[prev_edge_vtx], vtx_idx_dict[new_original_vtx], vtx_idx_dict[cur_edge_vtx], vtx_idx_dict[face_vtx]))

    return [*vtx_idx_dict], faces


def catmull_clark_subdivision(me, instantiate=False, transform=mathutils.Matrix.identity):
    # face centroids
    face_vertices = compute_face_vertices(me)

    # edge midpoints
    edge_vertices = compute_catmull_edge_vertices(me, face_vertices)

    vertex_faces = get_vertex_faces(me)
    vertex_edges = get_vertex_edges(me)

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
