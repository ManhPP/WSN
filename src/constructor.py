import os
import sys
import time
from copy import deepcopy

from DS.graph import Graph
from DS.vertex import Vertex

lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)


class Constructor:
    def __init__(self, logger, dict_egde, num_sensors, num_relays, num_positions, origin_list_vertices: Vertex = None):
        self.logger = logger
        if origin_list_vertices is None:
            self._origin_list_vertices = []
        else:
            self._origin_list_vertices = origin_list_vertices

        self.num_sensors = num_sensors
        self.num_relays = num_relays
        self.num_positions = num_positions
        self.dict_ind2edge = dict_egde

    def gen_graph(self, genes: list):
        st = time.time()
        # list_vertices = deepcopy(self._origin_list_vertices)
        list_vertices = self._origin_list_vertices[:]
        if len(genes) != self.num_positions + len(self.dict_ind2edge):
            raise Exception("Error Gen's length is not appropriate")

        graph = Graph()

        t1 = (time.time() - st)
        st = time.time()

        dict_edge_values = {i - self.num_positions + 1: genes[i] for i in range(self.num_positions, len(genes))}

        position_relay_index = list(
            dict(sorted({i + 1: genes[i] for i in range(self.num_positions)}.items(), key=lambda x: x[1])).keys())[
                               :self.num_relays]
        v0 = list_vertices[0]
        for i in self.dict_ind2edge.keys():
            edge = self.dict_ind2edge[i]
            v1, v2 = edge.vertices
            if v1.name == v0.name:
                if v2.name in position_relay_index:
                    graph.add_edge(edge)

        t2 = (time.time() - st)
        st = time.time()
        # [1,2,3, 6, 7, 8, 9, 10, 11, 12, 13]
        ignored_position = [i for i in range(1, self.num_positions + 1) if i not in position_relay_index]
        order = list(dict(sorted(list(dict_edge_values.items()), key=lambda x: x[1])).keys())

        t3 = (time.time() - st)
        stt = time.time()
        for i in range(len(order)):
            st = time.time()

            edge = self.dict_ind2edge[order[i]]

            t4 = (time.time() - st)
            st = time.time()

            if edge.vertices[0].name in ignored_position or edge.vertices[1].name in ignored_position:
                continue

            t5 = (time.time() - st)
            st = time.time()

            graph.add_edge(edge)

            t6 = (time.time() - st)

            if len(graph.edges) == self.num_relays + self.num_sensors:
                break
        t7 = time.time()-stt

        _ = graph.is_connected

        for v in graph.vertices:
            for adj in graph.graph[v]:
                try:
                    if graph.hop[adj] == 1 + graph.hop[v]:
                        try:
                            graph.num_child[v] += 1
                        except KeyError:
                            graph.num_child[v] = 1
                except KeyError:
                    continue

        return graph
