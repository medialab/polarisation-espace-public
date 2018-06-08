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
from collections import OrderedDict

HYPHE_FILE = './data/hyphe.csv'
SOURCES_FILE = './data/sources.csv'

HYPHE_INDEX = {}

with codecs.open(HYPHE_FILE, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)

    for line in reader:
        tags = OrderedDict()

        for k, v in line.items():
            if 'TAGS' not in k:
                continue

            tag = k.replace(' (TAGS)', '')
            tags[tag] = v

        HYPHE_INDEX[line['ID']] = tags

with open(SOURCES_FILE, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:

        if line['id'] not in HYPHE_INDEX:
            print()
            continue

        tags = HYPHE_INDEX[line['id']]

        print('\t'.join(list(tags.values())))
