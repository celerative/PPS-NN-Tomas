import NET_model
import ES
m2 = NET_model.create_model(True)
m1 = NET_model.create_model(True)
w1 = NET_model.get_weights(m1)
w2 = NET_model.get_weights(m2)
e2 = ES.ES_model(m2 ,2)
e1 = ES.ES_model(m1 ,1)
e3 = ES._crossover(e1, e2, 3, True)


import NET_model
import ES
ES.new_population(10, True)
p = ES.get_next_indiv(True)
p.fitness = 5
p = ES.get_next_indiv(True)
p.fitness = 45
p = ES.get_next_indiv(True)
p.fitness = 3
p = ES.get_next_indiv(True)
p.fitness = 33
p = ES.get_next_indiv(True)
p.fitness = 20
p = ES.get_next_indiv(True)
p.fitness = 22
p = ES.get_next_indiv(True)
p.fitness = 26
p = ES.get_next_indiv(True)
p.fitness = 80
p = ES.get_next_indiv(True)
p.fitness = 8
p = ES.get_next_indiv(True)
p.fitness = 9
p = ES.get_next_indiv(True)
