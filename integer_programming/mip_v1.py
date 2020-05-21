"""
sub list with all vertex
"""

import os
import sys
import time

lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)

import pulp
from ortools.linear_solver import pywraplp
from itertools import combinations
from pulp import *
import numpy as np
from integer_programming.prepare_data import prepare
from utils.arg_parser import parse_config


def sub_lists(my_list, n):
    subs = []
    for i in range(0, len(my_list) + 1):
        temp = [list(x) for x in combinations(my_list, i)]
        if len(temp) > 0:
            subs.extend(temp)
    result = []
    for i in subs:
        if len(i) > 1 and len(i) <= n:
            result.append(i)
    return result


def solve_by_or_tools(inp, is_adj_matrix, distance_matrix, dict_constant):
    solver = pywraplp.Solver('wsn',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    num_all_vertex = len(inp.all_vertex)
    connect_matrix = {}
    muy = {}
    delta = {}
    gamma = {}
    y = {}
    print("num all vertex: ", num_all_vertex)
    subs = sub_lists([i for i in range(num_all_vertex)], num_all_vertex)
    print("Len subset: ", len(subs))
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
    for k in range(1, num_all_vertex):
        for j in range(num_all_vertex):
            for i in range(num_all_vertex):
                y[i, j, k] = solver.BoolVar('y[%i, %i, %i]' % (i, j, k))

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

    # r16
    solver.Add(solver.Sum(
        connect_matrix[0, j] for j in range(inp.num_of_relay_positions + 1))
               <= inp.num_of_relays)

    # rang buoc tinh lien thong va chu trinh cua cay

    # r17
    solver.Add(solver.Sum(
        connect_matrix[i, j] for i in range(num_all_vertex) for j in range(num_all_vertex))
               == inp.num_of_relays + inp.num_of_sensors)

    # r18
    for sub in subs:
        sums = []
        for i in range(len(sub) - 1):
            for j in range(i + 1, len(sub)):
                sums.append(connect_matrix[sub[i], sub[j]] + connect_matrix[sub[j], sub[i]])
        solver.Add(solver.Sum(sums) <= len(sub) - 1)
        # solver.Add(solver.Sum((connect_matrix[sub[i], sub[j]] + connect_matrix[sub[j], sub[i]]) for j in range(i+1, len(sub)) for i in range(len(sub)-1)) <= len(sub) - 1 )

    # r20
    for j in range(num_all_vertex):
        for i in range(num_all_vertex):
            solver.Add(connect_matrix[i, j] <= is_adj_matrix[i][j])

    for i in range(1, num_all_vertex):
        # r3
        solver.Add(inp.num_of_sensors * b[i] >= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        # r4
        solver.Add(b[i] <= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))

    for i in range(inp.num_of_relay_positions + 1, num_all_vertex):
        # r1
        solver.Add(inp.num_of_sensors * (1 - a[i]) >= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        # r2
        solver.Add(1 - a[i] <= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))

    for i in range(1, inp.num_of_relay_positions + 1):
        solver.Add(a[i] == 0)
    for i in range(num_all_vertex):
        # r5
        solver.Add(e[i] == a[i] + b[i])

    for j in range(1, num_all_vertex):
        # r6
        solver.Add(e[j] == solver.Sum(connect_matrix[i, j] for i in range(num_all_vertex)))

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            # r7
            solver.Add(muy[i, j] <= a[j])
            # r8
            solver.Add(muy[i, j] <= connect_matrix[i, j])
            # r9
            solver.Add(muy[i, j] >= a[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            # r10
            solver.Add(delta[i, j] <= b[j])
            # r11
            solver.Add(delta[i, j] <= connect_matrix[i, j])
            # r12
            solver.Add(delta[i, j] >= b[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            # r13
            solver.Add(gamma[i, j] <= solver.Sum(connect_matrix[j, k] for k in range(num_all_vertex)))
            # r14
            solver.Add(gamma[i, j] <= inp.num_of_sensors * delta[i, j])
            # r15
            solver.Add(
                gamma[i, j] >= solver.Sum(
                    connect_matrix[j, k] for k in range(num_all_vertex)) - inp.num_of_sensors * (1 - delta[i, j]))

    for j in range(num_all_vertex):
        # r16
        solver.Add(solver.Sum(connect_matrix[i, j] for i in range(num_all_vertex)) <= 1)

    # hop constrained

    # r21
    for k in range(1, num_all_vertex):
        for j in range(1, num_all_vertex):
            if j != k:
                solver.Add(solver.Sum(y[i, j, k] for i in range(num_all_vertex)) - solver.Sum(
                    y[j, i, k] for i in range(1, num_all_vertex)) == 0)

    # r22
    for j in range(1, num_all_vertex):
        solver.Add(solver.Sum(y[i, j, j] for i in range(num_all_vertex)) == e[j])

    # r23
    for k in range(1, num_all_vertex):
        solver.Add(
            solver.Sum(y[i, j, k] for i in range(num_all_vertex) for j in range(1, num_all_vertex)) <= inp.max_hop)

    # r24
    for k in range(1, num_all_vertex):
        for i in range(num_all_vertex):
            for j in range(1, num_all_vertex):
                solver.Add(y[i, j, k] <= connect_matrix[i, j])

    print('Number of constraints =', solver.NumConstraints())
    result_status = solver.Solve()
    assert result_status == pywraplp.Solver.OPTIMAL
    connect_matrix_result = {}
    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            print(connect_matrix[i, j].solution_value(), end='|')
            connect_matrix_result[i, j] = connect_matrix[i, j].solution_value()
            if j == inp.num_of_relay_positions:
                print("|", end='|')
        print()
        if i == inp.num_of_relay_positions:
            print("---" * 20)
    print("\n\n")
    for i in range(num_all_vertex):
        print(a[i].solution_value(), end='|')
    print()
    for i in range(num_all_vertex):
        print(b[i].solution_value(), end='|')
    print()
    for i in range(num_all_vertex):
        print(e[i].solution_value(), end='|')

    print()

    for k in range(1, num_all_vertex):
        for j in range(num_all_vertex):
            for i in range(num_all_vertex):
                if y[i, j, k].solution_value() != 0:
                    print('y[%i, %i, %i]' % (i, j, k), y[i, j, k].solution_value())
    print('optimal value = ', solver.Objective().Value())
    print()
    print("Time = ", solver.WallTime(), " milliseconds")
    return dict_constant["l"] * solver.Objective().Value(), connect_matrix_result


def solve_by_pulp(inp, is_adj_matrix, distance_matrix, dict_constant):
    num_all_vertex = len(inp.all_vertex)

    connect_matrix = {}
    muy = {}
    delta = {}
    gamma = {}
    y = {}

    subs = sub_lists([i for i in range(num_all_vertex)])

    a = [0 for _ in range(num_all_vertex)]
    b = [0 for _ in range(num_all_vertex)]
    e = [0 for _ in range(num_all_vertex)]

    # Create a LP Minimization problem 
    lp_prob = pulp.LpProblem("wsn", LpMinimize)

    for i in range(num_all_vertex):
        a[i] = pulp.LpVariable('a[%i]' % i, 0, 1, cat=LpInteger)
        b[i] = pulp.LpVariable('b[%i]' % i, 0, 1, cat=LpInteger)
        e[i] = pulp.LpVariable('e[%i]' % i, 0, 1, cat=LpInteger)
        for j in range(num_all_vertex):
            connect_matrix[i, j] = pulp.LpVariable('C[%i,%i]' % (i, j), 0, 1, cat=LpInteger)
            muy[i, j] = pulp.LpVariable('muy[%i,%i]' % (i, j), 0, 1, cat=LpInteger)
            delta[i, j] = pulp.LpVariable('delta[%i,%i]' % (i, j), 0, 1, cat=LpInteger)
            gamma[i, j] = pulp.LpVariable('gamma[%i,%i]' % (i, j), 0, inp.num_of_sensors, cat=LpInteger)

    for k in range(1, num_all_vertex):
        for j in range(num_all_vertex):
            for i in range(num_all_vertex):
                y[i, j, k] = pulp.LpVariable('y[%i, %i, %i]' % (i, j, k), 0, 1, cat=LpInteger)

    lp_prob += pulp.lpSum(
        muy[i, j] * (dict_constant['E_TX'] + dict_constant['epsilon_fs'] * distance_matrix[i, j] ** 2) for i in
        range(1, num_all_vertex) for j in range(1, num_all_vertex)) + pulp.lpSum(
        delta[i, j] * (dict_constant['epsilon_mp'] * distance_matrix[i, j] ** 4) for i in range(1, num_all_vertex) for j
        in range(1, num_all_vertex)) + pulp.lpSum(
        gamma[i, j] * (dict_constant['E_RX'] + dict_constant['E_DA']) for i in range(1, num_all_vertex) for j in
        range(1, num_all_vertex))

    # Constraints
    lp_prob += pulp.lpSum(connect_matrix[0, j] for j in range(inp.num_of_relay_positions + 1)) <= inp.num_of_relays

    lp_prob += pulp.lpSum(connect_matrix[i, j] for i in range(num_all_vertex) for j in
                          range(num_all_vertex)) == inp.num_of_relays + inp.num_of_sensors

    for sub in subs:
        lp_prob += pulp.lpSum(
            connect_matrix[sub[i], sub[j]] + connect_matrix[sub[j], sub[i]] for j in range(i + 1, len(sub)) for i in
            range(len(sub) - 1)) <= len(sub) - 1

    for j in range(num_all_vertex):
        for i in range(num_all_vertex):
            lp_prob += connect_matrix[i, j] <= is_adj_matrix[i][j]

    for i in range(1, num_all_vertex):
        lp_prob += inp.num_of_sensors * b[i] >= pulp.lpSum(connect_matrix[i, j] for j in range(num_all_vertex))
        lp_prob += b[i] <= pulp.lpSum(connect_matrix[i, j] for j in range(num_all_vertex))

    for i in range(inp.num_of_relay_positions + 1, num_all_vertex):
        lp_prob += inp.num_of_sensors * (1 - a[i]) >= pulp.lpSum(connect_matrix[i, j] for j in range(num_all_vertex))
        lp_prob += 1 - a[i] <= pulp.lpSum(connect_matrix[i, j] for j in range(num_all_vertex))
    for i in range(1, inp.num_of_relay_positions + 1):
        lp_prob += a[i] == 0
    for i in range(num_all_vertex):
        lp_prob += e[i] == a[i] + b[i]

    for i in range(1, num_all_vertex):
        lp_prob += e[i] == pulp.lpSum(connect_matrix[j, i] for j in range(num_all_vertex))

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            lp_prob += muy[i, j] <= a[j]
            lp_prob += muy[i, j] <= connect_matrix[i, j]
            lp_prob += muy[i, j] >= a[j] + connect_matrix[i, j] - 1

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            lp_prob += delta[i, j] <= b[j]
            lp_prob += delta[i, j] <= connect_matrix[i, j]
            lp_prob += delta[i, j] >= b[j] + connect_matrix[i, j] - 1

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            lp_prob += gamma[i, j] <= pulp.lpSum(connect_matrix[j, k] for k in range(num_all_vertex))
            lp_prob += gamma[i, j] <= inp.num_of_sensors * delta[i, j]
            lp_prob += gamma[i, j] >= pulp.lpSum(
                connect_matrix[j, k] for k in range(num_all_vertex)) - inp.num_of_sensors * (1 - delta[i, j])

    for j in range(num_all_vertex):
        lp_prob += pulp.lpSum(connect_matrix[i, j] for i in range(num_all_vertex)) <= 1

    # hop constrained

    for k in range(1, num_all_vertex):
        for j in range(1, num_all_vertex):
            if j != k:
                lp_prob += pulp.lpSum(y[i, j, k] for i in range(num_all_vertex)) - pulp.lpSum(
                    y[j, i, k] for i in range(1, num_all_vertex)) == 0

    for j in range(1, num_all_vertex):
        lp_prob += pulp.lpSum(y[i, j, j] for i in range(num_all_vertex)) == e[j]

    for k in range(1, num_all_vertex):
        lp_prob += pulp.lpSum(
            y[i, j, k] for i in range(num_all_vertex) for j in range(1, num_all_vertex)) <= inp.max_hop

    for k in range(1, num_all_vertex):
        for i in range(num_all_vertex):
            for j in range(1, num_all_vertex):
                lp_prob += y[i, j, k] <= connect_matrix[i, j]

    lp_prob.solve()
    print(pulp.LpStatus[lp_prob.status])
    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            print(connect_matrix[i, j].varValue, end='|')
            if j == inp.num_of_relay_positions:
                print("|", end='|')
        print()
        if i == inp.num_of_relay_positions:
            print("---" * 20)

    return dict_constant["l"] * pulp.value(lp_prob.objective)


if __name__ == '__main__':
    _dict_constant, _data_path = parse_config()

    _inp, _is_adj_matrix, _distance_matrix = prepare(_data_path)
    # _inp, _is_adj_matrix, _distance_matrix = prepare("D:\\Code\WSN\\data\\test_small.json")
    print("load data ok")
    result, connect_matrix = solve_by_or_tools(_inp, _is_adj_matrix, _distance_matrix, _dict_constant)
    # result = solve_by_pulp(_inp, _is_adj_matrix, _distance_matrix, _dict_constant)

    print("result: ", result)

    subs = sub_lists([i for i in range(14)], len(_inp.all_vertex))
    for sub in subs:
        sum = 0
        for i in range(len(sub) - 1):
            for j in range(i + 1, len(sub)):
                sum += connect_matrix[sub[i], sub[j]] + connect_matrix[sub[j], sub[i]]
        if sum > len(sub) - 1:
            print('constraint error - sum: ', sum)
            print(sub)
