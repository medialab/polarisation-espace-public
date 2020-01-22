#!/usr/bin/env python

import click
import networkx as nx


@click.command()
@click.argument('filename')
@click.option('--mindegree', default=1, type=int, show_default=True)
@click.option('--filterfield', type=str, help="filter out nodes with attribute KEY=VAL")
@click.option('--weight/--no-weight', default=False, show_default=True)
def compute(filename, mindegree, filterfield, weight):
    """Prepare a GEXF network to be used with laroutourne"""
    G_in = nx.read_gexf(filename)
    G_out = nx.read_gexf(filename)

    filter_key = None
    filter_val = None
    if filterfield and "=" in filterfield:
        filter_key, filter_val = filterfield.split("=")

    for nid, data in G_in.nodes(data=True):
        if ((filter_key and data.get(filter_key, '') == filter_val)
         or (mindegree and G_in.degree(nid) < mindegree)):
            G_out.remove_node(nid)

    if not weight:
        for e in G_in.edges(data=True):
            for key in ["weight", "count"]:
                if key in e[2]:
                    del(G_out[e[0]][e[1]][key])

    nx.write_gexf(G_out, filename.replace(".gexf", "-prepared.gexf"))
    nx.write_graphml(G_out, filename.replace(".gexf", "-prepared.graphml"))


if __name__ == '__main__':
    compute()
