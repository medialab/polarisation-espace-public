#!/usr/bin/env python3
# =============================================================================
# Script to merge Hyphe failed crawls
# =============================================================================
#
import csv

MEDIA_FILE = './data/sources.csv'
FAILED_CRAWLS = './data/crawls-polarisation-failed.csv'

FAILED = set()

with open(FAILED_CRAWLS, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:
        FAILED.add(line['webentity_id'])

with open(MEDIA_FILE, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:
        if line['id'] in FAILED:
            print(0)
        else:
            print(1)
