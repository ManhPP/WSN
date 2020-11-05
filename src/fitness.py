import itertools
import time


def get_fitness(genes: list, params: dict, max_hop: int = 20, constructor=None):
    if constructor is None:
        raise Exception("Error: Must init constructor!")
    g = constructor.gen_graph(genes)
    if not g.is_connected:
        return float('inf')
    graph = g.graph
    for v in graph.keys():
        if g.hop[v] > max_hop:
            return float('inf')
    vertices = g.vertices
    all_values = itertools.chain.from_iterable(graph.values())
    adjacent = list(set(all_values))
    list_send = []
    list_send_receive = []

    for i in vertices:
        if i in adjacent:
            if len(graph[i]) > 1 and i.type_of_vertex != 'bs':
                list_send_receive.append(i)
            elif len(graph[i]) == 1:
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
                result += g.num_child[i] * (params['E_RX'] + params['E_DA']) + params['epsilon_fs'] * i.get_distance(j)**2
                break
    result *= params['l']
    return result


if __name__ == '__main__':
    pass