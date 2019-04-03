#!/usr/bin/env python3
# =============================================================================
# Script joining medialab urls to our own corpus
# =============================================================================
#
import csv
import sys
from ural import LRUTrie, normalize_url
from argparse import ArgumentParser, FileType

csv.field_size_limit(sys.maxsize)

# CLI Endpoint
parser = ArgumentParser(prog='join')
parser.add_argument('sources', help='CSV files of sources', type=FileType('r'))
parser.add_argument('target', help='Target CSV file', type=FileType('r'))
parser.add_argument('-o', '--output', help='output file', type=FileType('w'), default=sys.stdout)

args = parser.parse_args()

# Indexing
trie = LRUTrie(strip_trailing_slash=True)
index = {}

for line in csv.DictReader(args.sources):
    trie.set(normalize_url(line['url'], strip_trailing_slash=True), line)
    index[line['mediacloud_id']] = line

reader = csv.DictReader(args.target)
writer = csv.DictWriter(args.output, fieldnames=reader.fieldnames + ['polarisation_id', 'polarisation_name', 'webentity'])
writer.writeheader()

for line in reader:
    url = line['url']

    addendum = {
        'polarisation_id': '',
        'polarisation_name': '',
        'webentity': ''
    }

    match = trie.match(normalize_url(url, strip_trailing_slash=True))

    if match is None:
        match = index.get(line['media_id'])

    if match is not None:
        addendum['polarisation_id'] = match['id']
        addendum['polarisation_name'] = match['name']
        addendum['webentity'] = match['webentity']

    line.update(addendum)

    writer.writerow(line)
