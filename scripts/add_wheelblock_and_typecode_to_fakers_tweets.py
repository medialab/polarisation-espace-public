import csv
import gzip
import sys
from collections import defaultdict
from tqdm import tqdm
from ural import normalize_url
import casanova

def read_urls_types(list_urls_file):
    urls_types = {}
    codes = set()
    categories = set()
    with open(list_urls_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes.add(row["code"])
            categories.add(row["block"])
            url = normalize_url(row["clean_url"].strip(), strip_trailing_slash=True)
            urls_types[url] = [row["code"], row["block"], row["webentity"]]
    return urls_types, list(codes), list(categories)


def filter_and_enrich_tweets_from_csv(f, cat_urls, codes, categories, of=sys.stdout, total=None):
    add_fields = ["matched_urls", "webentities"] + categories + codes
    casa = casanova.enricher(f, of, add=add_fields)
    links_pos = casa.pos.links
    len_row = len(casa.fieldnames) - casa.added_count
    add_pos = {field: i for i, field in enumerate(add_fields)}
    try:
        for row in tqdm(casa, total=total):
            links = [normalize_url(u.strip(), strip_trailing_slash=True) for u in row[links_pos].split('|')]
            if not links:
                continue
            webentities = set()
            matched_urls = set()
            add_row = ['', ''] + [False for i in categories] + [False for j in codes]
            for u in links:
                infos = cat_urls.get(u, None)
                if infos:
                    matched_urls.add(u)
                    add_row[add_pos[infos[0]]] = True
                    add_row[add_pos[infos[1]]] = True
                    webentities.add(infos[2])
            add_row[add_pos["webentities"]] = "|".join(webentities)
            add_row[add_pos["matched_urls"]] = "|".join(matched_urls)

            if matched_urls:
                casa.writerow(row, add_row)

    except Exception as e:
        print("ERROR while processing", row, file=sys.stderr)
        raise(e)


def gzip_open(filename):
    return gzip.open(filename, mode="rt")

if __name__ == "__main__":
    urls_types_file = sys.argv[1]
    source = sys.argv[2]
    csv_lines = int(sys.argv[3]) if len(sys.argv) > 3 else None

    cat_urls, codes, categories = read_urls_types(urls_types_file)

    if source.endswith(".csv") or source.endswith(".gz"):
        # read tweets from tweets archive (csv possibly gzipped)
        open_wrapper = gzip_open if source.endswith(".gz") else open
        with open_wrapper(source) as f:
            # setattr(sys.stdout, 'tell', lambda: 0)
            filter_and_enrich_tweets_from_csv(f, cat_urls, codes, categories, total=csv_lines)



