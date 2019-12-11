import time, os, sys
lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)

from DS.edge import Edge
from DS.graph import Graph, Graph2, check_condition 
from DS.vertex import Vertex
from src.fitness import get_fitness, get_hop
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
        if len(genes) != self.num_positions + len(self.dict_ind2edge):
            raise Exception("Error Gen's length is not appropriate")

        graph = Graph2()

        dict_edge_values = {i - self.num_positions: genes[i] for i in range(self.num_positions,len(genes))}

        position_relay = list(
            dict(sorted({i: genes[i] for i in range(self.num_positions)}.items(), key=lambda x: x[1])).keys())[
                        :self.num_relays]
        ignored_position = [i for i in range(self.num_positions) if i not in position_relay]

        order = list(dict(sorted(list(dict_edge_values.items())[self.num_positions+1:], key=lambda x: x[1])).keys())

        for i in range(len(order)):
            graph.add_edge(self.dict_ind2edge[i])
            if len(graph.edges) == self.num_relays + self.num_sensors:
                break
        return graph