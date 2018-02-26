from keras.models import Sequential
from keras.layers import Dense


def create_model(random_weights_and_bias = False):
    model = Sequential()
    _kernel_initializer = 'glorot_uniform'
    _bias_initializer = 'zeros'
    if random_weights_and_bias:
        # modify random initializer if needed
        _kernel_initializer = 'glorot_uniform'
        _bias_initializer = 'glorot_uniform'
    model.add(Dense(15, activation='relu', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer, input_dim=30))
    # model.add(Dense(10, activation='tanh', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
    model.add(Dense(5, activation='softmax', kernel_initializer=_kernel_initializer, bias_initializer=_bias_initializer))
    return model


def compile(model):
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])


def train(model, x_train, y_train):
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=30, batch_size=5)


def evaluate(model, x_test, y_test):
    return model.evaluate(x_test, y_test, batch_size=5)


def predict(model, x_predict):
    return model.predict(x_predict, batch_size=5)


def load_trained_model(model, weights_path):
    model.load_weights(weights_path)


def save_model(model, model_path):
    model.save(model_path)


def get_weights(model):
    return model.get_weights()


def set_weights(model, weights):
    model.set_weights(weights)
