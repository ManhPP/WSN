import sys

from DS.graph import Graph
from DS.vertex import Vertex
from utils.arg_parser import parse_config
import itertools


def get_fitness(genes: list, max_hop: int = 20, constructor=None):
    if constructor is None:
        raise Exception("Error: Must init constructor!")
    g = constructor.gen_graph(genes)
    if not g.is_connected:
        return float('inf')
    graph = g.graph    
    vertices = g.vertices
    all_values = itertools.chain.from_iterable(graph.values())
    adjacent = list(set(all_values))
    list_send = []
    list_send_receive = []
    params, _ = parse_config()

    for i in vertices:
        if i in adjacent:
            if len(graph[i]) != 0:
                list_send_receive.append(i)
            else:
                list_send.append(i)

    result = 0
    for i in list_send:
        for j in g.vertices:
            if i in graph[j]:
                result += params['E_TX'] + params['epsilon_fs'] * i.get_distance(j)**2
                break
    for i in list_send_receive:
        for j in g.vertices:
            if i in graph[j]:
                result += i.num_child * (params['E_RX'] + params['E_DA']) + params['epsilon_mp'] * i.get_distance(j)**4
                break
    result *= params['l']

    for i in vertices:
        if get_hop(g, i) > max_hop:
            # print(i.hop)
            return float('inf')
        # result += 9999 * max(i.hop - max_hop, 0)

    return result


def get_hop(g: Graph, vertex: Vertex):
    if vertex not in g.vertices:
        raise Exception("Error vertices not in graph: ", vertex)
    graph = g.graph

    def cal(v):
        if v == g.vertices[0]:
            return 0
        else:
            for i in g.vertices:
                if v in graph[i]:
                    return 1 + cal(i)
    return cal(vertex)


if __name__ == '__main__':
    print(parse_config())
