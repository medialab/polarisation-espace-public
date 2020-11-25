#!/usr/bin/env python3
import csv
from collections import defaultdict

MATCHING = './data/matching_final.csv'
HYPHE = './data/hyphe.csv'
OUTPUT = './data/final-corpus.csv'

MATCHES = defaultdict(list)

KEEP = {
    'ID': 'webentity_id',
    'NAME': 'name',
    'PREFIXES AS URL': 'prefixes',
    'HOME PAGE': 'home_page',
    'START PAGES': 'start_pages',
    'INDEGREE': 'indegree',
    'CREATION TIMESTAMP': 'hyphe_creation_timestamp',
    'LAST MODIFICATION TIMESTAMP': 'hyphe_last_modification_timestamp',
    'Portée (TAGS)': 'outreach',
    'fondation (TAGS)': 'foundation_year',
    'batch (TAGS)': 'batch',
    'edito (TAGS)': 'edito',
    'Parodique (TAGS)': 'parody',
    'origine (TAGS)': 'origin',
    'digital nativeness (TAGS)': 'digital_native'
}

with open(MATCHING) as mf:
    reader = csv.DictReader(mf)

    for line in reader:
        if not line['ID_hyphe']:
            continue

        id_mediacloud = line['id_mediacloud'] or line['id_mediacloud_speciaux']

        if id_mediacloud:
            MATCHES[line['ID_hyphe']].append(id_mediacloud)

with open(HYPHE) as cf, open(OUTPUT, 'w') as of:
    fieldnames = list(KEEP.values()) + ['mediacloud_ids']

    reader = csv.DictReader(cf)
    writer = csv.DictWriter(of, fieldnames=fieldnames)
    writer.writeheader()

    for line in reader:
        if line['type (TAGS)'] != 'media':
            continue

        formatted = {v: line[k] for k, v in KEEP.items()}
        formatted['mediacloud_ids'] = '|'.join(MATCHES.get(line['ID'], []))

        writer.writerow(formatted)
