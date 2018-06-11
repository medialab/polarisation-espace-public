#!/usr/bin/env python3
# =============================================================================
# Script to merge nested block data unto the sources.
# =============================================================================
#
import csv

NESTED_BLOCKS = './data/nested_blocks.csv'
SOURCES_FILE = './data/sources.csv'

NB_INDEX = {}

with open(NESTED_BLOCKS, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:
        NB_INDEX[line['site']] = line

with open(SOURCES_FILE, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:

        if line['webentity'] not in NB_INDEX:
            print()
            continue

        indexed = NB_INDEX[line['webentity']]

        content = [indexed['level %i' % i] for i in range(4)]
        content += [indexed['level %i title' % i] for i in range(4)]

        print('\t'.join(content))
