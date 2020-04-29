import os, sys
lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)
from utils.load_input import WsnInput
from DS.position import distance


no_connect = 0 #9999


def prepare(path):
    inp = WsnInput.from_file(path)
    is_adj_matrix = [[0 for _ in range(len(inp.all_vertex))] for _ in range(len(inp.all_vertex))]
    distance_matrix = {}
    for i in inp.all_vertex:
        for j in inp.all_vertex:
            if j.name == 0:
                distance_matrix[i.name, j.name] = no_connect
                continue
            if i.name > 0 and j.name <= inp.num_of_relay_positions:
                distance_matrix[i.name, j.name] = no_connect
                continue
            if distance(i, j) <= 2 * inp.radius and distance(i, j) != 0:
                distance_matrix[i.name, j.name] = distance(i, j)
                is_adj_matrix[i.name][j.name] = 1
            else:
                distance_matrix[i.name, j.name] = no_connect
                is_adj_matrix[i.name][j.name] = 0

    return inp, is_adj_matrix, distance_matrix


if __name__ == '__main__':
    a = prepare('/home/manhpp/d/Code/WSN/data/test.json')
    print(a)
