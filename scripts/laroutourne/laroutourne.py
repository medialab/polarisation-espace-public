import sys
import pickle

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import graph_tool.all as gt
# GraphTool doc https://graph-tool.skewed.de/static/doc/index.html

graphmlfile = sys.argv[1]

if len(sys.argv) > 2:
    NB_ITERS = int(sys.argv[2])
else:
    NB_ITERS = 200000

statefile = graphmlfile.replace(".graphml", "") + "-%s.state" % NB_ITERS

#plus simple de charger le réseau en graphml apparemment
g=gt.load_graph(graphmlfile)

print("Graph loaded")


nL = 10
deg_corr = True
state = gt.minimize_nested_blockmodel_dl(g, deg_corr=deg_corr)     # Initialize the Markov
                                                                   # chain from the "ground
print("Markov chain bootstrapped")

bs = state.get_bs()                     # Get hierarchical partition.
bs += [np.zeros(1)] * (nL - len(bs))    # Augment it to L = 10 with
                                        # single-group levels.
print("Hierarchy inferred")

state = state.copy(bs=bs, sampling=True)

print("Model sampled")

# Recherche d'une meilleure solution avec sweeps (augmenter force_niter au besoin)
# Now we collect the marginal distributions for exactly NB_ITERS sweeps

def collect_marginals(s):
    global vm, em, count
    levels = s.get_levels()
    vm = [sl.collect_vertex_marginals(vm[l]) for l, sl in enumerate(levels)]
    em = levels[0].collect_edge_marginals(em)
    dls.append(s.entropy())
    count += 1
    if count % 2000 == 0:
        print("%s iterations done (%s)" % (count, str(100*count/NB_ITERS)+"%"))

dls = []                               # description length history
vm = [None] * len(state.get_levels())  # vertex marginals
em = None                              # edge marginals
count = 0

#gt.mcmc_equilibrate(state, force_niter=NB_ITERS, mcmc_args=dict(niter=10),
#                    callback=collect_marginals)
#print("Model equilibrated")

#S_mf = [gt.mf_entropy(sl.g, vm[l]) for l, sl in enumerate(state.get_levels())]
#print("MF Entropy computed")
#S_bethe = gt.bethe_entropy(g, em)[0]
#print("Bethe entropy computed")
#L = -np.mean(dls)

#print("Model evidence for deg_corr = %s:" % deg_corr,
#      L + sum(S_mf), "(mean field),", L + S_bethe + sum(S_mf[1:]), "(Bethe)")

# et très important pour retrouver la roue à l'avenir ou la sauvegarde
with open(statefile, "wb") as f:
    pickle.dump(state, f)

