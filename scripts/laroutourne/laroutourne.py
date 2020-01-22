import sys
import pickle

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import graph_tool.all as gt
# GraphTool doc https://graph-tool.skewed.de/static/doc/index.html

graphmlfile = sys.argv[1]
nb_steps = sys.argv[2]
g=gt.load_graph(graphmlfile)

print("Graph loaded")

deg_corr = True

states=[]
for i in in range(nb_steps):
	state = gt.minimize_nested_blockmodel_dl(g, deg_corr=deg_corr)
	print(i,' over ' + str(nb_steps) + " - model entropy: "  + str(state.entropy()))
	
entropies=[]
for i in in range(nb_steps):
	entropies.append(states[i])

best_entropy=min(entropies)
best_state_index=entropies.index(best_entropy)
best_state = states[best_state_index]

statefile = graphmlfile.replace(".graphml", '_'+str(best_entropy)+".state")
with open(statefile, "wb") as f:
	pickle.dump(best_state, f)

