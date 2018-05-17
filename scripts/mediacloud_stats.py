#!/usr/bin/env python3
# =============================================================================
# Script collecting various statistics about our mediacloud collections
# =============================================================================
#
import os
import csv
import sys
import mediacloud
from collections import Counter
from progressbar import ProgressBar
from pprint import pprint

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

SOURCES = './data/sources.csv'
COUNTER = Counter()

client = mediacloud.api.MediaCloud(MEDIACLOUD_API_KEY)

with open(SOURCES, 'r') as f:
    reader = csv.DictReader(f)
    bar = ProgressBar()

    for line in bar(reader):

        if 'mediacloud_id' not in line or not line['mediacloud_id']:
            continue

        result = client.storyCount(solr_filter='media_id:' + line['mediacloud_id'])
        COUNTER[line['name']] = result['count']

for name, count in COUNTER.most_common():
    print(name, count)
