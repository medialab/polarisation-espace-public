import sys
import pickle

from time import time
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

best = None
best_entropy = None
for i in range(nb_steps):
    s = time()
    state = gt.minimize_nested_blockmodel_dl(g, deg_corr=deg_corr)
    entropy = state.entropy()
    print("Run #%s/%s in %ss" % (i, nb_steps, int((time()-s)*100)/100) + " - model entropy: "  + str(entropy))
    if not best_entropy or entropy < best_entropy:
        best = state
        best_entropy = entropy
        print(" -> Best so far")

statefile = graphmlfile.replace(".graphml", ".state")
with open(statefile, "wb") as f:
    pickle.dump(best, f)

