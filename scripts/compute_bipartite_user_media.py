#!/usr/bin/env python3
# =============================================================================
# Script to compute the bipartite graph user<->media
# =============================================================================
#
# This script streams CSV lines from a Gazouilloire export and outputs the
# CSV representation of a bipartite graph linking users to the media they
# share in their tweets.
#
import os
import sys
import csv
from progressbar import ProgressBar

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie

# TODO: histogram for distinct urls

# Parameters
MEDIA_FILE = './data/sources_mediacloud.csv'
TWEETS_FILE = './data/180413_polarisation_users_links.csv'
OUTPUT_FILE = './bipartite-user-media.csv'

print('Indexing medias...')

MEDIAS_TRIE = LRUTrie()

with open(MEDIA_FILE, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:

        # NOTE: currently, media names are unique
        MEDIAS_TRIE.set(line['url'], line['name'])

print('Streaming tweets...')

with open(TWEETS_FILE, 'r') as tf, open(OUTPUT_FILE, 'w') as of:
    reader = csv.DictReader(tf)
    writer = csv.DictWriter(of, fieldnames=['user', 'media'])
    writer.writeheader()

    bar = ProgressBar()

    for line in bar(reader):
        user = line['user_screenname']
        links = line['links'].split('|')

        for link in links:
            media = MEDIAS_TRIE.longest(link)

            if media:
                writer.writerow({
                    'user': user,
                    'media': media
                })
