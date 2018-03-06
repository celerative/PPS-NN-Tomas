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
    def __init__(self, model, reward_function, batch_size=10, history_size=100, verbose=False):
        if model is None:
            model = NET_model.NET_model()
        else:
            self.model = model
        self.reward_function = reward_function
        self.batch_size = batch_size
        self.history_size = history_size
        self.history = []
        self.verbose = verbose

    def replay_train(self):
        pass

    def get_batch(self):
        len_history = len(self.history)
        in_shape_size = self.model.input_shape
        out_shape_size = self.model.output_shape
        train_size = (min(len_history, self.batch_size))
        train_x = np.zeros(train_size, in_shape_size)
        train_y = np.zeros(train_size, out_shape_size)
        for i, idx in enumerate(np.random.randint(0, len_history, size=train_x.shape[0])):
            state_now, action, reward, state_next = self.memory[idx][0]
            game_over = self.memory[idx][1]

            train_x[i] = state_now
            # There should be no target values for actions not taken.
            # Thou shalt not correct actions not taken #deep
            train_y[i] = self.model.predict(state_now)[0]
            Q_sa = np.max(self.model.predict(state_next)[0])
            if game_over:  # if game_over is True
                train_y[i][action] = reward
            else:
                # reward_t + gamma * max_a' Q(s', a')
                train_y[i][action] = reward + self.discount * Q_sa
        return train_x, train_y
