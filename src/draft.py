from collections import deque

from DS.graph import Graph
from utils.arg_parser import parse_config
from utils.init_log import init_log
from utils.load_input import WsnInput

inf = float('inf')


if __name__ == '__main__':
    logger = init_log()
    path = 'D:\\Code\\WSN\\data\\test.json'
    params, _ = parse_config()
    logger.info("prepare input data from path %s" % path)
    inp = WsnInput.from_file(path)

    vertices = inp.all_vertex[:]
    dict_ind2edge = inp.dict_ind2edge

    graph = Graph()

    position_relay_index = [1, 2, 3]
    v0 = inp.all_vertex[0]
    for i in inp.dict_ind2edge.keys():
        edge = inp.dict_ind2edge[i]
        v1, v2 = edge.vertices
        if v1.name == v0.name:
            if v2.name in position_relay_index:
                graph.add_edge(edge)

    distances = {vertex: inf for vertex in vertices}
    previous_vertices = {
        vertex: None for vertex in vertices
    }

    distances[vertices[0]] = 0
    while vertices:
        current_vertex = min(vertices, key=lambda vertex: distances[vertex])
        vertices.remove(current_vertex)
        if distances[current_vertex] == inf:
            break

        for adj in current_vertex.adjacent_vertices:
            distance = adj.get_distance(current_vertex)
            new_distance = distances[current_vertex] + distance
            if new_distance < distances[adj]:
                distances[adj] = new_distance
                previous_vertices[adj] = current_vertex

    path = deque()

