from DS.position import Position


class Vertex(Position):
    def __init__(self, pos: Position = Position(), type_of_vertex="normal", name=-1, hop: int = 0, num_child=0):
        super().__init__(pos.x, pos.y, pos.z)
        self.name = name
        self.hop = hop
        self.num_child = num_child
        self.type_of_vertex = type_of_vertex
        self.adjacent_vertices = []

    def check_adjacent(self, other):
        if type(other) != type(self):
            return False
        for element in self.adjacent_vertices:
            if element.pos.x == other.pos.x and element.pos.y == other.pos.y and element.pos.z == other.pos.z:
                return True
        return False

    def add_adjacent_vertex(self, vertex):
        self.adjacent_vertices.append(vertex)

    def reset_hop(self):
        self.hop = 0

    def reset_child(self):
        self.num_child = 0

    def to_dict(self):
        return {
            'name': self.name,
            "type": self.type_of_vertex,
            'hop': self.hop,
            'num_child': self.num_child,
            'x': self.x,
            'y': self.y,
            'z': self.z
        }

    @classmethod
    def from_dict(cls, d, type_of_vertex="normal", name=-1, hop=0, num_child=0):
        return cls(Position.from_dict(d), type_of_vertex, name, hop, num_child)

    def __hash__(self):
        return hash(str(self.name))

    def __repr__(self):
        return '%s (%f %f %f)' % (str(self.name + 1), self.x, self.y, self.z)
