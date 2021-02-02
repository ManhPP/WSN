import glob
import os
import random
import sys
import time

import numpy
from deap import base, creator, tools, algorithms
import multiprocessing

lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)

from constructor import Constructor
from fitness import get_fitness
from tree import spt, mst, encode
from utils.arg_parser import parse_config
from utils.init_log import init_log
from utils.load_input import WsnInput


creator.create("FitnessMin", base.Fitness, weights=(-1.,))
FitnessMin = creator.FitnessMin
creator.create("Individual", list, fitness=FitnessMin)

N_GENS = 200
POP_SIZE = 100
CXPB = 0.8
MUTPB = 0.2
TERMINATE = 30
RATE_THRESHOLD = 0.5
NUM_GA_RUN = 10


def random_init_individual(constructor, num_edges, num_pos):
    length = num_edges + num_pos
    individual = [random.random() for _ in range(length)]
    g = constructor.gen_graph(individual)
    i = 0
    while not g.is_connected:
        individual = [random.uniform(0, 1) for _ in range(length)]
        g = constructor.gen_graph(individual)
        i += 1
        print("init again times: ", i)
    # return creator.Individual(individual)
    return individual


def heuristic_init_individual(inp: WsnInput, constructor, rate_mst, rate_spt):
    method = random.choices(["rnd", "spt", "mst"], [1 - (rate_mst + rate_spt), rate_spt, rate_mst])[0]
    re_run = True
    num_re_run = 0
    while re_run:
        try:
            if method == "rnd":
                individual = random_init_individual(constructor, len(inp.dict_ind2edge.keys()), inp.num_of_relay_positions)
            elif method == 'spt':
                g = spt(inp)
                individual = encode(g[1], g[2], inp.num_of_relay_positions, inp.num_of_relays, inp.num_of_sensors,
                                    len(inp.dict_ind2edge))
            elif method == 'mst':
                g = mst(inp)
                individual = encode(g[1], g[2], inp.num_of_relay_positions, inp.num_of_relays, inp.num_of_sensors,
                                    len(inp.dict_ind2edge))
            re_run = False
        except:
            num_re_run += 1
            print("Rerun@!!: ", num_re_run)
            re_run = True
            if (num_re_run > 10):
                break


    return creator.Individual(individual)


def run_ga(inp: WsnInput, params: dict, logger=None):
    if logger is None:
        raise Exception("Error: logger is None!")

    logger.info("Start running GA...")

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("best", numpy.min, axis=0)

    logbook = tools.Logbook()
    logbook.header = 'ga', "best"

    constructor = Constructor(logger, inp.dict_ind2edge, inp.num_of_sensors, inp.num_of_relays,
                              inp.num_of_relay_positions,
                              inp.all_vertex)
    toolbox = base.Toolbox()

    pool = multiprocessing.Pool(processes=4)
    toolbox.register("map", pool.map)

    toolbox.register("individual", heuristic_init_individual, inp=inp, constructor=constructor,
                     rate_mst=params['rate_mst'], rate_spt=params['rate_spt'])
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    # toolbox.register("mate", crossover_one_point, num_positions=inp.num_of_relay_positions, rate_threshold=RATE_THRESHOLD,
    #                  indpb=0.4)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=20)
    # toolbox.register("select", tools.selBest, k=3)
    toolbox.register("evaluate", get_fitness, params=params, max_hop=inp.max_hop, constructor=constructor)
    result = []
    for g in range(NUM_GA_RUN):
        pop = toolbox.population(POP_SIZE)

        best_ind = toolbox.clone(pop[0])
        # logger.info("init best individual: %s, fitness: %s" % (best_ind, toolbox.evaluate(best_ind)))
        prev = -1  # use for termination
        count_term = 0  # use for termination

        for gen in range(N_GENS):
            offsprings = map(toolbox.clone, toolbox.select(pop, len(pop) - 1))
            offsprings = algorithms.varAnd(offsprings, toolbox, CXPB, MUTPB)
            min_value = float('inf')
            invalid_ind = []
            tmp = [ind for ind in offsprings]
            tmp.append(best_ind)
            fitnesses = toolbox.map(toolbox.evaluate, tmp)
            num_prev_gen_ind = 0
            for ind, fit in zip(tmp, fitnesses):
                if fit == float('inf'):
                    num_prev_gen_ind += 1
                    # invalid_ind.append(best_ind)
                else:
                    invalid_ind.append(ind)
            invalid_ind.extend(random.sample(pop, k=num_prev_gen_ind))
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
        record = stats.compile(pop)
        logbook.record(ga=g + 1, **record)
        logger.info(logbook.stream)
        result.append(min_value)
        # print(min_value)
        # logger.info("Finished! Best individual: %s, fitness: %s" % (best_ind, min_value))
        # logger.info("Best fitness: %s" % min_value)
    # tmp = constructor.gen_graph(best_ind)
    # tmp2 = get_fitness(best_ind, params,inp.max_hop,constructor)
    avg = numpy.mean(result)
    std = numpy.std(result)
    mi = numpy.min(result)
    ma = numpy.max(result)
    logger.info([mi, ma, avg, std])
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
    params, _data_path = parse_config()
    logger = init_log()
    init_rate = [(1,0),(0,1), (0,0)]
    for rate_mst, rate_spt in init_rate:
        params["rate_mst"] = rate_mst
        params["rate_spt"] = rate_spt
        logger.info("info param: %s" % params)
        
        for path in glob.glob(_data_path):
            t = time.time()
            logger.info("input path: %s" % path)
            inp = WsnInput.from_file(path)
            try:
                run_ga(inp, params, logger)
            except Exception as e:
                logger.info("Error: %s" % e)
            logger.info("Total time: %f" % (time.time() - t))
