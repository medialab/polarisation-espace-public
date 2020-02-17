import sys
import pickle

from time import time
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import graph_tool.all as gt
from draw_wheel import draw_from_state
# GraphTool doc https://graph-tool.skewed.de/static/doc/index.html


def roll(graphmlfile, nb_attempts, max_clusters, deg_corr=True):
    g = gt.load_graph(graphmlfile)

    print("Graph loaded")
    best = None
    best_entropy = None
    for i in range(nb_attempts):
        s = time()
        state = gt.minimize_nested_blockmodel_dl(g, deg_corr=deg_corr, B_max=max_clusters)
        entropy = state.entropy()
        print("Run #%s/%s in %ss" % (i+1, nb_attempts, int((time()-s)*100)/100) + " - model entropy: "  + str(entropy))
        if not best_entropy or entropy < best_entropy:
            best = state
            best_entropy = entropy
            print(" -> Best so far")

    statefile = graphmlfile.replace(".graphml", "-entropy_%s.state" % round(entropy))
    with open(statefile, "wb") as f:
        pickle.dump(best, f)
    print("State saved in", statefile)
    return statefile


if __name__ == "__main__":
    graphmlfile = sys.argv[1]

    try:
        nb_attempts = int(sys.argv[2])
    except:
        nb_attempts = 10

    try:
        max_clusters = int(sys.argv[3])
    except:
        max_clusters = None

    try:
        img_width = int(sys.argv[4])
    except:
        img_width = 3072

    statefile = roll(graphmlfile, nb_attempts, max_clusters)
    draw_from_state(statefile, img_width)
