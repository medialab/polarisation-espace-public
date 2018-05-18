#!/usr/bin/env python3
# =============================================================================
# Script computing stats concerning tweet urls
# =============================================================================
#
import csv
from progressbar import ProgressBar
from ural import normalize_url
from collections import Counter

URLS = './data/shared_urls.csv'
OUTPUT = './data/deduped_shared_urls.csv'
COUNTS = Counter()

# TODO: use LRUTrie
# TODO: improve heuristics

with open(URLS, 'r') as f:
    reader = csv.reader(f)
    next(reader)

    bar = ProgressBar()

    for line in bar(reader):
        url = normalize_url(line[0])
        count = line[1]

        # Dropping homepages
        if '/' not in url:
            continue

        COUNTS[url] += int(count)

print('Deduped url count: %i' % len(COUNTS))

print('Writing output...')
with open(OUTPUT, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['url', 'shares'])

    for url, count in COUNTS.most_common():
        writer.writerow([url, count])
