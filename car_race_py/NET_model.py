from keras.models import Sequential
from keras.layers import Dense


class NET_model:
    '''
        # Keras secuential model interface for ES, RL or sgd training

        The architecture for ANN is define in constructor, easily editable by adding layers (Denses) in it.

        Argument:
        * input_size: number for 1 dim input layer (input neurons), by default is 30.
        * random_weights_and_bias: generate random weights and bias if True or random weights and zeros bias if False, by default is False.
    '''
    def __init__(self, input_shape=30, output_shape=5, random_weights_and_bias=False):
        self.model = Sequential()
        _kernel_initializer = 'glorot_uniform'
        _bias_initializer = 'zeros'
        self.input_shape = input_shape
        self.output_shape = output_shape
        if random_weights_and_bias:
            # modify random initializer if needed
            _kernel_initializer = 'glorot_uniform'
            _bias_initializer = 'glorot_uniform'
        # Architecture of ANN can be modify here adding or removing Denses
        self.model.add(Dense(512, activation='relu', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer, input_dim=input_shape))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(256, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(128, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self.model.add(Dense(output_shape, activation='softmax', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
        self._compiled = False

    def compile(self):
        '''
            # Compile Keras model

            Some actions needs to have the model compiled to be perform
        '''
        self.model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
        self._compiled = True

    def train(self, x_train, y_train):
        '''
            # Train Keras model with SGD strategy

            Given data must have the correct structure for the Keras model in use.

            Arguments:
                x_train: numpy array with input data for model
                y_train: numpy array with output data for model

            Return: Loss and Acc list perform by test data set
        '''
        if not self._compiled:
            self.compile()
        return self.model.fit(x_train, y_train, epochs=30, batch_size=5)

    def train_on_batch(self, x_train, y_train):
        '''
            # Train Keras model with single gradient update on a single batch of data with SGD strategy

            Given data must have the correct structure for the Keras model in use.

            Arguments:
                x_train: numpy array with input data for model
                y_train: numpy array with output data for model

            Return: Loss and Acc list perform by test data set
        '''
        if not self._compiled:
            self.compile()
        return self.model.train_on_batch(x_train, y_train)

    def evaluate(self, x_test, y_test):
        '''
            # Evalueate Keras model

            Given data must have the correct structure for the Keras model in use

            Arguments:
                x_test: numpy array with input data for model
                y_test: numpy array with output data for model

            Return: Loss and Acc list perform by test data set
        '''
        return self.model.evaluate(x_test, y_test, batch_size=5)

    def predict(self, x_predict):
        '''
            # Run Keras model and predict output data from inputs

            Given data must have the correct structure for the Keras model in use

            Arguments:
                x_predict: numpy array with input data for model

            Return: numpy array with output data from model
        '''
        return self.model.predict(x_predict, batch_size=5)

    def load_model(self, model_path):
        '''
            # Load Keras model from file

            Arguments:
                model_path: file path and name
        '''
        self.model.load_weights(model_path)

    def save_model(self, model_path):
        '''
            # Save Keras model to file

            Arguments:
                model_path: file path and name
        '''
        self.model.save(model_path)

    def get_weights(self):
        '''
            # Return weights and bias from Keras model

            Return: list of arrays with weights and bias
        '''
        return self.model.get_weights()

    def set_weights(self, weights):
        '''
            # Set weights and bias to Keras model

            Arguments:
                weights: list of arrays with weights and bias
        '''
        self.model.set_weights(weights)
