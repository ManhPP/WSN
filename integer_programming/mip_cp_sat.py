"""
sat follow mip_v3.py
"""

import os
import sys

lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)

from ortools.sat.python import cp_model
from itertools import combinations
from prepare_data import prepare
from utils.arg_parser import parse_config

coef = 1000000000000.0


def sub_lists(my_list, n):
    subs = []
    for i in range(0, len(my_list) + 1):
        temp = [list(x) for x in combinations(my_list, i)]
        if len(temp) > 0:
            subs.extend(temp)

    for i in subs:
        if 1 < len(i) <= n:
            yield i


def solve_by_or_tools(inp, is_adj_matrix, distance_matrix, dict_constant):
    model = cp_model.CpModel()
    num_all_vertex = len(inp.all_vertex)
    connect_matrix = {}
    muy = {}
    delta = {}
    gamma = {}
    y = {}
    print("num all vertex: ", num_all_vertex)
    a = [0 for _ in range(num_all_vertex)]
    b = [0 for _ in range(num_all_vertex)]
    e = [0 for _ in range(num_all_vertex)]

    for i in range(num_all_vertex):
        a[i] = model.NewBoolVar('a[%i]' % i)
        b[i] = model.NewBoolVar('b[%i]' % i)
        e[i] = model.NewBoolVar('e[%i]' % i)
        for j in range(num_all_vertex):
            connect_matrix[i, j] = model.NewBoolVar('C[%i,%i]' % (i, j))
            muy[i, j] = model.NewBoolVar('muy[%i,%i]' % (i, j))
            delta[i, j] = model.NewBoolVar('delta[%i,%i]' % (i, j))
            gamma[i, j] = model.NewIntVar(0, inp.num_of_sensors, 'gamma[%i,%i]' % (i, j))
    for k in range(1, num_all_vertex):
        for j in range(num_all_vertex):
            for i in range(num_all_vertex):
                y[i, j, k] = model.NewBoolVar('y[%i, %i, %i]' % (i, j, k))

    # Objective
    obj_func = []
    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            obj_func.append(muy[i, j] * int(
                (dict_constant['E_TX'] + dict_constant['epsilon_fs'] * distance_matrix[i, j] ** 2)))
            obj_func.append(delta[i, j] * int(dict_constant['epsilon_fs'] * distance_matrix[i, j] ** 2))
            obj_func.append(gamma[i, j] * int((dict_constant['E_RX'] + dict_constant['E_DA'])))

    model.Minimize(sum(obj_func))
    model.Proto().objective.scaling_factor = 1.0
    # model.Minimize(
    #     sum(muy[i, j] * int(1e4 * (dict_constant['E_TX'] + dict_constant['epsilon_fs'] * distance_matrix[i, j] ** 2)) +
    #         delta[i, j] * int(1e4 * dict_constant['epsilon_mp'] * distance_matrix[i, j] ** 4) +
    #         gamma[i, j] * int(1e4 * (dict_constant['E_RX'] + dict_constant['E_DA']))
    #         for i in range(1, num_all_vertex) for j in range(1, num_all_vertex))
    # )

    # Constraints

    # r32
    model.Add(sum(connect_matrix[0, j] for j in range(inp.num_of_relay_positions + 1)) <= inp.num_of_relays)

    # rang buoc tinh lien thong va chu trinh cua cay

    # r33
    model.Add(sum(connect_matrix[i, j] for i in range(num_all_vertex) for j in range(num_all_vertex))
              == sum(connect_matrix[0, j] for j in range(inp.num_of_relay_positions + 1)) + inp.num_of_sensors)

    # r35
    for j in range(num_all_vertex):
        for i in range(num_all_vertex):
            model.Add(connect_matrix[i, j] <= is_adj_matrix[i][j])

    for i in range(num_all_vertex):
        # r3
        model.Add(inp.num_of_sensors * b[i] >= sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        # r4
        model.Add(b[i] <= sum(connect_matrix[i, j] for j in range(num_all_vertex)))

    for i in range(inp.num_of_relay_positions + 1, num_all_vertex):
        # r1
        model.Add(inp.num_of_sensors * (1 - a[i]) >= sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        # r2
        model.Add(1 - a[i] <= sum(connect_matrix[i, j] for j in range(num_all_vertex)))

    for i in range(1, inp.num_of_relay_positions + 1):
        model.Add(a[i] == 0)
    for i in range(num_all_vertex):
        # r5
        model.Add(e[i] == a[i] + b[i])

    for j in range(1, num_all_vertex):
        # r6
        model.Add(e[j] == sum(connect_matrix[i, j] for i in range(num_all_vertex)))

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            # r7
            model.Add(muy[i, j] <= a[j])
            # r8
            model.Add(muy[i, j] <= connect_matrix[i, j])
            # r9
            model.Add(muy[i, j] >= a[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            # r10
            model.Add(delta[i, j] <= b[j])
            # r11
            model.Add(delta[i, j] <= connect_matrix[i, j])
            # r12
            model.Add(delta[i, j] >= b[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            # r13
            model.Add(gamma[i, j] <= sum(connect_matrix[j, k] for k in range(num_all_vertex)))
            # r14
            model.Add(gamma[i, j] <= inp.num_of_sensors * delta[i, j])
            # r15
            model.Add(
                gamma[i, j] >= sum(
                    connect_matrix[j, k] for k in range(num_all_vertex)) - inp.num_of_sensors * (1 - delta[i, j]))

    for j in range(num_all_vertex):
        # r16
        model.Add(sum(connect_matrix[i, j] for i in range(num_all_vertex)) <= 1)

    # hop constrained

    # r21
    for k in range(1, num_all_vertex):
        for j in range(1, num_all_vertex):
            if j != k:
                model.Add(sum(y[i, j, k] for i in range(num_all_vertex)) - sum(
                    y[j, i, k] for i in range(1, num_all_vertex)) == 0)

    # r22
    for j in range(1, num_all_vertex):
        model.Add(sum(y[i, j, j] for i in range(num_all_vertex)) == e[j])
        model.Add(sum(y[0, i, j] for i in range(1, num_all_vertex)) == e[j])

    # r23
    for k in range(1, num_all_vertex):
        model.Add(
            sum(y[i, j, k] for i in range(num_all_vertex) for j in range(1, num_all_vertex)) <= inp.max_hop)

    # r24
    for k in range(1, num_all_vertex):
        for i in range(num_all_vertex):
            for j in range(1, num_all_vertex):
                model.Add(y[i, j, k] <= connect_matrix[i, j])

    # print('Number of constraints =', model.NumConstraints())
    solver = cp_model.CpSolver()
    # cp_model.sat_parameters_pb2
    solver.parameters.num_search_workers = 2
    solver.parameters.log_search_progress = True
    print(model.ModelStats())

    result_status = solver.Solve(model)
    print('Solve status: %s' % solver.StatusName(result_status))
    if result_status == cp_model.OPTIMAL:
        print('optimal value = ', solver.ObjectiveValue())

    print('Statistics')
    print('  - conflicts : %i' % solver.NumConflicts())
    print('  - branches  : %i' % solver.NumBranches())
    print('  - wall time : %f s' % solver.WallTime())
    print()
    return dict_constant["l"] * solver.ObjectiveValue()


if __name__ == '__main__':
    _dict_constant, _data_path = parse_config()

    _inp, _is_adj_matrix, _distance_matrix = prepare(_data_path)
    # _inp, _is_adj_matrix, _distance_matrix = prepare("./../data/test.json")
    print("load data ok")
    result = solve_by_or_tools(_inp, _is_adj_matrix, _distance_matrix, _dict_constant)
    # result = solve_by_pulp(_inp, _is_adj_matrix, _distance_matrix, _dict_constant)

    print("result: ", result)
