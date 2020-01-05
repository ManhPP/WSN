import itertools


def get_fitness(genes: list, params: dict, max_hop: int = 20, constructor=None):
    if constructor is None:
        raise Exception("Error: Must init constructor!")
    g = constructor.gen_graph(genes)
    if not g.is_connected:
        return float('inf')
    graph = g.graph
    for v in graph.keys():
        if v.hop > max_hop:
            return float('inf')
    vertices = g.vertices
    all_values = itertools.chain.from_iterable(graph.values())
    adjacent = list(set(all_values))
    list_send = []
    list_send_receive = []
    # params, _ = parse_config()

    for i in vertices:
        if i in adjacent:
            if len(graph[i]) > 1:
                list_send_receive.append(i)
            elif len(graph[i]) == 1:
                list_send.append(i)

    result = 0
    for i in list_send:
        # if i.type_of_vertex == "relay":
        #     continue
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

    return result
