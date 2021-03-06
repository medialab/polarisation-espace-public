#!/usr/bin/env python3
# =============================================================================
# Script computing stats concerning tweet urls
# =============================================================================
#
import os
import csv
import sys
from functools import lru_cache
from progressbar import ProgressBar
from ural import normalize_url
from collections import Counter, defaultdict

SHARES = './data/180918_polarisation_users_links_isrt.csv'
MEDIA_FILE = './data/sources.csv'
OUTPUT = './data/deduped_shared_urls.csv'
MEDIA_OUTPUT = './data/shared_medias.csv'

URL_BLACKLIST = set([
    'lemediatv.fr/devenez-socio'
])

TOKENS_BLACKLIST = [
    'mediaplayer',
    'plus.lequipe.fr/?v=',
]

FINAL_TOKENS_BLACKLIST = [
    '/player',
    '/en-direct',
    '/direct'
]

FAILED_TO_MATCH = set()
COUNTS_PER_UNIQUE_URL = Counter()
COUNTS_PER_MEDIA = Counter()
UNIQUE_URLS_PER_MEDIA = defaultdict(set)

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie

MEDIAS_TRIE = LRUTrie.from_csv(MEDIA_FILE)

# Memoization
normalize_url = lru_cache(maxsize=2048)(normalize_url)

# TODO: improve heuristics

with open(SHARES, 'r') as f:
    reader = csv.reader(f)
    next(reader)

    bar = ProgressBar()

    for line in bar(reader):

        urls = line[1].split('|')

        for url in urls:

            url = normalize_url(url)

            # Dropping homepages
            if '/' not in url:
                continue

            # Black lists
            if url in URL_BLACKLIST:
                continue

            if any(token in url for token in TOKENS_BLACKLIST):
                continue

            if any(url.endswith(token) for token in FINAL_TOKENS_BLACKLIST):
                continue

            media = MEDIAS_TRIE.longest(url)

            if not media:
                FAILED_TO_MATCH.add(url)
                continue

            COUNTS_PER_UNIQUE_URL[url] += 1
            COUNTS_PER_MEDIA[media] += 1
            UNIQUE_URLS_PER_MEDIA[media].add(url)

print('Deduped url count: %i' % len(COUNTS_PER_UNIQUE_URL))
print('Failed to match: %i' % len(FAILED_TO_MATCH))

print('Writing deduped urls output...')
with open(OUTPUT, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['url', 'shares'])

    for url, count in COUNTS_PER_UNIQUE_URL.most_common():
        writer.writerow([url, count])

print('Writing medias output...')
with open(MEDIA_OUTPUT, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['media', 'shares', 'urls'])

    for media, count in COUNTS_PER_MEDIA.most_common():
        writer.writerow([media, count, len(UNIQUE_URLS_PER_MEDIA[media])])
