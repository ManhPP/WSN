from DS.edge import Edge


class Graph:
    def __init__(self):
        self.graph = dict()
        self.vertices = self.generate_vertices
        self.edges = self.generate_edges

    @property
    def generate_vertices(self):
        return list(self.graph.keys())

    @property
    def generate_edges(self):
        edges = []
        for vertex in self.graph:
            for neighbour in self.graph[vertex]:
                self.edges.append(Edge(vertex, neighbour))
        return edges

    def add_edge(self, edge: Edge):
        if check_condition(self, edge):
            if edge.src_vertex in self.graph.keys():
                self.graph[edge.src_vertex].append(edge.dst_vertex)
            else:
                self.graph[edge.src_vertex] = [edge.dst_vertex]

            if edge.dst_vertex not in self.graph.keys():
                self.graph[edge.dst_vertex] = []

            self.vertices = self.generate_vertices
            self.edges = self.generate_edges
        else:
            raise Exception("Edge can not be added")

    def __str__(self):
        return str(self.graph)


def check_condition(graph: Graph, edge: Edge):
    if edge.dst_vertex not in graph.generate_vertices:
        return True
    elif edge.dst_vertex not in graph.graph.values() and edge.src_vertex not in graph.generate_vertices:
        return True
    else:
        return False
