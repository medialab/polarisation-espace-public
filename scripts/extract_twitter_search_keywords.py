#!/usr/bin/env python3
import csv
from ural import LRUTrie, normalize_url

CORPUS = './data/corpora/corpus_hyphe_curated.csv'
OUTPUT = './data/corpus_hyphe_curated_with_twitter_search.csv'
NORMALIZE_KWARGS = {
    'strip_trailing_slash': True,
    'strip_lang_subdomains': False
}

with open(CORPUS) as f, open(OUTPUT, 'w') as wf:
    reader = csv.DictReader(f)
    writer = csv.DictWriter(wf, fieldnames=reader.fieldnames + ['twitter_search'])
    writer.writeheader()

    for line in reader:
        prefixes = LRUTrie(**NORMALIZE_KWARGS)

        for prefix in line['PREFIXES AS URL'].split(' '):
            prefixes.set(prefix, prefix)

        matching_prefix = prefixes.match(line['HOME PAGE'])

        if matching_prefix is None:
            print()
            print('Alaaaarm!', line)
            print()

        search_keyword = normalize_url(matching_prefix, **NORMALIZE_KWARGS)

        print(line['NAME'], '=>', search_keyword)
