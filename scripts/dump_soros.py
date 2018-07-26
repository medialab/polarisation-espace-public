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

ROWS = 20
OUTPUT = './data/soros-urls.csv'

nb_batches = 0
last = 0
with open(OUTPUT, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'url', 'title', 'date', 'rss'])
    writer.writeheader()

    while True:
        result = client.storyList('Soros AND (tags_id_media:%i OR tags_id_media:%i)' % (38379799, 34412146),
                                  client.publish_date_query(*[date(2018, 4, 1), date.today()]), rows=ROWS,
                                  last_processed_stories_id=last)

        nb_batches += 1

        if len(result) == 0:
            break

        for story in result:
            writer.writerow({
                'id': story['stories_id'],
                'url': story['url'],
                'title': story['title'],
                'date': story['publish_date'],
                'rss': '1' if story['full_text_rss'] else '0'
            })

        print('Processed %i stories.' % (ROWS * nb_batches))
        last = result[-1]['processed_stories_id']

print('Done!')
