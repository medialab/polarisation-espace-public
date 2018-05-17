#!/usr/bin/env python3
# =============================================================================
# Script to retrieve Mediacloud ids
# =============================================================================
#
# Using the Mediacloud API to retrieve our medias' ids.
#
import os
import sys
import mediacloud

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

# INDEX = {}
# FRANCE_LOCAL_COLLECTION = 38379799
# FRANCE_NATIONAL_COLLECTION = 34412146

# client = mediacloud.api.MediaCloud(MEDIACLOUD_API_KEY)
# medias = []

# def fetch(tag, last=0):
#     result = client.mediaList(tags_id=[tag],
#                               rows=100, last_media_id=last)

#     if len(result) == 0:
#         return None, None

#     last_media = max(result, key=lambda m: m['media_id'])

#     return last_media['media_id'], result

# last_media_id = 0
# while True:
#     print('Fetching %i' % last_media_id)
#     last_media_id, result = fetch(FRANCE_NATIONAL_COLLECTION, last_media_id)

#     if result is None:
#         break

#     medias.extend(result)

# medias.extend(fetch(FRANCE_LOCAL_COLLECTION)[1])

# for media in medias:
#     INDEX[media['url']] = media['media_id']

import csv
import json
from collections import Counter
from urllib.parse import urlparse

with open('./data/mediacloud.json', 'r') as f:
    INDEX = json.load(f)

def get_host(url):
    parsed = urlparse(url)
    loc = parsed.netloc.split('.')
    return '.'.join([i for i in reversed(loc[:-1]) if i != 'www']) + '.' + loc[-1]

URL_INDEX = {}
MATCHED = Counter()
NOT_FOUND_IN_MEDIACLOUD = []
NOT_FOUND_IN_POLARISATION = []
for url, mediacloud_id in INDEX.items():
    URL_INDEX[get_host(url)] = mediacloud_id

with open('./data/sources.csv', 'r') as rf, open('./data/sources-with-mediacloud-data.csv', 'w') as wf:
    reader = csv.DictReader(rf)
    writer = csv.DictWriter(wf, fieldnames=reader.fieldnames + ['mediacloud_id'])
    writer.writeheader()

    for line in reader:

        if line['batch'] != '1':
            continue

        url = line['url']
        mediacloud_id = URL_INDEX.get(get_host('http://' + url))
        MATCHED[get_host('http://' + url)] += 1

        if mediacloud_id is None:
            NOT_FOUND_IN_MEDIACLOUD.append(url)

        line['mediacloud_id'] = mediacloud_id if mediacloud_id is not None else ''
        writer.writerow(line)

for url, count in MATCHED.items():

    if count > 1:
        print('%s found %i times' % (url, count))

for url in URL_INDEX.keys():
    if not url in MATCHED:
        NOT_FOUND_IN_POLARISATION.append(url)

print()
print('%i not found in mediacloud' % len(NOT_FOUND_IN_MEDIACLOUD))
for url in NOT_FOUND_IN_MEDIACLOUD:
    print('  ' + url)

print()
print('%i not found in polarisation' % len(NOT_FOUND_IN_POLARISATION))
for url in NOT_FOUND_IN_POLARISATION:
    print('  ' + url)
