
import click
import csv
import networkx as nx

@click.command()
@click.argument('filename')
def export_csv(filename):
    G = nx.read_gexf(filename)

    fields = set()
    for nid, data in G.nodes(data=True):
        if "id" in data:
            sys.exit("ERROR, graph has a node with an attribute named 'id'")
        fields |= set(data.keys())
    if "label" in fields:
        fields.remove("label")
    fields = ["id", "label"] + list(fields)

    with open(filename.replace(".gexf", "-nodes.csv"), "w") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=fields)
        writer.writeheader()
        for nid, data in G.nodes(data=True):
            node = {"id": nid}
            node.update(data)
            writer.writerow(node)


if __name__ == '__main__':
    export_csv()
