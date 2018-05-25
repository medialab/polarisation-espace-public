#!/usr/bin/env python3
# =============================================================================
# Script training the classifier
# =============================================================================
#
# Processing Le Monde's stories to train a categories classifier.
#
import csv
from collections import Counter

STORIES = './data/lemonde.csv'
CATEGORIES = Counter()
NB_SUBSCRIPTION = 0
NB_VIDEO = 0

with open(STORIES, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:
        text = line['text'].strip()

        if 'video' in line['url']:
            NB_VIDEO += 1
            continue

        if text.endswith('...'):
            NB_SUBSCRIPTION += 1
            continue

        category = line['url'].split('lemonde.fr/')[1].split('/', 1)[0]
        CATEGORIES[category] += 1

print('Found %i subscription articles.' % NB_SUBSCRIPTION)
print('Found %i video articles.' % NB_VIDEO)
print('Categories:')

for category, count in CATEGORIES.most_common():
    print('  %s: %i' % (category, count))
