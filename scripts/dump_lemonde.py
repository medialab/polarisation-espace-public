#!/usr/bin/env python3
# =============================================================================
# Script dumping Le Monde's stories
# =============================================================================
#
# We need to retrieve all of Le Monde's stories on mediacloud so we can train
# our thematic classifier afterwards.
#
import os
import csv
import sys
import mediacloud
from datetime import date
from pprint import pprint

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

client = mediacloud.api.AdminMediaCloud(MEDIACLOUD_API_KEY)

LEMONDE_ID = 39072
ROWS = 20
OUTPUT = './data/lemonde.csv'
FILTER = 'media_id:%i' % LEMONDE_ID
DATE = client.publish_date_query(date(2018, 5, 1), date.today())

estimation_result = client.storyCount(FILTER, solr_filter=DATE)

print('Estimating %i stories to fetch.' % estimation_result['count'])

# TODO: need to filter videos -> no text

nb_batches = 0
last = 0
with open(OUTPUT, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'url', 'title', 'text', 'date', 'rss'])
    writer.writeheader()

    while True:
        result = client.storyList(FILTER, solr_filter=DATE, rows=ROWS,
                                  text=1, last_processed_stories_id=last)

        nb_batches += 1

        if len(result) == 0:
            break

        for story in result:
            writer.writerow({
                'id': story['stories_id'],
                'url': story['url'],
                'title': story['title'],
                'text': story['story_text'],
                'date': story['publish_date'],
                'rss': '1' if story['full_text_rss'] else '0'
            })

        print('Processed %i stories.' % (ROWS * nb_batches))
        last = result[-1]['processed_stories_id']

print('Done!')
