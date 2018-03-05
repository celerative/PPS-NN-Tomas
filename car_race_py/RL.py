import numpy as np
import NET_model

'''
ES is a module to create populations of keras directional models.
Allows to iterate over the population and evolve it when gets to the end.

Works over 1 dim keras leyers, and perform crossover and mutatios on weights and bias from all layers.
The model is get from NET_model module to abstract it's implamentation.

Every individual is and ES_indiv instance, and has it's own fitness.

'''


class RL_indiv:
    '''
        # Individual from RL populations

        Atributes:
        * model --> NET_model representation of ANN (see NET_model for more info)
    '''
    def __init__(self, model, verbose=False):
        self.model = model
        self.verbose = verbose
