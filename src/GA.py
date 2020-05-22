import os
import random
import sys
import time

import numpy
from deap import base, creator, tools, algorithms
import multiprocessing

from DS.vertex import Vertex
from src.constructor import Constructor
from src.fitness import get_fitness
from utils.arg_parser import parse_config
from utils.init_log import init_log
from utils.load_input import WsnInput

lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)

creator.create("FitnessMin", base.Fitness, weights=(-1.,))
FitnessMin = creator.FitnessMin
creator.create("Individual", list, fitness=FitnessMin)

N_GENS = 200
POP_SIZE = 300
CXPB = 0.8
MUTPB = 0.2
TERMINATE = 30
RATE_THRESHOLD = 0.5


def init_individual(constructor, num_edges, num_pos):
    length = num_edges + num_pos
    individual = [random.random() for _ in range(length)]
    g = constructor.gen_graph(individual)
    i = 0
    while not g.is_connected:
        individual = [random.uniform(0, 1) for _ in range(length)]
        g = constructor.gen_graph(individual)
        i += 1
        print("init again times: ", i)
    return creator.Individual(individual)


def run_ga(inp: WsnInput, params: dict, logger=None):
    if logger is None:
        raise Exception("Error: logger is None!")

    logger.info("Start running GA...")

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = 'gen', "min", "avg", "std", "max"

    constructor = Constructor(logger, inp.dict_ind2edge, inp.num_of_sensors, inp.num_of_relays, inp.num_of_relay_positions,
                              inp.all_vertex)
    toolbox = base.Toolbox()

    pool = multiprocessing.Pool(processes=4)
    toolbox.register("map", pool.map)

    toolbox.register("individual", init_individual, constructor, len(inp.dict_ind2edge.keys()),
                     inp.num_of_relay_positions)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    # toolbox.register("mate", crossover_one_point, num_positions=inp.num_of_relay_positions, rate_threshold=RATE_THRESHOLD,
    #                  indpb=0.4)
    toolbox.register("mate", tools.cxSimulatedBinary, eta=0.5)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=20)
    # toolbox.register("select", tools.selBest, k=3)
    toolbox.register("evaluate", get_fitness, params=params, max_hop=inp.max_hop, constructor=constructor)

    pop = toolbox.population(POP_SIZE)

    best_ind = toolbox.clone(pop[0])
    logger.info("init best individual: %s, fitness: %s" % (best_ind, toolbox.evaluate(best_ind)))
    prev = -1  # use for termination
    count_term = 0  # use for termination

    for g in range(N_GENS):
        t = time.time()
        record = stats.compile(pop)
        logbook.record(gen=g, **record)
        logger.info(logbook.stream)
        offsprings = map(toolbox.clone, toolbox.select(pop, len(pop) - 1))
        offsprings = algorithms.varAnd(offsprings, toolbox, CXPB, MUTPB)
        min_value = float('inf')
        invalid_ind = []
        tmp = [ind for ind in offsprings]
        tmp.append(best_ind)
        fitnesses = toolbox.map(toolbox.evaluate, tmp)
        for ind, fit in zip(tmp, fitnesses):
            if fit == float('inf'):
                invalid_ind.append(best_ind)
            else:
                invalid_ind.append(ind)
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):

            ind.fitness.values = [fit]
            if min_value > fit:
                min_value = fit
                best_ind = toolbox.clone(ind)
        b = round(min_value, 6)
        if prev == b:
            count_term += 1
        else:
            count_term = 0

        pop[:] = invalid_ind[:]

        prev = b
        if count_term == TERMINATE:
            break

    logger.info("Finished! Best individual: %s, fitness: %s" % (best_ind, min_value))
    logger.info("Best fitness: %s" % min_value)
    tmp = constructor.gen_graph(best_ind)
    # tmp2 = get_fitness(best_ind, params,inp.max_hop,constructor)
    pool.close()

    return best_ind, logbook


def mutate(gen, num_positions):
    pass


def crossover_one_point(ind1, ind2, num_positions, rate_threshold, indpb):
    size = min(len(ind1), len(ind2))
    rate = random.random()
    if rate < rate_threshold:
        for i in range(num_positions):
            if random.random() < indpb:
                ind1[i], ind2[i] = ind2[i], ind1[i]
    else:
        for i in range(num_positions, size):
            if random.random() < indpb:
                ind1[i], ind2[i] = ind2[i], ind1[i]

    return ind1, ind2


if __name__ == '__main__':
    for i in range(8, 9):
        logger = init_log()

        t = time.time()

        params, path = parse_config()
        logger.info("input path: %s" % path)
        inp = WsnInput.from_file(path)
        logger.info("num generation: %s" % N_GENS)
        logger.info("population size: %s" % POP_SIZE)
        logger.info("crossover probability: %s" % CXPB)
        logger.info("mutation probability: %s" % MUTPB)
        logger.info("info input: %s" % inp.to_dict())
        run_ga(inp, params, logger)
        logger.info("Total time: %f" %(time.time()-t))
