from DS.edge import Edge, Edge2
from DS.vertex import Vertex


class Graph:
    def __init__(self):
        self.graph = dict()

    @property
    def vertices(self):
        return list(self.graph.keys())

    @property
    def edges(self):
        edges = []
        for vertex in self.graph:
            for neighbour in self.graph[vertex]:
                self.edges.append(Edge(vertex, neighbour))
        return edges
    @property
    def is_connected(self):
        tmp = self.connected_component()
        if len(tmp) > 1:
            return False
        else:
            return True

    def add_edge(self, edge: Edge):
        if edge.src_vertex in self.graph.keys():
            self.graph[edge.src_vertex].append(edge.dst_vertex)
        else:
            self.graph[edge.src_vertex] = [edge.dst_vertex]
        edge.dst_vertex.hop = 1 + int(edge.src_vertex.hop)
        edge.src_vertex.num_child += 1
        if edge.dst_vertex not in self.graph.keys():
            self.graph[edge.dst_vertex] = []

    def remove_edge(self, edge: Edge):
        self.graph[edge.src_vertex].remove(edge.dst_vertex)

    def DFS(self, i, visited, component):
        visited.append(i)
        component.append(i)
        for j in self.graph[i]:
            if (j not in visited):
                self.DFS(j, visited, component)

    def connected_component(self):
        v = self.vertices
        visited = []
        component = []
        result = []
        for i in v:
            if i not in visited:
                self.DFS(i, visited, component)
                result.append(component)
                component = []
        return result

    def __str__(self):
        return str(self.graph)


def check_condition(graph: Graph, edge: Edge):
    if edge.dst_vertex not in graph.vertices:
        return True
    elif edge.dst_vertex not in graph.graph.values():
        graph.add_edge(edge)
        if is_cyclic(graph) is False:
            graph.remove_edge(edge)
            return True
        graph.remove_edge(edge)
    else:
        return False


def is_cyclic(g):
    num_vertices = len(g.vertices)
    visited = []
    rec_stack = []
    for node in range(num_vertices):
        if node not in visited:
            if is_cyclic_util(g, g.vertices[node], visited, rec_stack) is True:
                return True
    return False


def is_cyclic_util(g: Graph, v: Vertex, visited: list, rec_stack: list):
    graph = g.graph
    visited.append(v)
    rec_stack.append(v)

    for neighbour in graph[v]:
        if neighbour not in visited:
            if is_cyclic_util(g, neighbour, visited, rec_stack) is True:
                return True
        elif neighbour in rec_stack:
            return True

    rec_stack.remove(v)
    return False
    
class Graph2:
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
                edge = Edge2(v1,v2)
                if edge not in self.edges:
                    self.edges.append(edge)
        return edges
    @property
    def is_connected(self):
        tmp = self.connected_component()
        if len(tmp) > 1:
            return False
        else:
            return True

    def add_edge(self, edge: Edge2):
        v1, v2 = edge.vertices
        if v1 in self.graph.keys():
            self.graph[v1].append(v2)
        else:
            self.graph[v1] = [v2]
        
        if v2 in self.graph.keys():
            self.graph[v2].append(v1)
        else:
            self.graph[v2] = [v1]
        
        if is_cyclic2(self):
            self.graph[v1].remove[v2]
            self.graph[v2].remove[v1]
            if len(self.graph[v1]) == 0:
                pass
            if len(self.graph[v2]) == 0:
                pass  


    def DFS(self, i, visited, component):
        visited.append(i)
        component.append(i)
        for j in self.graph[i]:
            if (j not in visited):
                self.DFS(j, visited, component)

    def connected_component(self):
        v = self.vertices
        visited = []
        component = []
        result = []
        for i in v:
            if i not in visited:
                self.DFS(i, visited, component)
                result.append(component)
                component = []
        return result

    def __str__(self):
        return str(self.graph)


def isCyclicUtil2(g: Graph2, v, visited, parent): 
        graph = g.graph
        #Mark the current node as visited  
        visited[v]= True
  
        #Recur for all the vertices adjacent to this vertex 
        for i in graph[v]: 
            # If the node is not visited then recurse on it 
            if  visited[i]==False :  
                if(isCyclicUtil2(g, i,visited,v)): 
                    return True
            # If an adjacent vertex is visited and not parent of current vertex, 
            # then there is a cycle 
            elif  parent!=i: 
                return True
          
        return False
           
   
#Returns true if the graph contains a cycle, else false. 
def isCyclic2(g:Graph2): 
    # Mark all the vertices as not visited 
    visited =[False]*len(g.graph.keys) 
    # Call the recursive helper function to detect cycle in different 
    #DFS trees 
    for i in range(len(g.graph.keys)): 
        if visited[i] ==False: #Don't recur for u if it is already visited 
            if(isCyclicUtil2(g, i,visited,-1))== True: 
                return True
        
    return False