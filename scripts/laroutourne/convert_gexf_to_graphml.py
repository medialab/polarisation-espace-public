#!/usr/bin/env python

import sys
import networkx as nx

filename = sys.argv[1]

nx.write_graphml(nx.read_gexf(filename), filename.replace(".gexf", ".graphml"))
