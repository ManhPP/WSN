from ortools.linear_solver import pywraplp
from utils.arg_parser import parse_config
from prepare_data import prepare


def solve_ortools(inp, is_adj_matrix, distance_matrix, dict_constant):
    solver = pywraplp.Solver('wsn',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    num_all_vertex = len(inp.all_vertex)
    available_edges = []
    connect_matrix = {}
    muy = {}
    delta = {}
    gamma = {}
    phi = {}
    z = {}
    i_matrix = {}
    j_matrix = {}

    a = [0 for _ in range(num_all_vertex)]
    b = [0 for _ in range(num_all_vertex)]
    e = [0 for _ in range(num_all_vertex)]

    for i in range(num_all_vertex):
        a[i] = solver.BoolVar('a[%i]' % i)
        b[i] = solver.BoolVar('b[%i]' % i)
        e[i] = solver.BoolVar('e[%i]' % i)
        for j in range(num_all_vertex):
            connect_matrix[i, j] = solver.BoolVar('C[%i,%i]' % (i, j))
            muy[i, j] = solver.BoolVar('muy[%i,%i]' % (i, j))
            delta[i, j] = solver.BoolVar('delta[%i,%i]' % (i, j))
            gamma[i, j] = solver.IntVar(0, inp.num_of_sensors, 'gamma[%i,%i]' % (i, j))
            phi[i, j] = solver.BoolVar('phi[%i,%i]' % (i, j))

    for i in range(num_all_vertex):
        for j in range(1, num_all_vertex):
            if is_adj_matrix[i][j] == 1:
                available_edges.append((i, j))
                for q in range(1, inp.max_hop + 1):
                    for k in range(1, num_all_vertex):
                        z[i, j, q, k] = solver.BoolVar('z[%i,%i,%i,%i]' % (i, j, q, k))

    for k in range(1, num_all_vertex):
        for q in range(1, inp.max_hop + 1):
            z[k, k, q, k] = solver.BoolVar('z[%i,%i,%i,%i]' % (k, k, q, k))

    for i in range(num_all_vertex):
        tmp = []
        for j in range(num_all_vertex):
            if is_adj_matrix[i][j] == 1:
                tmp.append(j)
        j_matrix[i] = tmp

    for j in range(num_all_vertex):
        tmp = []
        for i in range(num_all_vertex):
            if is_adj_matrix[i][j] == 1:
                tmp.append(i)
        i_matrix[j] = tmp

    # Objective
    solver.Minimize(
        solver.Sum(muy[i, j] * (dict_constant['E_TX'] + dict_constant['epsilon_fs'] * distance_matrix[i, j] ** 2)
                   for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)) +
        solver.Sum(delta[i, j] * (dict_constant['epsilon_mp'] * distance_matrix[i, j] ** 4)
                   for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)) +
        solver.Sum(gamma[i, j] * (dict_constant['E_RX'] + dict_constant['E_DA'])
                   for i in range(1, num_all_vertex) for j in range(1, num_all_vertex))
    )

    # Constraints
    # r2
    solver.Add(solver.Sum(
        connect_matrix[i, j] for i in range(num_all_vertex) for j in range(num_all_vertex)) <= inp.num_of_relays)

    # r4
    for j in range(num_all_vertex):
        for i in range(num_all_vertex):
            solver.Add(connect_matrix[i, j] <= is_adj_matrix[i][j])

    for i in range(num_all_vertex):
        solver.Add(inp.num_of_sensors * b[i] >= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        solver.Add(b[i] <= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))

    for i in range(inp.num_of_relay_positions + 1, num_all_vertex):
        solver.Add(inp.num_of_sensors * (1 - a[i]) >= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        solver.Add(1 - a[i] <= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))

    for i in range(num_all_vertex):
        solver.Add(2 * e[i] >= a[i] + b[i])
        solver.Add(e[i] <= a[i] + b[i])

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            solver.Add(muy[i, j] <= a[i])
            solver.Add(muy[i, j] <= connect_matrix[i, j])
            solver.Add(muy[i, j] >= a[i] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            solver.Add(delta[i, j] <= b[i])
            solver.Add(delta[i, j] <= connect_matrix[i, j])
            solver.Add(delta[i, j] >= b[i] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            solver.Add(gamma[i, j] <= solver.Sum(connect_matrix[i, k] for k in range(num_all_vertex)))
            solver.Add(gamma[i, j] <= inp.num_of_sensors * delta[i, j])
            solver.Add(
                gamma[i, j] >= solver.Sum(
                    connect_matrix[i, k] for k in range(num_all_vertex)) - inp.num_of_sensors * (1 - delta[i, j]))

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            solver.Add(phi[i, j] <= e[i])
            solver.Add(phi[i, j] <= connect_matrix[i, j])
            solver.Add(phi[i, j] >= e[i] + connect_matrix[i, j] - 1)

    for j in range(num_all_vertex):
        solver.Add(solver.Sum(phi[i, j] for i in range(num_all_vertex)) == 1)

    # hop constrained
    for i in j_matrix[0]:
        for k in range(1, num_all_vertex):
            solver.Add(z[0, i, 1, k] - solver.Sum(z[i, j, 2, k] for j in j_matrix[i]) == 0)

    for i, j in available_edges:
        for k in range(1, num_all_vertex):
            solver.Add(solver.Sum(z[i, j, q, k] for q in range(1, inp.max_hop + 1)) <= connect_matrix[i, j])

    for k in range(1, num_all_vertex):
        solver.Add(solver.Sum(z[j, k, inp.max_hop, k] for j in i_matrix[k]) + z[k, k, inp.max_hop, k] == 1)

    for k in range(1, num_all_vertex):
        for q in range(2, inp.max_hop):
            for i in range(1, num_all_vertex):
                solver.Add(
                    solver.Sum(z[j, i, q, k] for j in i_matrix[i]) -
                    solver.Sum(z[i, j, q+1, k] for j in j_matrix[i]) == 0)

    print('Number of constraints =', solver.NumConstraints())
    result_status = solver.Solve()
    assert result_status == pywraplp.Solver.OPTIMAL
    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            print(connect_matrix[i, j])
    print()
    print('optimal value = ', solver.Objective().Value())
    print()
    print("Time = ", solver.WallTime(), " milliseconds")


if __name__ == '__main__':
    _inp, _is_adj_matrix, _distance_matrix = prepare('/home/manhpp/Documents/Code/WSN/data/ga-dem1_r25_1.in')
    _dict_constant = parse_config()
    solve_ortools(_inp, _is_adj_matrix, _distance_matrix, _dict_constant)
