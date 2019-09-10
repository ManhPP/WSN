from deap import creator, base

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))


