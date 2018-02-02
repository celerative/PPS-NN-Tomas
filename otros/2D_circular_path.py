import numpy as np

PATH_LEN = 10
PATH = []
X_MAX = 0
Y_MAX = 0
X = 0
Y = 0

for p in range(PATH_LEN - 1):
    PATH.append((X, Y))
    if p < PATH_LEN / 4:
        X += np.random.randint(10)
        Y = np.random.randint(5)
    elif p < (PATH_LEN / 4) * 2:
        X = np.random.randint(5)
        Y += np.random.randint(10)
    elif p < (PATH_LEN / 4) * 3:
        X -= np.random.randint(10)
        Y = np.random.randint(5)
    elif p < PATH_LEN:
        X = np.random.randint(5)
        Y -= np.random.randint(10)
PATH.append(PATH[0])
print(PATH)
