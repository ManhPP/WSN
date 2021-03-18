import os
import sys
import time
from copy import deepcopy

lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)
lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)

from DS.graph import Graph
from DS.vertex import Vertex
from utils.load_input import WsnInput


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
        list_vertices = self._origin_list_vertices[:]
        if len(genes) != self.num_positions + len(self.dict_ind2edge):
            raise Exception("Error Gen's length is not appropriate")

        graph = Graph()

        parent = {}
        rank = {}

        dict_edge_values = {i - self.num_positions + 1: genes[i] for i in range(self.num_positions, len(genes))}

        position_relay_index = dict(
            sorted({i + 1: genes[i] for i in range(self.num_positions)}.items(), key=lambda x: x[1])[
            :self.num_relays]).keys()

        ignored_position = [i for i in range(1, self.num_positions + 1) if i not in position_relay_index]
        order = dict(sorted(dict_edge_values.items(), key=lambda x: x[1])).keys()

        for i in list_vertices:
            if i.name not in ignored_position:
                parent[i] = i
                rank[i] = 0

        v0 = list_vertices[0]
        for i in self.dict_ind2edge.keys():
            edge = self.dict_ind2edge[i]
            v1, v2 = edge.vertices
            if v1.name == v0.name:
                if v2.name in position_relay_index:
                    x = find(parent, v1)
                    y = find(parent, v2)
                    graph.add_edge(edge)
                    union(parent, rank, x, y)

        for i in order:
            edge = self.dict_ind2edge[i]

            if edge.vertices[0].name in ignored_position or edge.vertices[1].name in ignored_position:
                continue

            ###
            # union find
            x = find(parent, edge.vertices[0])
            y = find(parent, edge.vertices[1])
            if x != y:
                graph.add_edge(edge)
                union(parent, rank, x, y)
            ###

            # graph.add_edge(edge)

            if len(graph.edges) == self.num_relays + self.num_sensors:
                break

        graph.is_connected

        # print("par:", parent)
        # print("rak:", rank)
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


def find(parent, i):
    if parent[i] == i:
        return i
    return find(parent, parent[i])


def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)

    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot

    else:
        parent[yroot] = xroot
        rank[xroot] += 1


if __name__ == '__main__':
    genes = [0.8223327603832251, 0.5519544798440131, 0.06501414996964505, 0.8583744181340658, 0.5594550523184005,
             0.711301993249291, 0.6442170979029762, 0.32508811407024496, 0.1725090871101127, 0.36188450790235205,
             0.4222488856807952, 0.6941717810571076, 0.24165204504093984, 0.6880253604993705, 0.24565216565814663,
             0.5327694425914588, 0.46717796557700475, 0.9867536191383898, 0.1738898578214607, 0.8831379761998467,
             0.36657923276486326, 0.7496579400379899, 0.3543460420567176, 0.319607124864858, 0.279380603214455,
             0.5799968632766818, 0.9950962973516938, 0.7016305775360899, 0.6650792035130092, 0.6818779210454461,
             0.7432923539225167, 0.4273249078871607, 0.5530126825532685, 0.20322489387421905, 0.13525539033016742,
             0.634066892887522, 0.003800115671850346, 0.37929714351935384, 0.9515561608567823, 0.2124872143620513,
             0.9525333860312621, 0.1335565562227149, 0.09872205461112948, 0.7852197993654065, 0.14998777695064736,
             0.4850762009476114, 0.5060261537134161, 0.5929573782477754, 0.20159848634338673, 0.9896693109812186,
             0.9731578518651487, 0.42989159606769733, 0.1818002774615688, 0.5195527068029991, 0.11035013340743505,
             0.4944467936364799, 0.22412895674672917, 0.752741203307713, 0.9235345044470377, 0.28824100957630006,
             0.39566919150214874, 0.6233111448687184, 0.6108760866235008, 0.6873384260662784, 0.019976228320768064,
             0.42779798406303127, 0.46404943632654383, 0.693857752102711, 0.6174358536025151, 0.2729494147393693,
             0.78748016415214, 0.2959950975190051, 0.07289439737782955, 0.7949643173332854, 0.1775404371774827,
             0.16851374785740192, 0.4549142366543123, 0.6258454659592404, 0.9150106450266636, 0.9539110648909771,
             0.522572917739577, 0.9886351779714868, 0.44182708020930994, 0.5096059024145928, 0.8694650150223057,
             0.11684692765115667, 0.061135151607577765, 0.41417816399405183, 0.029527094667599507, 0.7276090477243848,
             0.5913856191333487, 0.6164846915980653, 0.5180693052113132, 0.05427816116901418, 0.951957984114913]
    inp = WsnInput.from_file("/Users/macbookpro/Workspace/WSN/code/WSN/data/test.json")
    # inp = WsnInput.from_file("/Users/macbookpro/Workspace/WSN/code/WSN/data/new_hop/ga-dem1_r25_1.json")

    constructor = Constructor(0, inp.dict_ind2edge, inp.num_of_sensors, inp.num_of_relays,
                              inp.num_of_relay_positions,
                              inp.all_vertex)
    t = time.time()
    g = constructor.gen_graph(genes)
    print("time:", time.time() - t)
    print(g.graph)
    print(g.hop)
