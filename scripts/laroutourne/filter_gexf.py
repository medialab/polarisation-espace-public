#!/usr/bin/env python

import sys
import networkx as nx

filename = sys.argv[1]

G1 = nx.read_gexf(filename)
G2 = nx.read_gexf(filename)

for nid, data in G1.nodes(data=True):
    if data.get('batch', '') == "EU":
        G2.remove_node(nid)

#for nid, data in G.nodes(data="batch"):
#    if G.in_degree(nid) < 3:
#        G.remove_node(nid)
#        print(nid, data)

nx.write_gexf(G2, filename.replace(".gexf", "-onlymedias.gexf"))
