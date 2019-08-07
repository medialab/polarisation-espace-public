#!/usr/bin/env python

import sys
import networkx as nx

filename = sys.argv[1]

G = nx.read_gexf(filename)

for nid, data in G.nodes(data="batch"):
    if data['batch'] == "EU":
        G.remove_node(nid)

for nid, data in G.nodes(data="batch"):
    if G.in_degree(nid) < 3:
        G.remove_node(nid)

nx.write_gexf(G, filename.replace(".gexf", "-filtered.gexf"))
