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
import math
import itertools
import networkx as nx
from collections import Counter, defaultdict
from fog.metrics import sparse_dot_product, weighted_jaccard_similarity
from progressbar import ProgressBar
from ural import normalize_url

# NOTE: possible to speed up through scipy

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie

# Parameters
MEDIA_FILE = '/store/gazouilloire/public/polarisation/190913-polarisation2-hyphe-corpus.csv'
TWEETS_FILE = '/store/gazouilloire/public/polarisation/190913-polarisation2-FR-users-urls.csv'
OUTPUT_FILE = '/store/gazouilloire/public/polarisation/190913-polarisation2-FR-%spartite-user-media'
OUTPUT_FILE2 = '/store/gazouilloire/public/polarisation/190913-polarisation2-FR-media-counts.csv'
SIMILARITY_THRESHOLD = 0.03
LIMIT = None
NAME_FIELD = 'NAME'

print('Indexing medias...')
MEDIAS_TRIE = LRUTrie.from_csv(MEDIA_FILE, detailed=True, urlfield='PREFIXES AS URL', urlseparator=' ', namefield=NAME_FIELD, filterrows={"type (TAGS)": "media"})

print('Streaming tweets...')

user_id_count = itertools.count()
USER_IDS = defaultdict(lambda: next(user_id_count))
USER_VECTORS = defaultdict(Counter)
MEDIAS_URLS = defaultdict(set)

# def pandas_reader(f):
#     for chunk in pd.read_csv(f, chunksize=5000, engine='c', dtype=str):
#         for row in chunk.itertuples():
#             yield row

with open(TWEETS_FILE, 'r') as tf, open((OUTPUT_FILE % "bi") + ".csv", 'w') as of:
    reader = csv.DictReader(tf)
    writer = csv.DictWriter(of, fieldnames=['user', 'media', 'normalized_url'])
    writer.writeheader()

    bar = ProgressBar()
    count = itertools.count()

    for line in bar(reader):

        if LIMIT is not None and next(count) > LIMIT:
            bar.finish()
            break

        user = line['user_screenname']
        user_id = USER_IDS[user]
        links = line['links'].split('|')

        for link in links:
            media = MEDIAS_TRIE.longest(link)

            if media:

                USER_VECTORS[media[NAME_FIELD]][user_id] += 1

                norm_link = normalize_url(link)
                MEDIAS_URLS[media[NAME_FIELD]].add(norm_link)

                writer.writerow({
                    'user': user,
                    'media': media[NAME_FIELD],
                    'normalized_url': norm_link
                })

MEDIAS = list(set([media[NAME_FIELD] for media in MEDIAS_TRIE.values]))

print('Found %i unique users.' % len(USER_IDS))
print('Found %i unique medias.' % len(MEDIAS))

print('Computing media norms...')

MEDIA_NORMS = {}

with open(OUTPUT_FILE2, 'w') as of:
    writer = csv.DictWriter(of, fieldnames=['media', 'tweets', 'users', 'shared_urls', 'user_vector_norm'])
    writer.writeheader()

    for media in MEDIAS:
        users = USER_VECTORS[media]
        MEDIA_NORMS[media] = math.sqrt(sum(map(lambda x: x * x, users.values())))

        writer.writerow({
            'media': media,
            'tweets': sum(users.values()),
            'users': len(users),
            'shared_urls': len(MEDIAS_URLS[media]),
            'user_vector_norm': MEDIA_NORMS[media]
        })

monopartite_cosine = nx.Graph()
monopartite_jaccard = nx.Graph()

print('Computing monopartite graph...')
bar = ProgressBar(max_value=len(MEDIAS))
for i in bar(range(len(MEDIAS))):
    media1 = MEDIAS[i]
    vector1 = USER_VECTORS[media1]
    norm1 = MEDIA_NORMS[media1]

    for j in range(i + 1, len(MEDIAS)):
        media2 = MEDIAS[j]
        vector2 = USER_VECTORS[media2]
        norm2 = MEDIA_NORMS[media2]

        # TODO: make option to pass norm to sparse_cosine_similarity
        dotproduct = sparse_dot_product(vector1, vector2)
        cosine = 0.0

        if norm1 != 0 and norm2 != 0:
            cosine = dotproduct / (norm1 * norm2)

        jaccard = weighted_jaccard_similarity(vector1, vector2)

        if cosine >= SIMILARITY_THRESHOLD:
            monopartite_cosine.add_edge(media1, media2, weight=cosine)

        if jaccard >= SIMILARITY_THRESHOLD:
            monopartite_jaccard.add_edge(media1, media2, weight=jaccard)

print('Resulting cosine monopartite graph has %i nodes and %i edges.' % (monopartite_cosine.order(), monopartite_cosine.size()))
nx.write_gexf(monopartite_cosine, (OUTPUT_FILE % "mono") + '-cosine.gexf')

print('Resulting jaccard monopartite graph has %i nodes and %i edges.' % (monopartite_jaccard.order(), monopartite_jaccard.size()))
nx.write_gexf(monopartite_jaccard, (OUTPUT_FILE % "mono") + '-jaccard.gexf')
