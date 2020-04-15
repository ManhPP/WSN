import time, os, sys
lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)

import json
from DS.position import distance
from DS.vertex import Vertex
from DS.edge import Edge
from utils.init_log import init_log


class WsnInput:
    def __init__(self, _max_hop=20, _num_of_relay_positions=40, _num_of_relays=20, _num_of_sensors=40,
                 _radius=20., _relays=None, _sensors=None, _all_vertex=None, _bs=None, _dict_ind2edge=None):
        self.max_hop = _max_hop
        self.relays = _relays
        self.sensors = _sensors
        self.num_of_relay_positions = _num_of_relay_positions
        self.num_of_relays = _num_of_relays
        self.num_of_sensors = _num_of_sensors
        self.radius = _radius
        self.BS = _bs
        self.all_vertex = _all_vertex
        self.dict_ind2edge = _dict_ind2edge

    @classmethod
    def from_file(cls, path):
        f = open(path)
        d = json.load(f)
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d):
        max_hop = d['H']
        num_of_relays = d['num_of_relays']
        num_of_relay_positions = d['num_of_relay_positions']
        num_of_sensors = d['num_of_sensors']
        radius = d['radius']
        relay_positions = []
        sensors = []
        name = 0
        dict_ind2edge = {}
        BS = Vertex.from_dict(d['center'], "bs", name)
        name += 1

        for i in range(num_of_relay_positions):
            relay_positions.append(Vertex.from_dict(d['relay_positions'][i], "relay", name))
            name += 1

        for i in range(num_of_sensors):
            sensors.append(Vertex.from_dict(d['sensors'][i], "sensor", name))
            name += 1

        all_vertex = [BS]
        all_vertex.extend(relay_positions)
        all_vertex.extend(sensors)
        for index_i in range(len(all_vertex)):
            i = all_vertex[index_i]
            for index_j in range(index_i+1, len(all_vertex)):
                j = all_vertex[index_j]
                dis = distance(i, j)
                if dis <= 2 * radius and distance(i, j) != 0:
                    edge = Edge(i, j)
                    if edge not in dict_ind2edge.values():
                        index = len(dict_ind2edge)
                        dict_ind2edge[index + 1] = edge

                    if j not in i.adjacent_vertices:
                        i.add_adjacent_vertex(j)
                    if i not in j.adjacent_vertices:
                        j.add_adjacent_vertex(i)

        return cls(max_hop, num_of_relay_positions, num_of_relays, num_of_sensors, radius, relay_positions, sensors, all_vertex, BS, dict_ind2edge)

    def freeze(self):
        self.sensors = tuple(self.sensors)
        self.relays = tuple(self.relays)

    def to_dict(self):
        return {
            'max_hop': self.max_hop,
            'num_of_relay_positions': self.num_of_relay_positions,
            'num_of_relays': self.num_of_relays,
            'num_of_sensors': self.num_of_sensors,
            'relays': list(map(lambda x: x.to_dict(), self.relays)),
            'sensors': list(map(lambda x: x.to_dict(), self.sensors)),
            'all_vertex': list(map(lambda x: x.to_dict(), self.all_vertex)),
            'center': self.BS.to_dict(),
            'radius': self.radius,
            'edge': self.dict_ind2edge
        }

    def reset_all_hop(self):
        for v in self.all_vertex:
            v.reset_hop()

    def reset_all_child(self):
        for v in self.all_vertex:
            v.reset_child()

    def to_file(self, file_path):
        d = self.to_dict()
        with open(file_path, "wt") as f:
            fstr = json.dumps(d, indent=4)
            f.write(fstr)

    def __hash__(self):
        return hash((self.max_hop, self.num_of_relay_positions, self.num_of_relays, self.num_of_sensors, self.radius,
                     tuple(self.relays), tuple(self.sensors)))

    def __eq__(self, other):
        return hash(self) == hash(other)


if __name__ == "__main__":
    inp = WsnInput.from_file('/home/manhpp/d/Code/WSN/data/test.json')
    print(inp.relays[0])