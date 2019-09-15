from DS.edge import Edge
from DS.graph import Graph, check_condition
from DS.vertex import Vertex


class Constructor:
    def __init__(self, num_sensors, num_relays, num_positions, list_vertices: Vertex = None):
        if list_vertices is None:
            self.list_vertex = []
        else:
            self.list_vertex = list_vertices
        self.num_sensors = num_sensors
        self.num_relays = num_relays
        self.num_positions = num_positions

    def add_vertex(self, vertex: Vertex):
        self.list_vertex.append(vertex)
        return True

    def gen_graph(self, genes: list):
        if len(genes) != 3*(self.num_positions + self.num_sensors + 1):
            raise Exception("Error Gen, length is not divisible by 3")
        graph = Graph()
        dict_order_adjacent = dict()
        dict_genes_order = {i: genes[i] for i in range(len(genes) // 3)}
        dict_genes_value = {i - len(genes) // 3: genes[i] for i in range(len(genes) // 3, 2 * len(genes) // 3)}
        # dict_genes_local_search = {i - 2 * len(genes) // 3: genes[i] for i in range(2 * len(genes) // 3,
        # 3 * len(genes) // 3)}
        order = list(dict(sorted(dict_genes_order.items(), key=lambda x: x[1])).keys())
        for i in range(len(order) - 1):
            index_vertex = order[i]
            vertex = self.list_vertex[index_vertex]
            print('--', -vertex.name)
            for j in vertex.adjacent_vertices:
                dict_order_adjacent[j.name] = dict_genes_value[j.name]
            order_adjacent = list(dict(sorted(dict_order_adjacent.items(), key=lambda x: x[1])).keys())
            for j in order_adjacent:
                edge = Edge(self.list_vertex[j], vertex)
                if check_condition(graph, edge):
                    graph.add_edge(edge)
                    print('++', self.list_vertex[j].name)
                    break
        return graph


if __name__ == '__main__':
    gen = [0.55, 0.75, 0.35, 0.65, 0.45, 0.99, 0.9, 0.3, 0.4, 0.6, 0.5, 0.4, 0.77, 0.22, 0.57, 0.45, 0.66, 0.14]
    vertices = [None for _ in range(6)]
    for i in range(6):
        vertices[i] = Vertex(i)
    vertices[0].adjacent_vertices = [vertices[1], vertices[3], vertices[5]]
    vertices[1].adjacent_vertices = [vertices[0], vertices[2], vertices[4], vertices[5]]
    vertices[2].adjacent_vertices = [vertices[0], vertices[1], vertices[3]]
    vertices[3].adjacent_vertices = [vertices[2], vertices[4], vertices[5]]
    vertices[4].adjacent_vertices = [vertices[1], vertices[3], vertices[3]]
    constructor = Constructor(3, 2, 2, vertices)
    a = constructor.gen_graph(gen)
