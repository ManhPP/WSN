from collections import deque
import random
import sys
import os

from src.constructor import Constructor

lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)

from DS.graph import Graph
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
    # if not path:
    #     _, path = parse_config()

    inp = WsnInput.from_file(path)
    vertices = inp.all_vertex[:]

    graph = Graph()

    position_relay_indices = random_choices(range(1, inp.num_of_relay_positions + 1), inp.num_of_relays)
    list_edge_indices = []

    previous_vertices = {
        vertex: None for vertex in vertices
    }

    v0 = inp.all_vertex[0]
    for i in inp.dict_ind2edge.keys():
        edge = inp.dict_ind2edge[i]
        v1, v2 = edge.vertices
        if v1.name == v0.name:
            if v2.name in position_relay_indices:
                graph.add_edge(edge)
                previous_vertices[v2] = v1
                list_edge_indices.append(i)

    distances = {vertex: inf for vertex in vertices}

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
                if current_vertex.type_of_vertex == "bs" or adj.name not in position_relay_indices \
                        or current_vertex.type_of_vertex == 'sensor':
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

    for item in inp.dict_ind2edge.items():
        if item[1].vertices in list_edge:
            len_edge_before = len(graph.edges)
            graph.add_edge(item[1])
            if len(graph.edges) == len_edge_before + 1:
                list_edge_indices.append(item[0])

    return graph, position_relay_indices, list_edge_indices


def mst(path=None):
    # if not path:
    #     _, path = parse_config()

    inp = WsnInput.from_file(path)
    vertices = inp.all_vertex[:]

    graph = Graph()

    position_relay_indices = random_choices(range(1, inp.num_of_relay_positions + 1), inp.num_of_relays)
    list_chosen_edge_indices = []

    v0 = inp.all_vertex[0]
    for i in inp.dict_ind2edge.keys():
        edge = inp.dict_ind2edge[i]
        v1, v2 = edge.vertices
        if v1.name == v0.name:
            if v2.name in position_relay_indices:
                graph.add_edge(edge)
                list_chosen_edge_indices.append(i)

    lst_edge_indices = []
    for item in inp.dict_ind2edge.items():
        edge = item[1]
        v1, v2 = edge.vertices
        if v1.type_of_vertex == 'relay' and v1.name not in position_relay_indices:
            continue
        if v2.type_of_vertex == 'relay':
            if v1.type_of_vertex == "bs" or v2.name not in position_relay_indices:
                continue
        else:
            lst_edge_indices.append(item[0])

    lst_edge_indices = sorted(lst_edge_indices, key=lambda x: inp.dict_ind2edge[x].distance)

    for i in lst_edge_indices:
        edge = inp.dict_ind2edge[i]
        num_edge_before = len(graph.edges)
        graph.add_edge(edge)
        if len(graph.edges) == num_edge_before + 1:
            list_chosen_edge_indices.append(i)
        if len(graph.edges) == inp.num_of_relays + inp.num_of_sensors:
            break
    return graph, position_relay_indices, list_chosen_edge_indices


def encode(position_relay_indices, list_edge_indices, num_position_relays, num_of_relays, num_of_sensors, num_edges):
    ind = []

    if len(position_relay_indices) != num_of_relays:
        raise Exception("Error encode")
    if len(list_edge_indices) != num_of_relays + num_of_sensors:
        raise Exception("Error encode")
    inter = random.random()
    for i in range(num_position_relays):
        if i + 1 in position_relay_indices:
            ind.append(random.uniform(0, inter))
        else:
            ind.append(random.uniform(inter, 1))
    inter = random.random()
    for i in range(1, num_edges + 1):
        if i in list_edge_indices:
            ind.append(random.uniform(0, inter))
        else:
            ind.append(random.uniform(inter, 1))

    return ind


if __name__ == '__main__':
    path = "D:\Code\WSN\data\\test.json"
    inp = WsnInput.from_file(path)
    constructor = Constructor(None, inp.dict_ind2edge, inp.num_of_sensors, inp.num_of_relays,
                              inp.num_of_relay_positions,
                              inp.all_vertex)
    # g = spt(path=path)
    g = mst(path=path)
    ind = encode(g[1], g[2], inp.num_of_relay_positions, inp.num_of_relays, inp.num_of_sensors, len(inp.dict_ind2edge))
    gr = constructor.gen_graph(ind)
    tmp = deque()
