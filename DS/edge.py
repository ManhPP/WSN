from DS.vertex import Vertex
from DS.position import distance


class Edge:
    def __init__(self, src: Vertex = None, dst: Vertex = None):
        self._src_vertex = src
        self._dst_vertex = dst
        self._distance = distance(src, dst)

    @property
    def src_vertex(self):
        return self._src_vertex

    @property
    def dst_vertex(self):
        return self._dst_vertex

    @property
    def distance(self):
        return self._distance

    def __repr__(self):
        return str(self.src_vertex) + " -> " + str(self.dst_vertex)
