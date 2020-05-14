from collections import deque
import random

from DS.graph import Graph
from utils.arg_parser import parse_config
from utils.init_log import init_log
from utils.load_input import WsnInput

inf = float('inf')


def random_choices(seq, num):
    result = []
    while len(result) != num:
        choice = random.choice(seq)
        if choice not in result:
            result.append(choice)
    return result


def spt(path=None):
    if not path:
        _, path = parse_config()

    inp = WsnInput.from_file(path)
    vertices = inp.all_vertex[:]

    graph = Graph()

    position_relay_indices = random_choices(range(1, inp.num_of_relay_positions + 1), inp.num_of_relays)

    v0 = inp.all_vertex[0]
    for i in inp.dict_ind2edge.keys():
        edge = inp.dict_ind2edge[i]
        v1, v2 = edge.vertices
        if v1.name == v0.name:
            if v2.name in position_relay_indices:
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
        if current_vertex.type_of_vertex == 'relay' and current_vertex.name not in position_relay_indices:
            continue

        for adj in current_vertex.adjacent_vertices:
            if adj.type_of_vertex == 'relay':
                if current_vertex.type_of_vertex == "bs" or adj.name not in position_relay_indices:
                    continue
            distance = adj.get_distance(current_vertex)
            new_distance = distances[current_vertex] + distance
            if new_distance < distances[adj]:
                distances[adj] = new_distance
                previous_vertices[adj] = current_vertex
    list_edge = []
    for item in previous_vertices.items():
        if None not in item:
            list_edge.append(sorted(item, key=lambda x: x.name))

    edge_indices = []
    for item in inp.dict_ind2edge.items():
        if item[1].vertices in list_edge:
            graph.add_edge(item[1])
            edge_indices.append(item[0])

    return graph, edge_indices, position_relay_indices


def mst(path=None):
    if not path:
        _, path = parse_config()

    inp = WsnInput.from_file(path)
    vertices = inp.all_vertex[:]

    graph = Graph()

    position_relay_indices = random_choices(range(1, inp.num_of_relay_positions + 1), inp.num_of_relays)

    v0 = inp.all_vertex[0]
    for i in inp.dict_ind2edge.keys():
        edge = inp.dict_ind2edge[i]
        v1, v2 = edge.vertices
        if v1.name == v0.name:
            if v2.name in position_relay_indices:
                graph.add_edge(edge)


if __name__ == '__main__':
    g, e, p = spt()
    tmp = deque()
