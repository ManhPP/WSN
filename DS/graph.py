from DS.edge import Edge


class Graph:
    def __init__(self):
        self.graph = dict()

    @property
    def vertices(self):
        return list(self.graph.keys())

    @property
    def edges(self):
        edges = []
        for v1 in self.graph:
            for v2 in self.graph[v1]:
                edge = Edge(v1, v2)
                if edge not in edges:
                    edges.append(edge)
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

        if self.is_cyclic2():
            self.graph[v1].remove(v2)
            self.graph[v2].remove(v1)

    def DFS(self, i, visited, component):
        visited.append(i)
        component.append(i)
        for j in self.graph[i]:
            if j not in visited:
                j.hop = i.hop + 1
                self.DFS(j, visited, component)

    def connected_component(self):
        v = self.vertices
        visited = []
        component = []
        result = []
        for i in v:
            if i not in visited:
                if len(component) == 0:
                    i.hop = 0
                self.DFS(i, visited, component)
                result.append(component)
                component = []
        return result

    def is_cyclic_util2(self, v, visited, parent):
        graph = self.graph
        # Mark the current node as visited
        visited.append(v)

        # Recur for all the vertices adjacent to this vertex
        for i in graph[v]:
            # If the node is not visited then recurse on it
            if i not in visited:
                if self.is_cyclic_util2(i, visited, v):
                    return True
            # If an adjacent vertex is visited and not parent of current vertex,
            # then there is a cycle
            elif parent != i:
                return True

        return False

    # Returns true if the graph contains a cycle, else false.
    def is_cyclic2(self):
        # Mark all the vertices as not visited 
        visited = []
        # Call the recursive helper function to detect cycle in different 
        # DFS trees
        for i in self.graph.keys():
            if i not in visited:  # Don't recur for u if it is already visited
                if self.is_cyclic_util2(i, visited, -1) is True:
                    return True

        return False

    def __str__(self):
        return str(self.graph)
