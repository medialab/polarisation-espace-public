import click
import csv
from os import listdir
from os.path import isfile, join


def footprint_clustering(hierarchy):
    footprint = []
    for l0, l1s in sorted(hierarchy.items(), key=lambda x: len(x[1].keys())):
        footprint.append(",".join([str(len(l2s)) for l1, l2s in sorted(l1s.items(), key=lambda x: len(x[1]))]))
    return "|".join(footprint)

@click.command()
@click.argument('directory')
def meta_cluster(directory):
    for fname in listdir(directory):
        fpath = join(directory, fname)
        if not isfile(fpath) or not fname.endswith(".csv") or not "entropy" in fname:
            continue
        with open(fpath) as csvf:
            clustering = "SBM entropy " + fname.split("-entropy_")[1].split("-")[0]
            hierarchy = {}
            clusters = 0
            for row in csv.DictReader(csvf):
                if row["level_2"] not in hierarchy:
                    hierarchy[row["level_2"]] = {}
                if row["level_1"] not in hierarchy[row["level_2"]]:
                    hierarchy[row["level_2"]][row["level_1"]] = []
                if row["level_0"] not in hierarchy[row["level_2"]][row["level_1"]]:
                    hierarchy[row["level_2"]][row["level_1"]].append(row["level_0"])
                    clusters += 1

            print(footprint_clustering(hierarchy))


if __name__ == '__main__':
    meta_cluster()

