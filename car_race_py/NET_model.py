from keras.models import Sequential
from keras.layers import Dense


def create_model():
    model = Sequential()
    model.add(Dense(15, activation='relu', input_dim=30))
    # model.add(Dense(10, activation='tanh'))
    model.add(Dense(5, activation='softmax'))
    return model


def train(model, x_train, y_train):
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=30, batch_size=5)


def evaluate(model, x_test, y_test):
    return model.evaluate(x_test, y_test, batch_size=5)


def predict(model, x_predict):
    return model.predict(x_predict, batch_size=5)


def load_trained_model(model, weights_path):
    model.load_weights(weights_path)
