import sys
import csv
import gzip
from collections import defaultdict

import casanova
from tqdm import tqdm
from ural import normalize_url


# Read list urls to filter
def read_list_urls(list_urls_file):
    categories_medias_urls = defaultdict(lambda: defaultdict(list))
    with open(list_urls_file, "r") as f:
        for row in csv.DictReader(f):
            url = normalize_url(row["clean_url"].strip())
            categories_medias_urls[row["niv0"]][row["webentity"]].append(url)
    return categories_medias_urls


def filter_and_enrich_tweets(f, cat_urls, of=sys.stdout, total=None):
    categories = list(cat_urls.keys())
    casa = casanova.enricher(f, of, add=["webentities"] + categories)
    links_pos = casa.pos.links

    for row in tqdm(casa, total=total):
        try:
            links = [normalize_url(u) for u in row[links_pos]]
            if not links:
                continue

            webentities = []
            cat_belongings = []
            for cat in categories:
                cat_match = False
                for we, urls in cat_urls[cat].items():
                    for u in links:
                        if u in urls:
                            cat_match = True
                            webentities.append(we)
                            links.remove(u)
                            break
                cat_belongings.append(cat_match)

            if webentities:
                casa.writerow(row, ["|".join(webentities)] + cat_belongings)

        except Exception as e:
            print("ERROR while processing", row, file=sys.stderr)
            raise(e)


def gzip_open(filename):
    return gzip.open(filename, mode="rt")


if __name__ == "__main__":
    list_urls_file = sys.argv[1]
    csv_archive = sys.argv[2]
    csv_lines = sys.argv[3] if len(sys.argv) > 3 else None

    cat_urls = read_list_urls(list_urls_file)

    # read tweets from tweets archive (csv possibly gzipped)
    open_wrapper = gzip_open if csv_archive.endswith(".gz") else open
    with open_wrapper(csv_archive) as f:
        setattr(sys.stdout, 'tell', lambda: 0)
        filter_and_enrich_tweets(f, cat_urls, total=csv_lines)
