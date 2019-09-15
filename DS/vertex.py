from DS.position import Position


class Vertex(Position):
    def __init__(self, name=None, pos: Position = Position()):
        super().__init__(pos.x, pos.y)
        self.name = name
        self.adjacent_vertices = []

    def check_adjacent(self, other):
        if type(other) != type(self):
            return False
        for element in self.adjacent_vertices:
            if element.pos.x == other.pos.x and element.pos.y == other.pos.y:
                return True
        return False

    def add_adjacent_vertex(self, vertex):
        self.adjacent_vertices.append(vertex)

    def __hash__(self):
        return hash(str(self.name))

    def __str__(self):
        return "name: " + self.name + str(self.adjacent_vertices)