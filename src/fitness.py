from DS.graph import Graph
from DS.vertex import Vertex
from utils.arg_parser import parse_config


def get_fitness(g: Graph):
    graph = g.graph
    vertices = g.vertices
    adjacent = list(set(graph.values))
    list_send = []
    list_send_receive = []

    params = parse_config()

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
                result += params['E_RX'] + params['E_DA'] + params['epsilon_mp'] * i.get_distance(j)**4
                break

    return params['l'] * result


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
