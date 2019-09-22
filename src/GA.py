import random

from deap import base, creator, tools, algorithms
import numpy as np
from src.fitness import get_fitness
from utils.load_input import WsnInput
from src.constructor import Constructor

creator.create("FitnessMin", base.Fitness, weights=(-1.,))
FitnessMin = creator.FitnessMin
creator.create("Individual", list, fitness=FitnessMin)

N_GENS = 200
POP_SIZE = 300
CXPB = 0.8
MUTPB = 0.2
TERMINATE = 30


def init_individual(num_sensors, num_pos):
    length = 3 * (num_sensors + num_pos + 1)
    individual = list(np.random.uniform(0, 1, size=(length,)))
    return creator.Individual(individual)


def run_ga(inp: WsnInput):
    constructor = Constructor(inp.num_of_sensors, inp.num_of_relays, inp.num_of_relay_positions, inp.all_vertex)
    toolbox = base.Toolbox()

    toolbox.register("individual", init_individual, inp.num_of_sensors, inp.num_of_relay_positions)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxUniform, indpb=0.2)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=20)
    # toolbox.register("select", tools.selBest, k=3)
    toolbox.register("evaluate", get_fitness, max_hop=inp.max_hop, constructor=constructor)

    pop = toolbox.population(POP_SIZE)
    best_ind = toolbox.clone(pop[0])
    print("init fitness: ", toolbox.evaluate(best_ind))
    prev = -1  # use for termination
    count_term = 0  # use for termination

    for g in range(N_GENS):
        offsprings = map(toolbox.clone, toolbox.select(pop, len(pop)))
        offsprings = algorithms.varAnd(offsprings, toolbox, CXPB, MUTPB)
        min_value = float('inf')
        invalid_ind = []
        tmp = [ind for ind in offsprings if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, tmp)
        # fit = list(fitnesses)
        for ind, fit in zip(tmp, fitnesses):
            if fit == float('inf'):
                invalid_ind.append(best_ind)
            else:
                invalid_ind.append(ind)
        fitnesses_main = toolbox.map(toolbox.evaluate, invalid_ind)
        # fit = list(fitnesses_main)
        for ind, fit in zip(invalid_ind, fitnesses_main):

            ind.fitness.values = [fit]
            if min_value > fit:
                min_value = fit
                best_ind = toolbox.clone(ind)
        print(best_ind)
        b = round(min_value, 6)
        if prev == b:
            count_term += 1
        else:
            count_term = 0
        print("min value this pop %d : %f " % (g, min_value))
        pop[:] = invalid_ind[:]
        prev = b
        if count_term == TERMINATE:
            break

    return best_ind


if __name__ == '__main__':
    inp = WsnInput.from_file('/home/manhpp/Documents/Code/WSN/data/ga-dem1_r25_1.in')
    run_ga(inp)
