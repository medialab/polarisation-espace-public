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
import itertools
import networkx as nx
from collections import Counter
from fog.metrics import sparse_cosine_similarity
from progressbar import ProgressBar

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie

# Parameters
MEDIA_FILE = './data/sources.csv'
TWEETS_FILE = './data/180426_polarisation_users_links.csv'
OUTPUT_FILE = './bipartite-user-media.csv'
SIMILARITY_THRESHOLD = 0.05
MAX_USERS = 100_000
LIMIT = None

print('Indexing medias...')

MEDIAS_TRIE = LRUTrie()

with open(MEDIA_FILE, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:

        # NOTE: currently, media names are unique
        MEDIAS_TRIE.set(line['url'], line['name'])

print('Streaming tweets...')

NB_USERS = 0
TWEETS_COUNTER = Counter()
MEDIAS = list()
with open(TWEETS_FILE, 'r') as tf, open(OUTPUT_FILE, 'w') as of:
    reader = csv.DictReader(tf)
    # writer = csv.DictWriter(of, fieldnames=['user', 'media'])
    # writer.writeheader()

    bar = ProgressBar()
    count = itertools.count()
    bipartite = nx.Graph()

    for line in bar(reader):

        if LIMIT is not None and next(count) > LIMIT:
            bar.finish()
            break

        user = line['user_screenname']
        links = line['links'].split('|')

        for link in links:
            media = MEDIAS_TRIE.longest(link)

            if media:
                user_key = '$&@%s@&$' % user

                if user_key not in bipartite:
                    NB_USERS += 1
                    bipartite.add_node(user_key, type='user')

                if MAX_USERS is not None:
                    TWEETS_COUNTER[user_key] += 1

                if media not in bipartite:
                    MEDIAS.append(media)
                    bipartite.add_node(media, type='media')

                bipartite.add_edge(user_key, media, weight=0)
                bipartite[user_key][media]['weight'] += 1

            # if media:
            #     writer.writerow({
            #         'user': user,
            #         'media': media
            #     })

print('Found %i unique users.' % NB_USERS)
print('Found %i unique medias.' % len(MEDIAS))

if MAX_USERS is not None:
    print('Trimming users to keep only top %i...' % MAX_USERS)

    top_users = set(t[0] for t in TWEETS_COUNTER.most_common(MAX_USERS))
    # TODO: print top 10
    for node, t in list(bipartite.nodes(data='type')):
        if t != 'user':
            continue

        if node not in top_users:
            bipartite.remove_node(node)

monopartite = nx.Graph()
monopartite.add_nodes_from(MEDIAS)

USER_VECTORS = {}

print('Pre-computing sparse user vectors...')
bar = ProgressBar(max_value=len(MEDIAS))
for media in bar(iter(MEDIAS)):
    user_vector = {}

    for user in bipartite.neighbors(media):
        weight = bipartite[media][user]['weight']
        user_vector[user] = weight

    USER_VECTORS[media] = user_vector

print('Computing monopartite graph...')
bar = ProgressBar(max_value=len(MEDIAS))
for media in bar(iter(MEDIAS)):
    user_vector = USER_VECTORS[media]

    other_medias = set()

    for user in bipartite.neighbors(media):
        for other_media in bipartite.neighbors(user):

            # We can skip computation half of the time
            if other_media >= media:
                continue

            other_medias.add(other_media)

    for other_media in other_medias:
        other_user_vector = USER_VECTORS[other_media]

        if len(user_vector) == 0 or len(other_user_vector) == 0:
            similarity = 0.0
        else:
            similarity = sparse_cosine_similarity(user_vector, other_user_vector)

        if similarity >= SIMILARITY_THRESHOLD:
            monopartite.add_edge(media, other_media, weight=similarity)

print('Resulting monopartite graph has %i nodes and %i edges.' % (monopartite.order(), monopartite.size()))
nx.write_gexf(monopartite, 'bipartite-user-media.gexf')
