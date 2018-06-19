#!/usr/bin/env python3
# =============================================================================
# Script Filtering The Hyperlinks
# =============================================================================
#
# Filtering the GEXF network file to remove uncrawled entities.
#
import csv
import networkx as nx

MEDIA_FILE = './data/sources.csv'
NETWORK_FILE = './data/hyperlinks.gexf'
OUTPUT_FILE = './data/hyperlinks-filtered.gexf'

f = open(MEDIA_FILE, 'r')
reader = csv.DictReader(f)
FAILED = set(line['id'] for line in reader if line['crawled'] == '0')

f.close()

g = nx.read_gexf(NETWORK_FILE)
print(len(g))

for failed in FAILED:
    g.remove_node(failed)

print(len(g))

for node, attrs in g.nodes(data=True):
    attrs['indegree'] = g.in_degree(node)

nx.write_gexf(g, OUTPUT_FILE)
