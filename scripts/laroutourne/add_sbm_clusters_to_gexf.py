import click
import csv
import networkx as nx
from os import listdir
from os.path import isfile, join

@click.command()
@click.argument('gexf')
@click.argument('directory')
def add_sbm_clusters(gexf, directory):
    G = nx.read_gexf(gexf)

    label_keys = {}
    rows = {}
    for nid, data in G.nodes(data=True):
        label_keys[data["label"]] = nid
        rows[data["label"]] = {
            "id": nid,
            "label": data["label"]
        }


    for f in listdir(directory):
        fpath = join(directory, f)
        if not isfile(fpath) or not f.endswith(".csv") or not "entropy" in f:
            continue
        with open(fpath) as csvf:
            clustering = "SBM entropy " + f.split("-entropy_")[1].split("-")[0]
            print(clustering)
            for row in csv.DictReader(csvf):
                G.nodes[label_keys[row["label"]]][clustering] = "%s.%s.%s" % (row["level_2"], row["level_1"], row["level_0"])
                rows[row["label"]][clustering] = "%s.%s.%s" % (row["level_2"], row["level_1"], row["level_0"])

    nx.write_gexf(G, gexf.replace(".gexf", "-with-SBM-clusters.gexf"))
    with open(gexf.replace(".gexf", "-with-SBM-clusters.csv"), "w") as csvf:
        writer = csv.writer(csvf)
        headers = rows["Lemonde.fr"].keys()
        writer.writerow(headers)
        for row in rows.values():
            writer.writerow([row[k] for k in headers])


if __name__ == '__main__':
    add_sbm_clusters()

