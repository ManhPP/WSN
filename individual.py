from deap import base, creator

creator.create("FitnessMin", base.Fitness,weights=(-1.,))
FitnessMin = creator.FitnessMin


class Individual(list):
    pass
