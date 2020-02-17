#!/usr/bin/env python

import click
import networkx as nx


@click.command()
@click.argument('filename')
@click.option('--min-degree', default=1, type=int, show_default=True)
@click.option('--min-indegree', default=0, type=int, show_default=True)
@click.option('--min-outdegree', default=0, type=int, show_default=True)
@click.option('--filter-field', type=str, help="filter out nodes with attribute KEY=VAL")
@click.option('--weight/--no-weight', default=False, show_default=True)
def compute(filename, min_degree, min_indegree, min_outdegree, filter_field, weight):
    """Prepare a GEXF network to be used with laroutourne"""

    gexf_text = ""
    with open(filename) as f:
        for line in f.readlines():
            if 'version="1.3"' in line:
                line = '<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/XMLSchema-instance">'
            elif '<viz:' in line:
                continue
            gexf_text += line
    cleangexf = filename.replace(".gexf", "-clean.gexf")
    with open(cleangexf, "w") as f:
        print(gexf_text, file=f)

    G_in = nx.read_gexf(cleangexf)
    G_out = nx.read_gexf(cleangexf)

    filter_key = None
    filter_val = None
    if filter_field and "=" in filter_field:
        filter_key, filter_val = filter_field.split("=")

    if not weight:
        for src, tgt, dat in G_in.edges(data=True):
            for key in ["weight", "count"]:
                if key in dat:
                    del G_out[src][tgt][key]

    for nid, data in G_in.nodes(data=True):
        if ((filter_key and data.get(filter_key, '') == filter_val)
         or (min_degree and G_in.degree(nid) < min_degree)
         or (min_indegree and G_in.in_degree(nid) < min_indegree)
         or (min_outdegree and G_in.out_degree(nid) < min_outdegree)):
            G_out.remove_node(nid)

    nx.write_gexf(G_out, filename.replace(".gexf", "-prepared.gexf"))
    nx.write_graphml(G_out, filename.replace(".gexf", "-prepared.graphml"))


if __name__ == '__main__':
    compute()
