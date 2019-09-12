import random

from deap import base, creator, tools
import numpy as np

creator.create("FitnessMin", base.Fitness, weights=(-1.,))
FitnessMin = creator.FitnessMin
creator.create("Individual", np.ndarray, fitness=FitnessMin)


def init_individual(num_sensors, num_pos):
    length = 3 * (num_sensors + num_pos + 1)
    individual = np.random.uniform(0, 1, size=(length,))
    return creator.Individual(individual)


def get_sub_list(src_list, n):
    dst_list = []
    b_list = list(src_list)
    for i in range(n):
        x = random.choice(b_list)
        dst_list.append(x)
        b_list.remove(x)
    return dst_list


def run_ga():
    pass
