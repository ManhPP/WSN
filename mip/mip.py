from ortools.linear_solver import pywraplp


def solve(inp, is_adj_matrix):
    solver = pywraplp.Solver('wsn',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    connect_matrix = {}
    num_all_vertex = len(inp.all_vertex)
    a = [0 for i in range(num_all_vertex)]
    b = [0 for i in range(num_all_vertex)]

    for i in range(num_all_vertex):
        a[i] = solver.BoolVar('a[%i]' % i)
        b[i] = solver.BoolVar('b[%i]' % i)
        for j in range(num_all_vertex):
            connect_matrix[i, j] = solver.BoolVar('C[%i,%i]' % (i, j))

    # Objective

    # Constraints
    # r2
    solver.Add(solver.Sum(
        connect_matrix[i, j] for i in range(num_all_vertex) for j in range(num_all_vertex)) <= inp.num_of_relays)

    # r4
    for j in range(num_all_vertex):
        for i in range(num_all_vertex):
            solver.Add(connect_matrix[i, j] <= is_adj_matrix[i][j])

    for i in range(inp.num_of_relays+1, num_all_vertex):
        pass
