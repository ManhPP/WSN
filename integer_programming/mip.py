import os
import sys
import time
lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)

import pulp
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from pulp import *
from itertools import combinations
import numpy as np
from integer_programming.prepare_data import prepare
from utils.arg_parser import parse_config
from ortools.sat.python import cp_model


def sub_lists(my_list):
	subs = []
	for i in range(0, len(my_list)+1):
	    temp = [list(x) for x in combinations(my_list, i)]
	    if len(temp)>0:
	        subs.extend(temp)
	result = []
	for i in subs:
		if len(i) > 1:
			result.append(i)
	return result

def solve_by_or_tools(inp, is_adj_matrix, distance_matrix, dict_constant):
    solver = pywraplp.Solver('wsn',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    
    num_all_vertex = len(inp.all_vertex)
    available_edges = []
    connect_matrix = {}
    muy = {}
    delta = {}
    gamma = {}
    # phi = {}
    z = {}
    i_matrix = {}
    j_matrix = {}

    subs = sub_lists([i for i in range(num_all_vertex)])

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
            # phi[i, j] = solver.BoolVar('phi[%i,%i]' % (i, j))

    for i in range(num_all_vertex):
        for j in range(1, num_all_vertex):
            if is_adj_matrix[i][j] == 1:
                available_edges.append((i, j))
                for q in range(1, inp.max_hop + 1):
                    for k in range(1, num_all_vertex):
                        z[i, j, q, k] = 0
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

    # solver.Minimize(solver.Sum(connect_matrix[i, j] * distance_matrix[i, j] for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)))

    # Constraints
    solver.Add(solver.Sum(
        connect_matrix[0, j] for j in range(inp.num_of_relay_positions+1))
               == inp.num_of_relays)
    # rang buoc tinh lien thong va chu trinh cua cay
    solver.Add(solver.Sum(
        connect_matrix[i,j] for i in range(num_all_vertex) for j in range(num_all_vertex))
               == inp.num_of_relays + inp.num_of_sensors)
    
    for sub in subs:
        solver.Add(solver.Sum(
            connect_matrix[sub[i], sub[j]] + connect_matrix[sub[j], sub[i]] for j in range(i+1, len(sub)) for i in range(len(sub)-1)) <= len(sub) - 1 )
        
    for j in range(num_all_vertex):
        for i in range(num_all_vertex):
            solver.Add(connect_matrix[i, j] <= is_adj_matrix[i][j])

    for i in range(1, num_all_vertex):
        solver.Add(inp.num_of_sensors * b[i] >= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        solver.Add(b[i] <= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
    # solver.Add(solver.Sum(b[i] for i in range(1,inp.num_of_relay_positions+1)) == inp.num_of_relays)
    for i in range(inp.num_of_relay_positions + 1, num_all_vertex):
        solver.Add(inp.num_of_sensors * (1 - a[i]) >= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
        solver.Add(1 - a[i] <= solver.Sum(connect_matrix[i, j] for j in range(num_all_vertex)))
    for i in range(1, inp.num_of_relay_positions + 1):
        solver.Add(a[i] == 0)
    for i in range(num_all_vertex):
        solver.Add(e[i] == a[i] + b[i])
    for i in range(1, num_all_vertex):    
        solver.Add(e[i] == solver.Sum(connect_matrix[j, i] for j in range(num_all_vertex)))

    # solver.Add(solver.Sum(b[i] for i in range(1, inp.num_of_relay_positions + 1)) <= inp.num_of_relays)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            solver.Add(muy[i, j] <= a[j])
            solver.Add(muy[i, j] <= connect_matrix[i, j])
            solver.Add(muy[i, j] >= a[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            solver.Add(delta[i, j] <= b[j])
            solver.Add(delta[i, j] <= connect_matrix[i, j])
            solver.Add(delta[i, j] >= b[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            solver.Add(gamma[i, j] <= solver.Sum(connect_matrix[j, k] for k in range(num_all_vertex)))
            solver.Add(gamma[i, j] <= inp.num_of_sensors * delta[i, j])
            solver.Add(
                gamma[i, j] >= solver.Sum(
                    connect_matrix[j, k] for k in range(num_all_vertex)) - inp.num_of_sensors * (1 - delta[i, j]))

    # for i in range(num_all_vertex):
    #     for j in range(num_all_vertex):
    #         solver.Add(phi[i, j] <= e[j])
    #         solver.Add(phi[i, j] <= connect_matrix[i, j])
    #         solver.Add(phi[i, j] >= e[j] + connect_matrix[i, j] - 1)

    # for j in range(1, num_all_vertex):
    #     solver.Add(solver.Sum(phi[i, j] for i in range(1, num_all_vertex)) == 1)
    # for i in range(inp.num_of_relay_positions + 1):
    #     solver.Add(solver.Sum(phi[i, j] for j in range(num_all_vertex)) >= 1)
    for j in range(num_all_vertex):
        solver.Add(solver.Sum(connect_matrix[i, j] for i in range(num_all_vertex)) <= 1)
    
    # hop constrained
    for i in j_matrix[0]:
        for k in range(1, num_all_vertex):
            solver.Add(z[0, i, 1, k] - solver.Sum(z[i, j, 2, k] for j in j_matrix[i]) == 0)

    for i, j in available_edges:
        for k in range(1, num_all_vertex):
            solver.Add(solver.Sum(z[i, j, q, k] for q in range(1, inp.max_hop + 1)) <= connect_matrix[i, j])

    for k in range(1, num_all_vertex):
        solver.Add(solver.Sum(z[j, k, inp.max_hop, k] for j in i_matrix[k]) + z[k, k, inp.max_hop, k] == e[k])

    for k in range(1, num_all_vertex):
        for q in range(2, inp.max_hop):
            for i in range(1, num_all_vertex):
                solver.Add(
                    solver.Sum(z[j, i, q, k] for j in i_matrix[i]) -
                    solver.Sum(z[i, j, q+1, k] for j in j_matrix[i]) == 0)

    print('Number of constraints =', solver.NumConstraints())
    result_status = solver.Solve()
    assert result_status == pywraplp.Solver.OPTIMAL
    connect_matrix_result = {}
    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            print(connect_matrix[i, j].solution_value(),end='|')
            connect_matrix_result[i,j] = connect_matrix[i, j].solution_value()
            if j == inp.num_of_relay_positions:
                print("|",end='|')
        print()
        if i == inp.num_of_relay_positions:
            print("---"*20)
    print("\n\n")
    for i in range(num_all_vertex):
        print(a[i].solution_value(), end='|')
    print()
    for i in range(num_all_vertex):
        print(b[i].solution_value(), end='|')
    print()
    for i in range(num_all_vertex):
        print(e[i].solution_value(), end='|')
    print("\nZ:")
    for i in range(num_all_vertex):
        for j in range(1, num_all_vertex):
            if is_adj_matrix[i][j] == 1:
                for q in range(1, inp.max_hop + 1):
                    for k in range(1, num_all_vertex):
                        if z[i, j, q, k].solution_value() == 1:
                            print(i,j,q,k)

    print()
    print('optimal value = ', solver.Objective().Value())
    print()
    print("Time = ", solver.WallTime(), " milliseconds")
    return dict_constant["l"] * solver.Objective().Value(), connect_matrix_result

def solve_by_pulp(inp, is_adj_matrix, distance_matrix, dict_constant):
    num_all_vertex = len(inp.all_vertex)
    available_edges = []
    connect_matrix = {}
    muy = {}
    delta = {}
    gamma = {}
    # phi = {}
    z = {}
    i_matrix = {}
    j_matrix = {}

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
            # phi[i, j] = pulp.LpVariable('phi[%i,%i]' % (i, j), 0, 1, cat=LpInteger)

    for i in range(num_all_vertex):
        for j in range(1, num_all_vertex):
            if is_adj_matrix[i][j] == 1:
                available_edges.append((i, j))
                for q in range(1, inp.max_hop + 1):
                    for k in range(1, num_all_vertex):
                        z[i, j, q, k] = pulp.LpVariable('z[%i,%i,%i,%i]' % (i, j, q, k), 0, 1, cat=LpInteger)

    for k in range(1, num_all_vertex):
        for q in range(1, inp.max_hop + 1):
            z[k, k, q, k] = pulp.LpVariable('z[%i,%i,%i,%i]' % (k, k, q, k), 0, 1, cat=LpInteger)
            
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

    lp_prob += pulp.lpSum(muy[i, j] * (dict_constant['E_TX'] + dict_constant['epsilon_fs'] * distance_matrix[i, j] ** 2) for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)) + pulp.lpSum(delta[i, j] * (dict_constant['epsilon_mp'] * distance_matrix[i, j] ** 4) for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)) + pulp.lpSum(gamma[i, j] * (dict_constant['E_RX'] + dict_constant['E_DA']) for i in range(1, num_all_vertex) for j in range(1, num_all_vertex))
    
    # Constraints
    lp_prob += pulp.lpSum(connect_matrix[0, j] for j in range(inp.num_of_relay_positions+1)) <= inp.num_of_relays

    lp_prob += pulp.lpSum(connect_matrix[i,j] for i in range(num_all_vertex) for j in range(num_all_vertex)) == inp.num_of_relays + inp.num_of_sensors
    
    for sub in subs:
        lp_prob += pulp.lpSum(connect_matrix[sub[i], sub[j]] + connect_matrix[sub[j], sub[i]] for j in range(i+1, len(sub)) for i in range(len(sub)-1)) <= len(sub) - 1
        

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
            lp_prob += gamma[i, j] >= pulp.lpSum(connect_matrix[j, k] for k in range(num_all_vertex)) - inp.num_of_sensors * (1 - delta[i, j])

    # for i in range(num_all_vertex):
    #     for j in range(num_all_vertex):
    #         lp_prob += phi[i, j] <= e[j]
    #         lp_prob += phi[i, j] <= connect_matrix[i, j]
    #         lp_prob += phi[i, j] >= e[j] + connect_matrix[i, j] - 1

    # for j in range(1, num_all_vertex):
    #     lp_prob += pulp.lpSum(phi[i, j] for i in range(num_all_vertex)) == 1

    for j in range(num_all_vertex):
        lp_prob += pulp.lpSum(connect_matrix[i, j] for i in range(num_all_vertex)) <= 1
    
    # hop constrained
    for i in j_matrix[0]:
        for k in range(1, num_all_vertex):
            lp_prob += z[0, i, 1, k] - pulp.lpSum(z[i, j, 2, k] for j in j_matrix[i]) == 0

    for i, j in available_edges:
        for k in range(1, num_all_vertex):
            lp_prob += pulp.lpSum(z[i, j, q, k] for q in range(1, inp.max_hop + 1)) <= connect_matrix[i, j]

    for k in range(1, num_all_vertex):
        lp_prob += pulp.lpSum(z[j, k, inp.max_hop, k] for j in i_matrix[k]) + z[k, k, inp.max_hop, k] == 1

    for k in range(1, num_all_vertex):
        for q in range(2, inp.max_hop):
            for i in range(1, num_all_vertex):
                lp_prob += pulp.lpSum(z[j, i, q, k] for j in i_matrix[i]) - pulp.lpSum(z[i, j, q+1, k] for j in j_matrix[i]) == 0

    lp_prob.solve()
    print(pulp.LpStatus[lp_prob.status])
    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            print(connect_matrix[i, j].varValue,end='|')
            if j == inp.num_of_relay_positions:
                print("|",end='|')
        print()
        if i == inp.num_of_relay_positions:
            print("---"*20)
    
    return dict_constant["l"] * pulp.value(lp_prob.objective)

def solve_by_or_tools_model(inp, is_adj_matrix, distance_matrix, dict_constant):

    model = cp_model.CpModel()
      
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

    subs = sub_lists([i for i in range(num_all_vertex)])

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
            phi[i, j] = model.NewBoolVar('phi[%i,%i]' % (i, j))

    for i in range(num_all_vertex):
        for j in range(1, num_all_vertex):
            if is_adj_matrix[i][j] == 1:
                available_edges.append((i, j))
                for q in range(1, inp.max_hop + 1):
                    for k in range(1, num_all_vertex):
                        z[i, j, q, k] = model.NewBoolVar('z[%i,%i,%i,%i]' % (i, j, q, k))

    for k in range(1, num_all_vertex):
        for q in range(1, inp.max_hop + 1):
            z[k, k, q, k] = model.NewBoolVar('z[%i,%i,%i,%i]' % (k, k, q, k))
            
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
    model.Minimize(
        sum([np.dot(muy[i, j],(dict_constant['E_TX'])) + np.power(np.dot(dict_constant['epsilon_fs'],distance_matrix[i, j]),2)
            + np.power(np.dot(np.dot(delta[i, j],(dict_constant['epsilon_mp'])), distance_matrix[i, j]),4)
            + np.dot(gamma[i, j],(dict_constant['E_RX'] + dict_constant['E_DA'])) for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)])
    )

    # model.Minimize(model.Sum(connect_matrix[i, j] * distance_matrix[i, j] for i in range(1, num_all_vertex) for j in range(1, num_all_vertex)))

    # Constraints
    model.Add(sum(
        [connect_matrix[0, j] for j in range(inp.num_of_relay_positions+1)])
               == inp.num_of_relays)
    # rang buoc tinh lien thong va chu trinh cua cay
    model.Add(sum(
        [connect_matrix[i,j] for i in range(num_all_vertex) for j in range(num_all_vertex)])
               == inp.num_of_relays + inp.num_of_sensors - 1)
    
    for sub in subs:
        model.Add(sum(
            [connect_matrix[i, j] for j in range(i+1, len(sub)) for i in range(len(sub))])
               <= len(sub) - 1 )

    for j in range(num_all_vertex):
        for i in range(num_all_vertex):
            model.Add(connect_matrix[i, j] <= is_adj_matrix[i][j])

    for i in range(1, num_all_vertex):
        model.Add(inp.num_of_sensors * b[i] >= sum([connect_matrix[i, j] for j in range(num_all_vertex)]))
        model.Add(b[i] <= sum([connect_matrix[i, j] for j in range(num_all_vertex)]))

    for i in range(inp.num_of_relay_positions + 1, num_all_vertex):
        model.Add(inp.num_of_sensors * (1 - a[i]) >= sum([connect_matrix[i, j] for j in range(num_all_vertex)]))
        model.Add(1 - a[i] <= sum([connect_matrix[i, j] for j in range(num_all_vertex)]))

    for i in range(num_all_vertex):
        model.Add(e[i] == a[i] + b[i])

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            model.Add(muy[i, j] <= a[j])
            model.Add(muy[i, j] <= connect_matrix[i, j])
            model.Add(muy[i, j] >= a[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            model.Add(delta[i, j] <= b[j])
            model.Add(delta[i, j] <= connect_matrix[i, j])
            model.Add(delta[i, j] >= b[j] + connect_matrix[i, j] - 1)

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            model.Add(gamma[i, j] <= sum([connect_matrix[j, k] for k in range(num_all_vertex)]))
            model.Add(gamma[i, j] <= inp.num_of_sensors * delta[i, j])
            model.Add(
                gamma[i, j] >= sum(
                    [connect_matrix[j, k] for k in range(num_all_vertex)]) - inp.num_of_sensors * (1 - delta[i, j]))

    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            model.Add(phi[i, j] <= e[j])
            model.Add(phi[i, j] <= connect_matrix[i, j])
            model.Add(phi[i, j] >= e[j] + connect_matrix[i, j] - 1)

    for j in range(1, num_all_vertex):
        model.Add(sum([phi[i, j] for i in range(1, num_all_vertex)]) == 1)
 
    # hop constrained
    for i in j_matrix[0]:
        for k in range(1, num_all_vertex):
            model.Add(z[0, i, 1, k] - sum([z[i, j, 2, k] for j in j_matrix[i]]) == 0)

    for i, j in available_edges:
        for k in range(1, num_all_vertex):
            model.Add(sum([z[i, j, q, k] for q in range(1, inp.max_hop + 1)]) <= connect_matrix[i, j])

    for k in range(1, num_all_vertex):
        model.Add(sum([z[j, k, inp.max_hop, k] for j in i_matrix[k]]) + z[k, k, inp.max_hop, k] == 1)

    for k in range(1, num_all_vertex):
        for q in range(2, inp.max_hop):
            for i in range(1, num_all_vertex):
                model.Add(
                    sum([z[j, i, q, k] for j in i_matrix[i]]) -
                    sum([z[i, j, q+1, k] for j in j_matrix[i]]) == 0)


    solver = cp_model.Cpmodel()

    result_status = solver.Solve(model)
    assert result_status == solver.OPTIMAL
    for i in range(num_all_vertex):
        for j in range(num_all_vertex):
            print(connect_matrix[i, j])
    print()
    return dict_constant["l"] * solver.ObjectiveValue()


if __name__ == '__main__':
    _dict_constant, _data_path = parse_config()

    _inp, _is_adj_matrix, _distance_matrix = prepare(_data_path)
    result, connect_matrix = solve_by_or_tools(_inp, _is_adj_matrix, _distance_matrix, _dict_constant)
    # result = solve_by_pulp(_inp, _is_adj_matrix, _distance_matrix, _dict_constant)

    print("result: ", result)

 
    subs = sub_lists([i for i in range(14)])
    for sub in subs:
        sum = 0
        for i in range(len(sub)-1):
            for j in range(i+1, len(sub)):
                sum += connect_matrix[sub[i], sub[j]] + connect_matrix[sub[j], sub[i]] 
        if sum > len(sub) - 1:
            print('constraint error - sum: ', sum)
            print(sub)