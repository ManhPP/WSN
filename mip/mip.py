from ortools.linear_solver import pywraplp
from utils.arg_parser import parse_config
from DS.position import distance

def solve(inp, is_adj_matrix, distance_matrix, dict_constant):
    solver = pywraplp.Solver('wsn',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    num_all_vertex = len(inp.all_vertex)

    connect_matrix = {}
    muy = {}
    delta = {}
    gamma = {}
    phi = {}

    a = [0 for i in range(num_all_vertex)]
    b = [0 for i in range(num_all_vertex)]
    e = [0 for i in range(num_all_vertex)]

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

    # Objective
    solver.Minimize(
        solver.Sum(muy[i, j] * (dict_constant['E_TX'] + dict_constant['epsilon_fs'] * distance_matrix[i, j] ** 2)
                   for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)) +
        solver.Sum())

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
        solver.Add(b[i] <= solver.Add(connect_matrix[i, j] for j in range(num_all_vertex)))

    for i in range(inp.num_of_relay_positions + 1, num_all_vertex):
        solver.Add(inp.num_of_sensors * (1 - a[i]) >= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        solver.Add(1 - a[i] <= solver.Add(connect_matrix[i, j] for j in range(num_all_vertex)))

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

