import numpy as np
import NET_model

'''
ES is a module to create populations of keras directional models.
Allows to iterate over the population and evolve it when gets to the end.

Works over 1 dim keras leyers, and perform crossover and mutatios on weights and bias from all layers.
The model is get from NET_model module to abstract it's implamentation.

Every individual is and ES_indiv instance, and has it's own fitness.

'''


class ES_indiv:
    '''
        # Individual from ES populations

        Atributes:
        * fitness --> score to evalueate indiv
        * model --> NET_model representation of ANN (see NET_model for more info)
        * indiv_id --> number to identificate indiv in generation
        * generation --> number for the generations witch the indiv belongs
    '''
    def __init__(self, model, indiv_id, generation=1):
        self.fitness = 0
        self.model = model
        self.indiv_id = indiv_id
        self.generation = generation


_population = []
_next_population = []
_generation_index = 0
_indiv_index = 0


def new_population(size=10, seed=None, verbose=False):
    '''
        # Create a new populations to evolve and train

        Arguments:
            size: of the population
            seed: list of ES_indiv to add and generate population, should have equeal or less individuals than size number
            verbose: show results
    '''
    global _population
    global _generation_index
    _generation_index = 0
    global _indiv_index
    _indiv_index = 0
    if seed is None:
        for indiv_id in range(size):
            model = NET_model.NET_model(random_weights_and_bias=True)
            _population.append(ES_indiv(model, indiv_id))
    else:
        i = 0
        for s in seed:
            s.fitness = 0
            s.indiv_id = i
            s.generation = _generation_index
            _population.append(s)
            i += 1
        while len(_population) != size:
            p = _crossover(_population[np.random.randint(0, len(_population))], _population[np.random.randint(0, len(_population))], i, verbose)
            _population.append(p)
            i += 1
    if verbose:
        print("New generation of {} individuals created".format(len(_population)))


def get_next_indiv(simple_crossover=False, verbose=False):
    '''
        # Return next indiv from populations

        if population reachs the end, automaticaly evolve it and return first indiv from next generation

        Arguments:
            simple_crossover: generates clone from one random parent insted of cross parents NET_models
            verbose: show results

        Return: next ES_indiv from population
    '''
    global _population
    global _indiv_index
    if _indiv_index == len(_population):
        if verbose:
            print("End of population...")
        evolve_population(simple_crossover=simple_crossover, verbose=verbose)
        _indiv_index = 0
    pop = _population[_indiv_index]
    if verbose:
        print("Next individual ID: {}".format(pop.indiv_id))
    _indiv_index += 1
    return pop


def get_indiv(indiv_id, verbose=False):
    '''
        # Return indiv by id from populations

        if indiv_id is out of range from population size, return None.

        Arguments:
            indiv_id: id or index for individual in population list
            verbose: show results

        Return: ES_indiv with indiv_id given from population
    '''
    global _population
    if indiv_id < len(_population):
        pop = _population[indiv_id]
        return pop
    else:
        if verbose:
            print("Index {} out of range".format(indiv_id))
        return None


def evolve_population(simple_crossover=False, verbose=False):
    '''
        # Create next generation from best indivs, sorting by fitness

        Arguments:
            simple_crossover: generates clone from one random parent insted of cross parents NET_models
            verbose: show results
    '''
    global _population
    global _next_population
    global _generation_index
    _generation_index += 1
    _next_population = []
    if verbose:
        print("Evolving population from generation {}:".format(_population[0].generation))
    _population.sort(key=lambda fit: fit.fitness, reverse=True)
    #####################
    # save best model
    _population[0].model.save_model("ES_models/ES_gen{:0>2}_fit{:0>3}.h5".format(_population[0].generation, _population[0].fitness))
    #####################
    # selection
    # 25% from original sorted by fitness population
    i = 0
    for index in range(len(_population) // 4):
        p = _population[index]
        if verbose:
            print("Individual number {} selected, with fit of {}".format(p.indiv_id, p.fitness))
        p.fitness = 0
        p.indiv_id = i
        p.generation = _generation_index
        _next_population.append(p)
        i += 1
    #####################
    # # one randomly selected individual from the 70% less fitness original population
    # p = _population[np.random.randint(len(_population) // 3 + 1, len(_population))]
    # if verbose: print("Individual number {} selected randomly, with fit of {}".format(p.indiv_id, p.fitness))
    # p.fitness = 0
    # p.indiv_id = i
    # p.generation = _generation_index
    # _next_population.append(p)
    # i += 1
    #####################
    # crossover
    # fill _next_population with new individuals
    if verbose:
        print("Completing population doing crossover...")
    while len(_population) != len(_next_population):
        if simple_crossover:
            p = _simple_crossover(_next_population[np.random.randint(0, len(_next_population))], _next_population[np.random.randint(0, len(_next_population))], i, verbose)
        else:
            p = _crossover(_next_population[np.random.randint(0, len(_next_population))], _next_population[np.random.randint(0, len(_next_population))], i, verbose)
        _next_population.append(p)
        i += 1
    #####################
    # mutate
    if verbose:
        print("Making mutations randomly over the entire population...")
    for p in _next_population:
        if np.random.random() > 0.5:
            _mutate(p, verbose)
    _population = _next_population
    if verbose:
        print("New population created!")


def _crossover(indiv1, indiv2, indiv_num, verbose=False):
    '''
        # Create new ES_indiv from two selected parents

        The crossover child have random number of weights and bias from each weights and bias parent1's vector and the rest from parent2

        Arguments:
            indiv1: ES_indiv to crossover
            indiv2: ES_indiv to crossover
            indiv_num: ID for new ES_indiv
            verbose: show results

        Return: new ES_indiv
    '''
    if verbose:
        print("Performing crossover with individuals {} and {}:".format(indiv1.indiv_id, indiv2.indiv_id))
    global _generation_index
    w1 = indiv1.model.get_weights()
    w2 = indiv2.model.get_weights()
    new_w = indiv1.model.get_weights()
    for i in range(0, len(w1), 2):
        # weights
        for j in range(len(w1[i])):
            index = np.random.randint(len(w1[i][j]))
            if verbose:
                print("Cuting weights from neuron {} of layer {} to layer {} ({} inputs --> {} outputs) on index {}".format(j, i//2, i//2+1, len(w1[i]), len(w1[i][j]), index))
            for k in range(index):
                new_w[i][j][k] = w2[i][j][k]
        # bias
        index = np.random.randint(len(w1[i+1]))
        if verbose:
            print("Cuting bias from layer {} of {} neurons on index {}".format(i//2, len(w1[i+1]), index))
        for j in range(index):
            new_w[i+1][j] = w2[i+1][j]
    m = NET_model.NET_model(random_weights_and_bias=True)
    m.set_weights(new_w)
    p = ES_indiv(m, indiv_num, _generation_index)
    return p


def _simple_crossover(indiv1, indiv2, indiv_num, verbose=False):
    '''
        # Create new ES_indiv from two selected parents

        The SIMPLE crossover child is a direct clone from one of is parents

        Arguments:
            indiv1: ES_indiv to crossover
            indiv2: ES_indiv to crossover
            indiv_num: ID for new ES_indiv
            verbose: show results

        Return: new ES_indiv
    '''
    if verbose:
        print("Performing SIMPLE crossover with individuals {} and {}:".format(indiv1.indiv_id, indiv2.indiv_id))
    global _generation_index
    if np.random.random() > 0.5:
        new_w = indiv1.model.get_weights()
    else:
        new_w = indiv2.model.get_weights()
    m = NET_model.NET_model(random_weights_and_bias=True)
    m.set_weights(new_w)
    p = ES_indiv(m, indiv_num, _generation_index)
    return p


def _mutate(indiv, verbose=False):
    '''
        # Perform random mutations on some weights and bias from the individual

        Mutations possibilities are from 10% for each weights and bias.

        Arguments:
            indiv: ES_indiv to mutate
            verbose: show results
    '''
    w = indiv.model.get_weights()
    w_mutated = 0
    b_mutated = 0
    for i in range(0, len(w), 2):
        # weights
        for j in range(len(w[i])):
            for k in range(len(w[i][j])):
                if np.random.random() > 0.9:
                    w_mutated += 1
                    w[i][j][k] += 2 * np.random.random() - 1
        # bias
        for j in range(len(w[i+1])):
            if np.random.random() > 0.9:
                b_mutated += 1
                w[i][j][k] += 2 * np.random.random() - 1
    indiv.model.set_weights(w)
    if verbose:
        print("Mutate randomly {} weights and {} bias on individual {}".format(w_mutated, b_mutated, indiv.indiv_id))
