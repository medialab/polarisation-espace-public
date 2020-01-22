#!/usr/bin/env python

import sys
import networkx as nx

filename = sys.argv[1]

G_in = nx.read_gexf(filename)
G_out = nx.read_gexf(filename)

# TODO add CLI option to filter nodes with cat=val attributes
#for nid, data in G.nodes(data="batch"):
#    if data['batch'] == "EU":
#        G.remove_node(nid)

# TODO add CLI option to filter nodes with indegree lower than threshold
#for nid, data in G.nodes(data="batch"):
#    if G.in_degree(nid) < 3:
#        G.remove_node(nid)
#        print(nid, data)

for e in G_in.edges(data=True):
    for key in ["weight", "count"]:
        if key in e[2]:
            del(G_out[e[0]][e[1]][key])

nx.write_graphml(G_out, filename.replace(".gexf", ".graphml"))
