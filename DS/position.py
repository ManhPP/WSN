import math


class Position:
    def __init__(self, x=0., y=0.):
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def get_distance(self, p):
        return distance(self, p)


def distance(p_1: Position, p_2: Position):
    return math.sqrt((p_1.x - p_2.x) ** 2 + (p_1.y - p_2.y) ** 2)


if __name__ == '__main__':
    p1 = Position(0, 1)
    p2 = Position(1, 2)
    print(distance(p1, p2))
    print(p1.get_distance(p2))
