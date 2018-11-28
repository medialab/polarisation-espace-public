#!/usr/bin/env python3
# =============================================================================
# Script dumping ANSES data
# =============================================================================
#
# Script retrieving stories urls from mediacloud and associates them to
# Twitter shares and the relevant media.
#
import os
import csv
import sys
import mediacloud
from datetime import date
from progressbar import ProgressBar
from ural import normalize_url

sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie
from config import MEDIACLOUD_API_KEY

MEDIA_FILE = './data/sources.csv'
SHARED_URLS_FILE = './data/181128_polarisation_shared_urls.csv'
OUTPUT = './data/anses-output.csv'

TAGS_ID_MEDIA = (38379799, 34412146)
ROWS = 20

QUERIES = [
    'glyphosate',
    'slime',
    '(chlordécone OR chlordecone)'
]

client = mediacloud.api.MediaCloud(MEDIACLOUD_API_KEY)
trie = LRUTrie.from_csv(MEDIA_FILE, detailed=True)

DEDUPED_URLS = {}

# Indexing urls
with open(SHARED_URLS_FILE, 'r') as f:
    reader = csv.reader(f)
    next(reader)

    bar = ProgressBar()

    for line in bar(reader):
        DEDUPED_URLS[normalize_url(line[0])] = int(line[1])

bar.finish()

# Retrieving mediacloud urls
with open(OUTPUT, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['query', 'id', 'date', 'url', 'normalized', 'title', 'media', 'shares'])
    writer.writeheader()

    for query in QUERIES:
        print('Query "%s"' % query)

        nb_batches = 0
        last = 0

        # TODO: add mediacloud_id + match by id rather
        while True:
            result = client.storyList('%s AND (tags_id_media:%i OR tags_id_media:%i)' % (query, *TAGS_ID_MEDIA),
                                      client.publish_date_query(*[date(2018, 4, 1), date.today()]), rows=ROWS,
                                      last_processed_stories_id=last)

            nb_batches += 1

            if len(result) == 0:
                break

            for story in result:
                media = trie.longest(story['url'])
                normalized_url = normalize_url(story['url'])

                writer.writerow({
                    'query': query,
                    'id': story['stories_id'],
                    'url': story['url'],
                    'normalized': normalized_url,
                    'title': story['title'],
                    'date': story['publish_date'],
                    'media': media['name'] if media else '',
                    'shares': DEDUPED_URLS[normalized_url] if normalized_url in DEDUPED_URLS else ''
                })

            print('  • Processed %i stories.' % (ROWS * nb_batches))
            last = result[-1]['processed_stories_id']
