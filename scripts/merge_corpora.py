#!/usr/bin/env python3
# =============================================================================
# Script attempting to merge sources from a variety of different corpora
# =============================================================================
#
import re
import csv
from os.path import join
from ural import LRUTrie
from fog.key import create_fingerprint, create_ngrams_fingerprint

STRIP_PARENTHIZED = re.compile(r'\([^)]*\)')
STRIP_ARTICLES = re.compile(r"(?:l['’]|l[ae]\b|les\b)", re.I)
STRIP_TLD = re.compile(r'\.[a-z]{1,4}$', re.I)

SOURCES = './data/sources.csv'
HYPHE = './data/corpora/corpus_hyphe_curated.csv'
CORPORA_LIST = './data/corpora/corpora.csv'
NOT_FOUND = './data/not-found.csv'
SOCIAL = './data/social.csv'

FILTERS = {
    'factiva-no-urls.csv': lambda line: line['Language (slg)'] == 'French'
}

NAME_PROCESSORS = {
    'factiva-no-urls.csv': lambda name: re.sub(STRIP_PARENTHIZED, '', name).strip()
}

fingerprint = create_fingerprint(split=('-'))
def custom_fingerprint(string):
    return fingerprint(re.sub(STRIP_ARTICLES, '', re.sub(STRIP_TLD, '', string)))

ngrams_fingerprint = create_ngrams_fingerprint(split=('-'))
def custom_ngrams_fingerprint(string):
    return ngrams_fingerprint(2, re.sub(STRIP_ARTICLES, '', re.sub(STRIP_TLD, '', string)))


TRIE = LRUTrie(strip_trailing_slash=True)
SOCIAL_TRIE = LRUTrie(strip_trailing_slash=True)
NAME_INDEX = {}
NGRAMS_NAME_INDEX = {}

SOCIAL_TRIE.set('twitter.com', 'twitter')
SOCIAL_TRIE.set('twitter.fr', 'twitter')
SOCIAL_TRIE.set('facebook.com', 'facebook')
SOCIAL_TRIE.set('facebook.fr', 'facebook')

# Reading master corpus
with open(SOURCES) as f:
    for line in csv.DictReader(f):
        record = {'polarisation': line}
        TRIE.set(line['url'], record)
        NAME_INDEX[custom_fingerprint(line['name'])] = record
        NGRAMS_NAME_INDEX[custom_ngrams_fingerprint(line['name'])] = record

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
        else:
            NAME_INDEX[custom_fingerprint(line['NAME'])] = match
            NGRAMS_NAME_INDEX[custom_ngrams_fingerprint(line['NAME'])] = record

# Reading other corpora
with open(CORPORA_LIST) as f, open(NOT_FOUND, 'w') as nf:
    writer = csv.DictWriter(nf, fieldnames=['corpus', 'url', 'name'])
    writer.writeheader()

    for line in csv.DictReader(f):
        corpus = line['filename']
        print('Merging %s' % corpus)

        url_field = line['url']
        name_field = line['name']

        preprocessor = NAME_PROCESSORS.get(corpus)
        filtering = FILTERS.get(corpus)

        with open(join('.', 'data', 'corpora', corpus)) as g:
            for l in csv.DictReader(g):

                if filtering and not filtering(l):
                    continue

                url = l.get(url_field) if url_field else None
                name = l.get(name_field) if name_field else None
                match = None

                if preprocessor and name:
                    name = preprocessor(name)

                if url is not None:
                    match = TRIE.match(url)

                if name is not None and match is None:
                    match = NAME_INDEX.get(custom_fingerprint(name))

                    if match is None:
                        match = NGRAMS_NAME_INDEX.get(custom_ngrams_fingerprint(name))

                if match is not None:
                    match[corpus] = l
                else:
                    writer.writerow({
                        'corpus': corpus,
                        'url': url or '',
                        'name': name or ''
                    })
