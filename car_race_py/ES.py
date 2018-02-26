import numpy as np
import NET_model

class ES_model:
    def __init__(self, model, indiv):
        self.fitness = 0
        self.model = model
        self.generation = 1
        self.indiv = indiv


_population = []
_next_population = []
indiv_index = 0

def new_population(size=10):
    global _population
    for indiv in range(size):
        model = NET_model.create_model(random_weights_and_bias = True)
        _population.append(ES_model(model, indiv))


def get_next_indiv():
    global _population
    global indiv_index
    if indiv_index ==  len(_population):
        evolve_population()
        indiv_index = 0
    pop = _population.index(indiv_index)
    indiv_index += 1
    return pop


def evolve_population():
    global _population
    global _next_population
    _next_population = []
    print("evolving population from generation {} to {}".format(_population[0].generation, _population[0].generation + 1))
    _population.sort(key=lambda fit: fit.fitness, reverse=True)
    # selection
    # 30% from original sorted by fitness population
    i = 0
    for p in range(len(_population) // 3):
        p.indiv = i
        _next_population.append(p)
        i += 1
    # one randomly selected individual from the 70% less fitness original population
    p = _population[np.random.randint(len(_population) // 3 + 1, len(_population))]
    p.indiv = i
    _next_population.append(p)
    i += 1
    # crossover
    # fill _next_population with new individuals
    while len(_population) != len(_next_population):
        p = _crossover(_population[np.random.randint(0, len(_population))], _population[np.random.randint(0, len(_population))], i)
        _next_population.append(p)
        i += 1
    # mutate
    for p in _next_population:
        if np.random.random() > 0.5:
            _mutate(p)


def _crossover(indiv1, indiv2, indiv_num):
    w1 = NET_model.get_weights(indiv1.model)
    w2 = NET_model.get_weights(indiv2.model)
    new_w = NET_model.get_weights(indiv1.model)
    for i in range(0, len(w1), 2):
        # weights
        for j in range(len(w1[i])):
            for k in range(np.random.randint(len(w1[i][j]))):
                new_w[i][j][k] = w2[i][j][k]
        # bias
        for j in range(np.random.randint(len(w1[i+1]))):
            new_w[i+1][j] = w2[i+1][j]
    m = NET_model.create_model(random_weights_and_bias = True)
    NET_model.set_weights(m, new_w)
    p = ES_model(m, indiv_num)
    return p


def _simple_crossover(indiv1, indiv2, indiv_num):
    if np.random.random() > 0.5:
        new_w = NET_model.get_weights(indiv1.model)
    else:
        new_w = NET_model.get_weights(indiv2.model)
    m = NET_model.create_model(random_weights_and_bias = True)
    NET_model.set_weights(m, new_w)
    p = ES_model(m, indiv_num)
    return p


def _mutate(indiv):
    w = NET_model.get_weights(indiv.model)
    for i in range(0, len(w), 2):
        # weights
        for j in range(len(w[i])):
            for k in range(len(w[i][j])):
                if np.random.random() > 0.9:
                    w[i][j][k] += 2 * np.random.random() - 1
        # bias
        for j in range(len(w[i+1])):
            if np.random.random() > 0.9:
                w[i][j][k] += 2 * np.random.random() - 1
    NET_model.set_weights(indiv.model, w)
