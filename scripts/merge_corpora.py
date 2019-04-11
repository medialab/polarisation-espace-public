#!/usr/bin/env python3
# =============================================================================
# Script attempting to merge sources from a variety of different corpora
# =============================================================================
#
import csv
from os.path import join
from ural import LRUTrie

SOURCES = './data/sources.csv'
HYPHE = './data/corpora/corpus_hyphe_curated.csv'
CORPORA_LIST = './data/corpora/corpora.csv'
NOT_FOUND = './data/not-found.csv'
SOCIAL = './data/social.csv'

TRIE = LRUTrie(strip_trailing_slash=True)
SOCIAL_TRIE = LRUTrie(strip_trailing_slash=True)

SOCIAL_TRIE.set('twitter.com', 'twitter')
SOCIAL_TRIE.set('twitter.fr', 'twitter')
SOCIAL_TRIE.set('facebook.com', 'facebook')
SOCIAL_TRIE.set('facebook.fr', 'facebook')

# Reading master corpus
with open(SOURCES) as f:
    for line in csv.DictReader(f):
        TRIE.set(line['url'], {'polarisation': line})

# Reading hyphe corpus
with open(HYPHE) as f, open(SOCIAL, 'w') as of:
    reader = csv.DictReader(f)
    writer = csv.DictWriter(of, fieldnames=reader.fieldnames + ['twitter', 'facebook', 'twitter_count', 'facebook_count'])
    writer.writeheader()

    for line in reader:
        prefixes = line['PREFIXES AS URL'].split(' ')
        match = None

        for prefix in prefixes:
            match = TRIE.match(prefix)

            if match is not None:
                match['hyphe'] = line

                for prefix in prefixes:
                    TRIE.set(prefix, match)

                break

        twitter = [p for p in prefixes if SOCIAL_TRIE.match(p) == 'twitter']
        facebook = [p for p in prefixes if SOCIAL_TRIE.match(p) == 'facebook']

        line['twitter'] = '|'.join(twitter)
        line['facebook'] = '|'.join(facebook)
        line['twitter_count'] = len(twitter)
        line['facebook_count'] = len(facebook)

        writer.writerow(line)

        if match is None:
            # TODO: output them
            print('Could not match', line['NAME'], line['STATUS'])

# Reading other corpora
with open(CORPORA_LIST) as f, open(NOT_FOUND, 'w') as nf:
    writer = csv.DictWriter(nf, fieldnames=['corpus', 'url', 'name'])
    writer.writeheader()

    for line in csv.DictReader(f):

        url_field = line['url']
        name_field = line['name']

        # Skipping corpora without url information for now
        if not url_field:
            continue

        with open(join('.', 'data', 'corpora', line['filename'])) as g:
            for l in csv.DictReader(g):
                url = l[url_field]
                name = l.get(name_field, '')

                match = TRIE.match(url)

                if match is not None:
                    match[line['filename']] = l
                else:
                    writer.writerow({
                        'corpus': line['filename'],
                        'url': url,
                        'name': name
                    })
