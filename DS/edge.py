from DS.vertex import Vertex
from DS.position import distance


class Edge:
    def __init__(self, v1: Vertex = None, v2: Vertex = None):
        self.vertices = sorted([v1, v2], key=lambda x: x.name)
        self._distance = distance(v1,v2)

    @property
    def distance(self):
        return self._distance

    def __repr__(self):
        return str(self.vertices)
