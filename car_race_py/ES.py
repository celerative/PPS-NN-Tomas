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
        * indiv_obj --> to attach some object to individual
    '''
    def __init__(self, model, indiv_id, generation=1, indiv_obj=None):
        self.fitness = 0
        self.model = model
        self.indiv_id = indiv_id
        self.generation = generation
        self.game_over = False
        self.indiv_obj = indiv_obj


class Population:
    '''
        # Create a new populations to evolve and train

        Atributes:
        * size --> size of the population

        Arguments:
            size: of the population
            seed: list of ES_indiv to add and generate population, should have equeal or less individuals than size number
            verbose: show results
    '''
    def __init__(self, size=10, seed=None, verbose=False):
        self.size = size
        self._population = []
        self._generation_index = 0
        self._indiv_index = 0
        if seed is None:
            for indiv_id in range(size):
                model = NET_model.NET_model(random_weights_and_bias=True)
                self._population.append(ES_indiv(model, indiv_id))
        else:
            i = 0
            for s in seed:
                s.fitness = 0
                s.indiv_id = i
                s.generation = self._generation_index
                self._population.append(s)
                i += 1
            while len(self._population) != size:
                p = self._crossover(self._population[np.random.randint(0, len(self._population))], self._population[np.random.randint(0, len(self._population))], i, verbose)
                self._population.append(p)
                i += 1
        if verbose:
            print("New generation of {} individuals created".format(len(self._population)))

    def population_is_dead(self):
        '''
            # Return if al individuals from population are dead

            Return: True if population is dead
        '''
        for p in self._population:
            if not p.game_over:
                return False
        return True

    def get_next_indiv(self, simple_crossover=False, verbose=False):
        '''
            # Return next indiv from populations

            this method is to evaluate individuals one by one.
            if population reachs the end, automaticaly evolve it and return first indiv from next generation.

            Arguments:
                simple_crossover: generates clone from one random parent insted of cross parents NET_models
                verbose: show results

            Return: next ES_indiv from population
        '''
        if self._indiv_index == len(self._population):
            if verbose:
                print("End of population...")
            self.evolve_population(simple_crossover=simple_crossover, verbose=verbose)
            self._indiv_index = 0
        pop = self._population[self._indiv_index]
        if verbose:
            print("Next individual ID: {}".format(pop.indiv_id))
        self._indiv_index += 1
        return pop

    def get_indiv(self, indiv_id, verbose=False):
        '''
            # Return indiv by id from populations

            if indiv_id is out of range from population size, return None.

            Arguments:
                indiv_id: id or index for individual in population list
                verbose: show results

            Return: ES_indiv with indiv_id given from population
        '''
        if indiv_id < len(self._population):
            pop = self._population[indiv_id]
            return pop
        else:
            if verbose:
                print("Index {} out of range".format(indiv_id))
            return None

    def evolve_population(self, simple_crossover=False, verbose=False):
        '''
            # Create next generation from best indivs, sorting by fitness

            Arguments:
                simple_crossover: generates clone from one random parent insted of cross parents NET_models
                verbose: show results
        '''
        self._generation_index += 1
        _next_population = []
        if verbose:
            print("Evolving population from generation {}:".format(self._population[0].generation))
        self._population.sort(key=lambda fit: fit.fitness, reverse=True)
        #####################
        # save best model
        self._population[0].model.save_model("ES_models/ES_gen{:0>2}_fit{:0>3}.h5".format(self._population[0].generation, self._population[0].fitness))
        #####################
        # selection
        # 25% from original sorted by fitness population
        parents_count = len(self._population) // 4
        i = 0
        for index in range(parents_count):
            p = self._population[index]
            if verbose:
                print("Individual number {} selected, with fit of {}".format(p.indiv_id, p.fitness))
            p.fitness = 0
            p.indiv_id = i
            p.generation = self._generation_index
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
        while len(self._population) != len(_next_population):
            if simple_crossover:
                p = self._simple_crossover(_next_population[np.random.randint(0, parents_count)], _next_population[np.random.randint(0, parents_count)], i, verbose)
            else:
                p = self._crossover(_next_population[np.random.randint(0, parents_count)], _next_population[np.random.randint(0, parents_count)], i, verbose)
            _next_population.append(p)
            i += 1
        #####################
        # mutate
        if verbose:
            print("Making mutations randomly over the entire population...")
        # for p in _next_population:
        for i in range(parents_count, self.size):
            if np.random.random() > 0.5:
                self._mutate(_next_population[i], verbose)
        #####################
        self._population = _next_population
        if verbose:
            print("New population created!")

    def _crossover(self, indiv1, indiv2, indiv_num, verbose=False):
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
        self._generation_index
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
        p = ES_indiv(m, indiv_num, self._generation_index)
        return p

    def _simple_crossover(self, indiv1, indiv2, indiv_num, verbose=False):
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
        self._generation_index
        if np.random.random() > 0.5:
            new_w = indiv1.model.get_weights()
        else:
            new_w = indiv2.model.get_weights()
        m = NET_model.NET_model(random_weights_and_bias=True)
        m.set_weights(new_w)
        p = ES_indiv(m, indiv_num, self._generation_index)
        return p

    def _mutate(self, indiv, verbose=False):
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
                        if np.random.random() > 0.5:
                            w[i][j][k] += w[i][j][k] * 0.05
                        else:
                            w[i][j][k] -= w[i][j][k] * 0.05
                        # w[i][j][k] = 2 * np.random.random() - 1
            # bias
            for j in range(len(w[i+1])):
                if np.random.random() > 0.9:
                    b_mutated += 1
                    if np.random.random() > 0.5:
                        w[i+1][j] += w[i+1][j] * 0.05
                    else:
                        w[i+1][j] -= w[i+1][j] * 0.05
                    # w[i+1][j] = 2 * np.random.random() - 1
        indiv.model.set_weights(w)
        if verbose:
            print("Mutate randomly {} weights and {} bias on individual {}".format(w_mutated, b_mutated, indiv.indiv_id))
