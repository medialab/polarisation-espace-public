import sys
import pickle
from time import time
from argparse import ArgumentParser

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import graph_tool.all as gt
from draw_wheel import draw_from_state
# GraphTool doc https://graph-tool.skewed.de/static/doc/index.html


def roll(graphmlfile, nb_attempts, min_clusters, max_clusters, deg_corr=True):
    g = gt.load_graph(graphmlfile)

    print("Graph loaded")
    best = None
    best_entropy = None
    for i in range(nb_attempts):
        s = time()
        state = gt.minimize_nested_blockmodel_dl(g)#, deg_corr=deg_corr, B_min=min_clusters, B_max=max_clusters)
        entropy = state.entropy()
        print("Run #%s/%s in %ss" % (i+1, nb_attempts, int((time()-s)*100)/100) + " - model entropy: "  + str(entropy))
        if not best_entropy or entropy < best_entropy:
            best = state
            best_entropy = entropy
            print(" -> Best so far")

    max_clusters_str = ""
    if max_clusters:
        max_clusters_str = "-%s_max_clusters" % max_clusters

    statefile = graphmlfile.replace(".graphml", max_clusters_str+"-entropy_%s.state" % round(entropy))
    with open(statefile, "wb") as f:
        pickle.dump(best, f)

    print("State saved in", statefile)
    return statefile


def write_blocks_csv(statefile):
    with open(statefile, "rb") as f:
        state = pickle.load(f)

    levels = state.get_levels()

    for s in levels:
        print(s)

    node_assignment = {}
    for i in range(state.g.num_vertices()):
        for h in range(3):
            r = levels[h].get_blocks()[i]
            node_assignment.setdefault(state.g.vp["label"][i], []).append(str(r))

    blocks_csv_file = statefile.replace(".state", "-blocks.csv")
    with open(blocks_csv_file, "w") as f:
        print("label,level_0,level_1,level_2", file=f)
        for label in node_assignment:
            print('"%s",' % label.replace('"', '""') + ','.join(node_assignment[label]), file=f)


def compute():
    "Compute SBM, write CSV of blocks and draw wheel"

    parser = ArgumentParser(prog='laroutourne')
    parser.add_argument('graphmlfile', help='GraphML file to process', type=str)
    parser.add_argument('-n', '--nb-attempts', help='number of SBM runs to try', type=int, default=10)
    parser.add_argument('-m', '--min-clusters', help='minimum number of clusters desired', type=int)
    parser.add_argument('-M', '--max-clusters', help='maximum number of clusters desired', type=int)
    parser.add_argument('-w', '--img-width', help='dimensions of the image of the wheel to generate', type=int, default=3072)
    args = parser.parse_args()

    statefile = roll(args.graphmlfile, args.nb_attempts, args.min_clusters, args.max_clusters)
    draw_from_state(statefile, args.img_width)
    write_blocks_csv(statefile)


if __name__ == "__main__":
    compute()
