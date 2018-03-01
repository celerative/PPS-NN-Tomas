from keras.models import Sequential
from keras.layers import Dense


class NET_model:
    def __init__(self, random_weights_and_bias=False):
        self.model = Sequential()
        _kernel_initializer = 'glorot_uniform'
        _bias_initializer = 'zeros'
        if random_weights_and_bias:
            # modify random initializer if needed
            _kernel_initializer = 'glorot_uniform'
            _bias_initializer = 'glorot_uniform'
        # Architecture of ANN can be modify here addind or removing Denses
        self.model.add(Dense(15, activation='relu', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer, input_dim=30))
        self.model.add(Dense(10, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(5, activation='softmax', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))

    def compile(self):
        self.model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

    def train(self, x_train, y_train):
        self.model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
        self.model.fit(x_train, y_train, epochs=30, batch_size=5)

    def evaluate(self, x_test, y_test):
        return self.model.evaluate(x_test, y_test, batch_size=5)

    def predict(self, x_predict):
        return self.model.predict(x_predict, batch_size=5)

    def load_trained_model(self, weights_path):
        self.model.load_weights(weights_path)

    def save_model(self, model_path):
        self.model.save(model_path)

    def get_weights(self):
        return self.model.get_weights()

    def set_weights(self, weights):
        self.model.set_weights(weights)
