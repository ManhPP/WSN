from DS.graph import Graph
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


if __name__ == '__main__':
    print(parse_config())
