#!/usr/bin/env python3
# =============================================================================
# Script to merge Hyphe data unto the sources.
# =============================================================================
#
# This script reads data exported from Hyphe and add web entities information
# to our sources.
#
import codecs
import csv

HYPHE_FILE = './data/hyphe.csv'
SOURCES_FILE = './data/sources.csv'
OUTPUT_FILE = './data/sources-with-hyphe-data.csv'

# Indexing sources
SOURCES_INDEX = {}
SOURCES_HEADERS = None

def normalize_source_url(url):

    if 'antipresse' in url:
        return 'antipresse.net'

    return (
        url
            .replace('accueil.html', '')
            .rstrip('/')
    )

with open(SOURCES_FILE, 'r') as f:
    reader = csv.DictReader(f)
    SOURCES_HEADERS = reader.fieldnames

    for line in reader:
        SOURCES_INDEX[normalize_source_url(line['url'])] = line

# Pairing
with codecs.open(HYPHE_FILE, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)

    for line in reader:
        status = line['STATUS']
        prefixes = line['PREFIXES AS URL'].split(' ')

        if status == 'UNDECIDED':

            # Adding
            url = prefixes[0]
            SOURCES_INDEX[url] = {
                'id': line['ID'],
                'url': url,
                'batch': 2,
                'webentity': line['NAME'],
                'prefixes': '|'.join(prefixes)
            }

            continue

        source = None

        for prefix in prefixes:
            prefix = (
                prefix
                    .replace('http://', '')
                    .replace('https://', '')
                    .rstrip('/')
            )

            source = SOURCES_INDEX.get(prefix)

            if source is None:
                source = SOURCES_INDEX.get('www.' + prefix)

            if source is not None:
                break

        if source is None:
            print('Could not match %s' % prefixes[0])
            raise Exception('Aborting.')

        source['id'] = line['ID']
        source['webentity'] = line['NAME']
        source['prefixes'] = '|'.join(prefixes)

# Output, sorted by batch then name
SOURCES_HEADERS.extend(['id', 'webentity', 'prefixes'])

with open(OUTPUT_FILE, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=SOURCES_HEADERS)
    writer.writeheader()

    sources = sorted(SOURCES_INDEX.values(), key=lambda x: (str(x['batch']), x.get('name', x['url'])))

    for source in sources:
        writer.writerow(source)
