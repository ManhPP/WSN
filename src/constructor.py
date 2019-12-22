import time, os, sys
lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)

from DS.edge import Edge as Edge
from DS.graph import Graph
from DS.vertex import Vertex
from copy import deepcopy


class Constructor:
    def __init__(self, dict_egde,  num_sensors, num_relays, num_positions, origin_list_vertices: Vertex = None):
        if origin_list_vertices is None:
            self._origin_list_vertices = []
        else:
            self._origin_list_vertices = origin_list_vertices
        
        self.num_sensors = num_sensors
        self.num_relays = num_relays
        self.num_positions = num_positions
        self.dict_ind2edge = dict_egde

    def gen_graph(self, genes: list):
        list_vertices = deepcopy(self._origin_list_vertices)
        if len(genes) != self.num_positions + len(self.dict_ind2edge):
            raise Exception("Error Gen's length is not appropriate")

        graph = Graph()

        dict_edge_values = {i - self.num_positions: genes[i] for i in range(self.num_positions,len(genes))}

        position_relay_index = list(
            dict(sorted({i+1: genes[i] for i in range(self.num_positions)}.items(), key=lambda x: x[1])).keys())[
                        :self.num_relays]
        v0 = list_vertices[0]
        for i in self.dict_ind2edge.keys():
            edge = self.dict_ind2edge[i]
            v1, v2 = edge.vertices
            if v1.name == v0.name:
                if v2.name in position_relay_index:
                    graph.add_edge(edge)

        ignored_position = [i for i in range(1, self.num_positions+1) if i not in position_relay_index]
        order = list(dict(sorted(list(dict_edge_values.items())[self.num_positions+1:], key=lambda x: x[1])).keys())

        for i in range(1, len(order) + 1):
            edge = self.dict_ind2edge[i]
            if edge.vertices[0].name in ignored_position or edge.vertices[1].name in ignored_position or edge in graph.edges:
                continue
            graph.add_edge(self.dict_ind2edge[i])
            if len(graph.edges) == self.num_relays + self.num_sensors:
                break
        return graph