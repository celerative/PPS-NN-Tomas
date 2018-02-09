import json
import numpy as np

# el archivo data.json tiene almacenadas las pociciones de los oponentes en la
# grilla con cientos de casos de ejemplo
data_in = json.load(open('raw_data.json'))

grid = np.zeros(shape=(6, 5), dtype=float, order='F')
out = np.zeros(shape=(5, 1), dtype=float, order='F')

data = []

# cargo en la lista data todos los datos del archivo data.json
for d in data_in:
    grid = np.zeros(shape=(6, 5), dtype=float, order='F')
    out = np.zeros(shape=(5, 1), dtype=float, order='F')
    for g in d:
        if (g['y'] >= 0 and g['y'] < 24):
            grid[int(g['y'] / 4)][int(g['x'] / 3)] = 1
    data.append((grid, out))

# posiciono al jugador(.5) de forma aleatoria sobre la fila 5 de la grilla
for d in data:
    d[0][5][int(np.random.rand() * 5)] = .5
    # d[0][5][1] = .5#

# busco en cada grilla si tiene solucion y calculo la salida esperada para
# dicha entrada(grilla)
data_path = []

player_pos = -1
l = []
l_final = []
data_aux = []


def calculate_path(p, yy, xx, r, score):
    global l
    global l_final
    global final_score
    # global aux_dir
    # global final_dir
    if p[yy][xx] != 0:
        if yy == 0:
            score += p[yy][xx]
            if score < final_score:
                final_score = score
                # final_dir =  aux_dir
                l_final = []
                for ll in l:
                    l_final.append(ll)
        else:
            # buscar a izquierda
            if xx < 4 and p[yy][xx + 1] < 0 and r != 1:
                # if yy == 5:
                #     aux_dir = 0
                l.append([('y', yy), ('xx', xx), ('peso', p[yy][xx])])
                calculate_path(p, yy, xx + 1, 0, score + p[yy][xx])
                del l[-1]
            # buscar a derecha
            if xx > 0 and p[yy][xx - 1] < 0 and r != 0:
                # if yy == 5:
                #     aux_dir = 1
                l.append([('y', yy), ('xx', xx), ('peso', p[yy][xx])])
                calculate_path(p, yy, xx - 1, 1, score + p[yy][xx])
                del l[-1]
            # buscar arriba
            if yy > 0 and p[yy - 1][xx] < 0:
                # if yy == 5:
                #     aux_dir = .5
                l.append([('y', yy), ('xx', xx), ('peso', p[yy][xx])])
                calculate_path(p, yy - 1, xx, .5, score + p[yy][xx])
                del l[-1]


print("Calculating expected answers from {0} data candidates:"
      .format(len(data)))
count = 0
for d in data:
    _in = d[0]
    _out = d[1]
    path = np.zeros(shape=(6, 5), dtype=float, order='F')
    np.copyto(path, _in)
    for y in range(6):
        for x in range(5):
            if _in[y][x] == 0 or _in[y][x] == .5:
                if _in[y][x] == .5:
                    player_pos = x
                if x == 0:
                    if y == 0:
                        path[y][x] = _in[y][x + 1] - 2
                    else:
                        path[y][x] = _in[y - 1][x] + _in[y][x + 1] - 2
                elif x == 4:
                    if y == 0:
                        path[y][x] = _in[y][x - 1] - 2
                    else:
                        path[y][x] = _in[y - 1][x] + _in[y][x - 1] - 2
                else:
                    if y == 0:
                        path[y][x] = _in[y][x - 1] + _in[y][x + 1] - 3
                    else:
                        path[y][x] = _in[y - 1][x] + _in[y][x - 1] + _in[y][x + 1] - 3
    final_score = 0
    # final_dir = -1
    # aux_dir = -1
    calculate_path(path, 5, player_pos, .5, 0)
    # TODO mostrar progreso de generacion de respuestas esperadas
    bar = ""
    len_data = len(str(len(data)))
    for x in range(0, int((count / len(data) * 30))):
        bar += "="
    bar += ">"
    for y in range(len(bar), 30):
        bar += "."
    print("\r{0:>{align}}/{1} [{2}]"
          .format(count, len(data), bar, align=len_data), end="")
    count += 1
    if count == len(data):
        print("\r{0}/{1} [==============================]"
              .format(count, len(data)))
    h = 0
    # busco el lugar por el que pasa de las linea 5 a la 4
    while l_final[h][0][1] != 4:
        h += 1
        try:
            k = l_final[h][1][1]
        except Exception as e:
            print(h)
            print(path)
            print(l_final)
            exit()
    _out[k][0] = 1

    if final_score != 0:
        data_aux.append(d)
        data_path.append([('path', path), ('final_score', final_score)])
data = data_aux

# verificar que no haya casos erroneos (encierror y score en cero)
for x in range(len(data)):
    for k in range(5):
        if data[x][0][5][k] == .5:
            if k == 0 or data[x][0][5][k - 1] == 1:
                if k == 4 or data[x][0][5][k + 1] == 1:
                    if data[x][0][4][k] == 1:
                        del data[x]
                        del data_path[x]
    if len(data) - 1 == x:
        break

print("ok.. no deadlocks")
for x in range(len(data)):
    if data_path[x][1][1] == 0:
        del data[x]
        del data_path[x]
    if len(data) - 1 == x:
        break

for x in range(len(data)):
    if data_path[x][1][1] == 0:
        print(x)
        print(data[x])
        print(data_path[x])
        print("scores en cero")
        exit()

print("ok.. zero scores removed")
print("{0} valid data.".format(len(data)))

while 0 == 0:
    q = int(input("Enter index to see data,"
            " -1 to exit or -2 to train the Net:\n"))
    if q == -1:
        exit()
    if q == -2:
        break
    if q < len(data):
        print(q)
        print(data[q])
        print(data_path[q])

x_train = np.empty(shape=(10000, 30), dtype=float)
y_train = np.empty(shape=(10000, 5), dtype=float)
x_test = np.empty(shape=(1000, 30), dtype=float)
y_test = np.empty(shape=(1000, 5), dtype=float)
x_predict = np.empty(shape=(1, 30), dtype=float)
if len(data) >= 11000:
    for x in range(10000):
        for i in range(6):
            for j in range(5):
                x_train[x][i * 5 + j] = data[x][0][i][j]
                if i == 0:
                    y_train[x][j] = data[x][1][j]
    for x in range(10000, 11000):
        for i in range(6):
            for j in range(5):
                x_test[x - 10000][i * 5 + j] = data[x][0][i][j]
                if i == 0:
                    y_test[x - 10000][j] = data[x][1][j]
    x = np.random.randint(11000, len(data))
    for i in range(6):
        for j in range(5):
            x_predict[0][i * 5 + j] = data[x][0][i][j]

    from keras.models import Sequential
    from keras.layers import Dense
    model = Sequential()
    model.add(Dense(15, activation='relu', input_dim=30))
    model.add(Dense(10, activation='tanh'))
    model.add(Dense(5, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='sgd',
                  metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=30, batch_size=5)
    loss_and_acc = model.evaluate(x_test, y_test, batch_size=5)
    print("Evaluated test_data results --> loss: {0:.4f} - acc: {1:.4f}"
          .format(loss_and_acc[0], loss_and_acc[1]))
    y_predict = model.predict(x_predict, batch_size=5)
    print("Predicted solution for data number {0}:".format(x))
    print("[{} , {} , {} , {} , {} ],\n"
          "[{} , {} , {} , {} , {} ],\n"
          "[{} , {} , {} , {} , {} ],\n"
          "[{} , {} , {} , {} , {} ],\n"
          "[{} , {} , {} , {} , {} ],\n"
          "[{} , {} , {} , {} , {} ]"
          .format(*x_predict[0]))
    print("Predicted results:")
    print("[{:.4f} , {:.4f} , {:.4f} , {:.4f} , {:.4f} ]"
          .format(*y_predict[0]))
    print("Expected results:")
    print("[{} , {} , {} , {} , {} ]"
          .format(*data[x][1]))
    from keras.utils import plot_model
    plot_model(model, to_file='model.png', show_shapes=True)
    model.save('model_H.h5')
    data_final = [(10000, x_train), (10000, y_train), (1000, x_test),
                  (1000, y_test), (1, x_predict)]
    save = input("Save training data? [Y/n]: ")
    if save == 'y' or save == 'Y':
        np.save("processed_data_H", data)
        print("Training data were save!")
    else:
        print("Training data weren't save!")
else:
    print("less than 11000 valid data. Abort training!")
