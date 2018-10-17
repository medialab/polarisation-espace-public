#!/usr/bin/env python3
# =============================================================================
# Script collecting various statistics about our mediacloud collections
# =============================================================================
#
import os
import csv
import sys
import mediacloud
from datetime import date
from collections import Counter
from progressbar import ProgressBar
from pprint import pprint

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

SOURCES = './data/sources.csv'
COUNTER = Counter()

client = mediacloud.api.AdminMediaCloud(MEDIACLOUD_API_KEY)

with open(SOURCES, 'r') as f:
    reader = csv.DictReader(f)
    bar = ProgressBar()

    for line in bar(reader):

        if 'mediacloud_id' not in line or not line['mediacloud_id']:
            continue

        result = client.storyCount(
            'media_id:%s' % line['mediacloud_id'],
            client.publish_date_query(*[date(2018, 4, 1), date.today()])
        )
        COUNTER[line['name']] = result['count']

for name, count in COUNTER.most_common():
    print('%s,%s' % (name, count))
