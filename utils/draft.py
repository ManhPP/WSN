import random


def cxSimulatedBinary(ind1, ind2, eta, upper_bound=1., lower_bound=0.):
    """Executes a simulated binary crossover that modify in-place the input
    individuals. The simulated binary crossover expects :term:`sequence`
    individuals of floating point numbers.

    :param lower_bound:
    :param upper_bound:
    :param ind1: The first individual participating in the crossover.
    :param ind2: The second individual participating in the crossover.
    :param eta: Crowding degree of the crossover. A high eta will produce
                children resembling to their parents, while a small eta will
                produce solutions much more different.
    :returns: A tuple of two individuals.

    This function uses the :func:`~random.random` function from the python base
    :mod:`random` module.
    """
    for i, (x1, x2) in enumerate(zip(ind1, ind2)):
        rand = random.random()
        if rand <= 0.5:
            beta = 2. * rand
        else:
            beta = 1. / (2. * (1. - rand))
        beta **= 1. / (eta + 1.)
        i1 = 0.5 * (((1 + beta) * x1) + ((1 - beta) * x2))
        i2 = 0.5 * (((1 - beta) * x1) + ((1 + beta) * x2))

        if lower_bound < i1 < upper_bound:
            ind1[i] = i1
        else:
            ind1[i] = random.uniform(0, 1)
        if lower_bound < i2 < upper_bound:
            ind2[i] = i2
        else:
            ind2[i] = random.uniform(0, 1)

    return ind1, ind2


if __name__ == '__main__':
    a = [0.1, 0.2, 0.3]
    b = [0.4, 0.5, 0.6]
    x, y = cxSimulatedBinary(a, b, 0.1)
    print(x)
    print(y)
