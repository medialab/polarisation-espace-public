#!/usr/bin/env python

import sys
import networkx as nx

filename = sys.argv[1]

G = nx.read_gexf(filename)

for nid, batch in G.nodes(data="batch"):
    if batch == "EU":
        del G.node[nid]

nx.write_gexf(G, filename.replace(".gexf", "-filtered.gexf"))
