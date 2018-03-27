# PPS-NN-Tomas

This repository contain proof for supervised an unsupervised training on keras sequential CNNs with specifics data sets, Evolution Strategies and Reinforce Learning.

The example chosen to perform proof was the game from Brick-Games Car Race (picture). The solution is approach by a CNN with an input layer of 30 neurons and a 5 neurons output layer.

* Input: is an 1 dimension array witch represent a 6x5 grid with Ones on enemy positions, .5 value on player's position and Zeros to fill the empty space.
* Output: represent the 5 possibles position for the player, when the max value is the desire answer. It was implemented with a Softmax activation function.


## Car Race



## Car Race Py



## CUDA Installation

Contain information to perform properly installation of CUDA and other dependencies to use the GPU on training batches.
