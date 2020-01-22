import sys
import pickle

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import graph_tool.all as gt
# GraphTool doc https://graph-tool.skewed.de/static/doc/index.html

graphmlfile = sys.argv[1]
try:
    nb_steps = int(sys.argv[2])
except:
    nb_steps = 10

g = gt.load_graph(graphmlfile)

print("Graph loaded")

deg_corr = True

states = []
for i in range(nb_steps):
    state = gt.minimize_nested_blockmodel_dl(g, deg_corr=deg_corr)
    print(i, ' over ' + str(nb_steps) + " - model entropy: "  + str(state.entropy()))

entropies = []
for i in range(nb_steps):
    entropies.append(states[i])

best_entropy = min(entropies)
best_state_index = entropies.index(best_entropy)
best_state = states[best_state_index]

print("Best entropy found:", best_entropy)
statefile = graphmlfile.replace(".graphml", ".state")
with open(statefile, "wb") as f:
    pickle.dump(best_state, f)

