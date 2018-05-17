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
from progressbar import ProgressBar

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

LEMONDE_ID = 39072
OUTPUT = './data/lemonde.csv'

client = mediacloud.api.AdminMediaCloud(MEDIACLOUD_API_KEY)

nb_batches = 0
last = 0
with open(OUTPUT, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'url', 'title', 'text', 'date', 'rss'])
    writer.writeheader()

    bar = ProgressBar()

    while True:
        result = client.storyList(solr_filter='media_id:%i' % LEMONDE_ID, text=1, last_processed_stories_id=last)

        bar.update(nb_batches)
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

        last = result[-1]['stories_id']

bar.finalize()
