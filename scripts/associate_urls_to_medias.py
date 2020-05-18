import os, csv
import sys
from ural import normalize_url

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie

def associate_urls_medias(csviterator, csv_field, trie):
    print("url,media")
    for row in csviterator:
        link = row.get(csv_field, None)
        if not link: continue
        url = normalize_url(link, strip_irrelevant_subdomain=False, strip_protocol=False)
        media = trie.longest(link) or ""
        print('"%s","%s"' % (link.replace('"', '""'), media.replace('"', '""')))

if __name__ == "__main__":
    medias_file = sys.argv[1]
    medias_trie = LRUTrie.from_csv(medias_file, detailed=False, urlfield='PREFIXES AS URL', urlseparator=' ', namefield="NAME", filterrows={"type (TAGS)": "media"})

    csv_input = sys.argv[2]
    csv_field = sys.argv[3]
    with open(csv_input) as f:
        associate_urls_medias(csv.DictReader(f), csv_field, medias_trie)
