from utils.load_input import WsnInput
from copy import deepcopy
from DS.position import distance


def prepare(path):
    inp = WsnInput.from_file(path)
    is_adj_matrix = [[0 for _ in range(len(inp.all_vertex))] for _ in range(len(inp.all_vertex))]

    for i in inp.all_vertex:
        for j in inp.all_vertex:
            if j.name == 0:
                continue
            if i.name > inp.num_of_relay_positions >= j.name:
                continue
            if distance(i, j) <= inp.radius and distance(i, j) != 0:
                is_adj_matrix[i.name][j.name] = 1

    return inp, is_adj_matrix


if __name__ == '__main__':
    a = prepare('/home/manhpp/Documents/Code/WSN/data/ga-dem1_r25_1.in')
    print(a)
