import sys
import pickle

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import graph_tool.all as gt
# GraphTool doc https://graph-tool.skewed.de/static/doc/index.html

graphmlfile = sys.argv[1]

#plus simple de charger le réseau en graphml apparemment
g=gt.load_graph(graphmlfile)

print("Graph loaded")

def collect_marginals(s):
        global vm, em, count
        levels = s.get_levels()
        vm = [sl.collect_vertex_marginals(vm[l]) for l, sl in enumerate(levels)]
        em = levels[0].collect_edge_marginals(em)
        dls.append(s.entropy())
        count +=1
        if count % 2000 == 0:
            print("%s iterations done (%s)" % (count, str(count/2000)+"%"))


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

dls = []                               # description length history
vm = [None] * len(state.get_levels())  # vertex marginals
em = None                              # edge marginals
count = 0

print("Levels extracted")

# Recherche d'une meilleure solution avec sweeps (augmenter force_niter au besoin)
# Now we collect the marginal distributions for exactly 200,000 sweeps
gt.mcmc_equilibrate(state, force_niter=200000, mcmc_args=dict(niter=10),
                    callback=collect_marginals)
print("Model equilibrated")
S_mf = [gt.mf_entropy(sl.g, vm[l]) for l, sl in enumerate(state.get_levels())]
print("MF Entropy computed")
S_bethe = gt.bethe_entropy(g, em)[0]
print("Bethe entropy computed")
L = -np.mean(dls)

print("Model evidence for deg_corr = %s:" % deg_corr,
      L + sum(S_mf), "(mean field),", L + S_bethe + sum(S_mf[1:]), "(Bethe)")



# et puis on trace la roue:

pos=state.draw(output="blockmodel_simple_filtered.png",vertex_text=state.g.vertex_properties['label'],vertex_text_position=1,output_size=(60, 60),vertex_size=1)
position=pos[2]
import math
text_rot = state.g.new_vertex_property('double')
state.g.vertex_properties['text_rot'] = text_rot
for v in state.g.vertices():
    if position[v][0] >0:
        text_rot[v] = math.atan(position[v][1]/position[v][0])
    else:
        text_rot[v] = math.pi + math.atan(position[v][1]/position[v][0])

state.draw(output="hyphe_nested_bm_noncorr3_filteredcorr.png",vertex_text=state.g.vertex_properties['label'],vertex_text_rotation=state.g.vertex_properties['text_rot'],vertex_size=1,vertex_text_position=1,output_size=(2000, 2000))

print("Wheel drawn")

# et très important pour retrouver la roue à l'avenir ou la sauvegarde

pickle.dump(state, open( "state_filteredv5.pkl", "wb" ))

