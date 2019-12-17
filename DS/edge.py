from DS.vertex import Vertex
from DS.position import distance


class Edge:
    def __init__(self, v1: Vertex = None, v2: Vertex = None):
        self.vertices = sorted([v1, v2], key=self.get_vertex_name)
        self._distance = distance(v1,v2)

    @staticmethod
    def get_vertex_name(v: Vertex):
        return v.name

    @property
    def distance(self):
        return self._distance

    def __repr__(self):
        return str(self.vertices)
