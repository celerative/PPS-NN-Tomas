import numpy as np
import NET_model

'''
RL is a module to

'''


class RL_indiv:
    '''
        # Individual from RL populations

        Atributes:
        * model --> NET_model representation of ANN (see NET_model for more info)
    '''
    def __init__(self, model=None, outcome_activation="relu", batch_size=10, discount=.9, history_size=100, game_over_state=True, verbose=False):
        if model is None:
            model = NET_model.NET_model()
        else:
            self.model = model
        self.activation = outcome_activation
        self.batch_size = batch_size
        self.discount = discount
        self.history_size = history_size
        self.history = []
        self.game_over_state = game_over_state
        self.verbose = verbose

    def replay_train(self):
        train_x, train_y = self._get_batch()
        self.model.train_on_batch(train_x, train_y)

    def save_itaration(self, state_now, action_index, reward, state_next, game_over=False):
        if self.game_over_state:
            self.history.append([state_now, action_index, reward, state_next, game_over])
        else:
            self.history.append([state_now, action_index, reward, state_next, False])
        if len(self.history) > self.history_size:
            del self.history[0]

    def _get_batch(self):
        len_history = len(self.history)
        train_size = (min(len_history, self.batch_size))
        train_x = np.zeros((train_size, self.model.input_shape))
        train_y = np.zeros((train_size, self.model.output_shape))
        if self.activation == "relu":
            for i, i_history in enumerate(np.random.randint(0, len_history, size=train_size)):
                state_now, action_index, reward, state_next, game_over = self.history[i_history]
                train_x[i] = state_now
                train_y[i] = self.model.predict(state_now)[0]
                Q_sa = np.max(self.model.predict(state_next)[0])
                if game_over:  # if game_over is True
                    train_y[i][action_index] = reward
                else:
                    # reward_t + gamma * max_a' Q(s', a')
                    train_y[i][action_index] = reward + self.discount * Q_sa
        elif self.activation == "softmax":
            i = 0
            while len(train_x) < train_size:
                state_now, action_index, reward, state_next, game_over = self.history[np.random.randint(0, len_history)]
                if reward == 1:
                    train_x[i] = state_now
                    if game_over:  # if game_over is True (with reward 1 the game ends on win)
                        train_y[i][action_index] = reward
                    else:
                        # the action taken was correct
                        train_y[i][action_index] = reward
                    i += 1
        return train_x, train_y
