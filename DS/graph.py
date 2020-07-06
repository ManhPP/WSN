from DS.edge import Edge


class Graph:
    def __init__(self):
        self.graph = dict()
        self.hop = {}
        self.num_child = {}
        self.subsets = []

    @property
    def vertices(self):
        return list(self.graph.keys())

    @property
    def edges(self):
        edges = []
        names = []
        for v1 in self.graph:
            for v2 in self.graph[v1]:
                edge = Edge(v1, v2)
                name = (edge.vertices[0].name, edge.vertices[1].name)
                if name not in names:
                    edges.append(edge)
                    names.append(name)
        return edges

    @property
    def is_connected(self):
        tmp = self.connected_component()
        if len(tmp) > 1:
            return False
        else:
            return True

    def add_edge(self, edge: Edge):
        v1, v2 = edge.vertices
        if v1 in self.graph.keys():
            if v2 not in self.graph[v1]:
                self.graph[v1].append(v2)
        else:
            self.graph[v1] = [v2]

        if v2 in self.graph.keys():
            if v1 not in self.graph[v2]:
                self.graph[v2].append(v1)
        else:
            self.graph[v2] = [v1]

        # if self.is_cyclic2():
        #     self.graph[v1].remove(v2)
        #     self.graph[v2].remove(v1)

    def DFS(self, i, visited, component):
        visited.append(i)
        component.append(i)
        for j in self.graph[i]:
            if j not in visited:
                self.hop[j] = self.hop[i] + 1
                # j.hop = i.hop + 1
                self.DFS(j, visited, component)

    def connected_component(self):
        v = self.vertices
        visited = []
        component = []
        result = []
        for i in v:
            if i not in visited:
                if len(component) == 0:
                    self.hop[i] = 0
                    # i.hop = 0
                self.DFS(i, visited, component)
                result.append(component)
                component = []
        return result

    def is_cyclic_util2(self, v, visited, parent):
        graph = self.graph
        visited.append(v)

        for i in graph[v]:
            if i not in visited:
                if self.is_cyclic_util2(i, visited, v):
                    return True
            elif parent != i:
                return True

        return False

    def is_cyclic2(self):
        visited = []
        for i in self.graph.keys():
            if i not in visited:
                if self.is_cyclic_util2(i, visited, -1) is True:
                    return True

        return False

    def __str__(self):
        return str(self.graph)
