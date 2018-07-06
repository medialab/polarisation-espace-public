#!/usr/bin/env python3
# =============================================================================
# Script computing stats related to stories as found in article content
# =============================================================================
#
import csv
import os
import sys
import mediacloud
from datetime import date
from progressbar import ProgressBar

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie
from config import MEDIACLOUD_API_KEY

MEDIA_FILE = './data/sources.csv'
OUTPUT_FILE = './data/keyword-stories.csv'

FRANCE_LOCAL_COLLECTION = 38379799
FRANCE_NATIONAL_COLLECTION = 34412146

DEFAULT_DATE = [date(2018, 4, 1), date.today()]

STORIES = {
    'tolbiac_blesse': {
        'query': 'Tolbiac AND (mort OR bless* OR deced*)',
        'date': [date(2018, 4, 1), date(2018, 4, 30)]
    },
    'tolbiac_prostitution': {
        'query': 'Tolbiac AND (sexe OR prostitu* OR drogu*)',
        'date': [date(2018, 4, 15), date.today()]
    },
    'mamoudou_gassama': {
        'query': 'Mamoudou OR Gassama',
        'date': [date(2018, 5, 26), date.today()]
    },
    'pma_gpa': {
        'query': 'PMA OR GPA',
        'date': [date(2018, 4, 1), date.today()]
    },
    'aquarius': {
        'query': 'Aquarius',
        'date': [date(2018, 6, 8), date.today()]
    },
    'dimitri_payet': {
        'query': '"Dimitri Payet"',
        'date': [date(2018, 5, 11), date(2018, 5, 20)]
    },
    'meghan_markle': {
        'query': '"Meghan Markle"',
        'date': [date(2018, 5, 12), date(2018, 5, 21)]
    },
    'soros': {
        'query': 'Soros',
        'date': [date(2018, 4, 1), date.today()]
    },
    'beltrame': {
        'query': 'Beltrame',
        'date': [date(2018, 3, 24), date(2018, 5, 1)]
    },
    'macron_aides_sociales': {
        'query': 'Macron AND pognon AND dingue',
        'date': [date(2018, 6, 10), date.today()]
    },
    'virginie_calmels': {
        'query': '"Virginie Calmels"',
        'date': [date(2018, 6, 1), date.today()]
    },
    'anticor': {
        'query': 'Anticor',
        'date': [date(2018, 6, 1), date.today()]
    },
    'salvini': {
        'query': '"Mateo Salvini" AND aquarius',
        'date': [date(2018, 6, 8), date.today()]
    },
    'rabiot': {
        'query': '"Adrien Rabiot"',
        'date': [date(2018, 5, 11), date(2018, 5, 21)]
    },
    'parcoursup': {
        'query': 'parcoursup',
        'date': [date(2018, 4, 1), date.today()]
    },
    'blanquefort': {
        'query': 'Ford AND Blanquefort',
        'date': [date(2018, 4, 1), date.today()]
    },
    'whirlpool': {
        'query': 'Whirlpool AND Amiens',
        'date': [date(2018, 4, 1), date.today()]
    },
    'maduro': {
        'query': 'Maduro AND élection',
        'date': [date(2018, 4, 1), date.today()]
    },
    'attentat_opera': {
        'query': 'attentat AND opéra',
        'date': [date(2018, 5, 11), date(2018, 6, 7)]
    },
    'attentat_egyptien': {
        'query': 'Collomb AND égyptien',
        'date': [date(2018, 4, 1), date.today()]
    },
    'macron_vatican': {
        'query': 'Macron AND ("Saint Siège" OR Vatican)',
        'date': [date(2018, 6, 15), date(2018, 7, 5)]
    },
    'macron_migrants': {
        'query': 'Macron AND (centre OR centres) AND (migrant OR migrants OR migrations)',
        'date': [date(2018, 6, 9), date(2018, 7, 5)]
    }
}

client = mediacloud.api.AdminMediaCloud(MEDIACLOUD_API_KEY)
trie = LRUTrie.from_csv(MEDIA_FILE, detailed=True)


def count(story, media_id):
    solr_filter = client.publish_date_query(*(story['date'] if story else DEFAULT_DATE))

    if story:
        solr_query = 'media_id:%s AND (%s)' % (media_id, story['query'])
    else:
        solr_query = 'media_id:%s' % media_id

    result = client.storyCount(solr_query, solr_filter)

    return result['count']


with open(OUTPUT_FILE, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'name', 'story', 'count'])
    writer.writeheader()

    bar = ProgressBar()

    for media in bar(trie.values):

        if 'mediacloud_id' not in media or not media['mediacloud_id']:
            continue

        c = count(None, media['mediacloud_id'])

        writer.writerow({
            'id': media['id'],
            'name': media['name'],
            'story': 'all',
            'count': c
        })

        for story_name, story in STORIES.items():
            writer.writerow({
                'id': media['id'],
                'name': media['name'],
                'story': story_name,
                'count': 0 if c == 0 else count(story, media['mediacloud_id'])
            })
