#!/usr/bin/env python3
# =============================================================================
# Script computing stats related to stories as found in deduped urls
# =============================================================================
#
from collections import Counter
import csv
import os
import pandas as pd
from progressbar import ProgressBar
import seaborn as sns
import sys

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie

URLS = './data/deduped_shared_urls.csv'
MEDIA_FILE = './data/sources.csv'
OUTPUT = './data/url-stories.csv'
MEDIAS_TRIE = LRUTrie.from_csv(MEDIA_FILE, detailed=True)

STORIES = ['beltrame', 'mamoudou', 'soros', 'unef']

MEDIA_COUNTS = Counter()
STORIES_COUNTS = {k: Counter() for k in STORIES}
WEBENTITIES = {media['webentity']: media for media in MEDIAS_TRIE.values}

with open(URLS, 'r') as f:
    reader = csv.DictReader(f)
    bar = ProgressBar()

    for line in bar(reader):

        media = MEDIAS_TRIE.longest(line['url'])

        if media['batch'] != '1':
            continue

        webentity = media['webentity']

        MEDIA_COUNTS[webentity] += 1

        for story in STORIES:
            if story in line['url'].lower():
                STORIES_COUNTS[story][webentity] += 1

with open(OUTPUT, 'w') as f:
    # 1
    # writer = csv.writer(f)
    # writer.writerow(['media', 'count'] + ['level%i' % i for i in range(4)] + STORIES)

    # for media, count in MEDIA_COUNTS.items():
    #     line = [media, count]
    #     line += [WEBENTITIES[media]['level%i_title' % i] for i in range(4)]
    #     line += [STORIES_COUNTS[story][media] for story in STORIES]

    #     writer.writerow(line)

    # 2
    # writer = csv.writer(f)
    # writer.writerow(['media', 'count', 'story'] + ['level%i' % i for i in range(4)])

    # for media, count in MEDIA_COUNTS.items():
    #     writer.writerow([media, count, 'all'] + [WEBENTITIES[media]['level%i_title' % i] for i in range(4)])

    #     for story in STORIES:
    #         writer.writerow([media, STORIES_COUNTS[story][media], story] + [WEBENTITIES[media]['level%i_title' % i] for i in range(4)])

    DATA = []

    MEDIA_SUM = sum(MEDIA_COUNTS.values())
    STORIES_SUM = {story: sum(STORIES_COUNTS[story].values()) for story in STORIES}

    for media, count in MEDIA_COUNTS.items():
        for story in ['all'] + STORIES:
            item = {
                'media': media,
                'story': story
            }

            if story == 'all':
                item['count'] = count / MEDIA_SUM
            else:
                item['count'] = STORIES_COUNTS[story][media] / STORIES_SUM[story]

            for i in range(4):
                item['level%i' % i] = WEBENTITIES[media]['level%i_title' % i]

            DATA.append(item)

    frame = pd.DataFrame(DATA)
    frame.to_csv(OUTPUT)
    # frame.plot(kind='bar', x='level2', y='count')
    # plot = sns.factorplot(x='level2', y='count', hue='story', data=frame, kind='bar', ci=None)
    # plot.set_xticklabels(rotation=90)
    # plot.savefig('./data/url-stories.png')
