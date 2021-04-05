import bpy
import mathutils


## ------------ DATA STRUCTURE QUERIES ------------

def add(vtx, vtx_idx_dict, vtx_last_idx):
    if vtx not in vtx_idx_dict:
        vtx_idx_dict[vtx] = vtx_last_idx
        return True
    return False


## ----------------- MATH QUERIES -----------------

def average_vertices(me, vertices_idx):
    avg = mathutils.Vector([0,0,0])
    for vert_idx in vertices_idx:
        avg += me.vertices[vert_idx].co

    return (avg / len(vertices_idx))

def average_vertices_coords(vertices_coords):
    cum_sum = mathutils.Vector([0,0,0])
    for vertex_coords in vertices_coords:
        cum_sum += vertex_coords

    return (cum_sum / len(vertices_coords))

def get_neighbor_contribution(vertex_edges, new_edge_vertices, filtered_edges_dict, contribution=1/4):
    new_vtx_contribution = mathutils.Vector([0,0,0])
    for edge_key in vertex_edges:
        if edge_key in filtered_edges_dict:
            new_vtx_contribution += new_edge_vertices[edge_key] * contribution
    
    return new_vtx_contribution


## ---------- TOPOLOGY FILTER QUERIES -----------

# get inner and boundary edges
def get_manifolds(me):

    edge_polygons = {}

    for polygon in me.polygons:
        for edge_key in polygon.edge_keys:
            edge_polygons[edge_key] = [polygon.index] if edge_key not in edge_polygons else edge_polygons[edge_key] + [polygon.index]

    manifolds = {edge_key:faces for edge_key, faces in edge_polygons.items() if len(edge_polygons[edge_key]) == 2}
    boundary = {edge_key:faces for edge_key, faces in edge_polygons.items() if len(edge_polygons[edge_key]) == 1}

    return manifolds, boundary

# get crease for all edges
def get_crease_per_edge(me):
    crease = {}
    for edge in me.edges:
        crease[edge.key] = edge.crease

    return crease


## ------------- TOPOLOGY RELATIONS -------------

# F:{V}
def compute_face_vertices(me):
    face_vertices = []
    for polygon in me.polygons:
        face_vertices.append(average_vertices(me, polygon.vertices))

    return face_vertices

# E:{V} (for inner and boundary edges)
def compute_edge_vertices(me):
    edge_vertices = {}
    manifold_edges_polygon_dict, boundary_edges_polygon_dict = get_manifolds(me)
    for edge_key in manifold_edges_polygon_dict:
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co

        # new face verices (computed above)
        edge_vertices[edge_key] = ((vtx_A1 + vtx_A2)/2.0)[:]

    for edge_key in boundary_edges_polygon_dict:
        # current edge vertices
        vtx_A1, vtx_A2 = me.vertices[edge_key[0]].co, me.vertices[edge_key[1]].co

        # new face verices (computed above)
        edge_vertices[edge_key] = ((vtx_A1 + vtx_A2)/2.0)[:]

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
