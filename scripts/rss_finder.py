#!/usr/bin/env python3
# =============================================================================
# Script to find RSS feeds for missing entries in mediacloud
# =============================================================================
#
# Some entries are missing in mediacloud. We therefore need to find them
# before being able to add them to mediacloud.
#
import csv
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin

MATCHING = './data/matching_final.csv'
CORPUS = './data/hyphe.csv'
OUTPUT = './data/hyphe-with-rss.csv'

MATCHES = defaultdict(list)
MISSING = set()

with open(MATCHING) as mf:
    reader = csv.DictReader(mf)

    for line in reader:
        if not line['ID_hyphe']:
            continue

        if not line['id_mediacloud']:
            MISSING.add(line['ID_hyphe'])
        else:
            MATCHES[line['ID_hyphe']].append(line['id_mediacloud'])

WEBENTITIES = {}
FIELDNAMES = None

with open(CORPUS) as cf:
    reader = csv.DictReader(cf)
    FIELDNAMES = reader.fieldnames

    for line in reader:
        if line['type (TAGS)'] != 'media':
            continue

        WEBENTITIES[line['ID']] = line

def find_rss_feeds(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    links = soup.select('link[type="application/rss+xml"][href], link[type="application/atom+xml"][href]')

    rss = set(urljoin(r.url, link.get('href')) for link in links)

    return rss

MISSING_RSS_FEED = defaultdict(set)

for weid in MISSING:
    we = WEBENTITIES[weid]

    print('Investigating %s' % we['NAME'])

    urls = [we['HOME PAGE']]
    urls += we['START PAGES'].split(' ')

    for url in urls:
        print('  Fetching %s' % url)
        rss = find_rss_feeds(url)
        MISSING_RSS_FEED[weid].update(rss)
        if len(rss) != 0:
            print('  Found %i feed(s):' % len(rss))

            for l in rss:
                print('    - %s' % l)

    print()

FIELDNAMES += ['missing', 'mediacloud_ids', 'rss_feeds']

with open(OUTPUT, 'w') as of:
    writer = csv.DictWriter(of, fieldnames=FIELDNAMES)
    writer.writeheader()

    for weid, line in WEBENTITIES.items():
        if weid in MISSING:
            line['missing'] = 'yes'
            line['rss_feeds'] = ' '.join(MISSING_RSS_FEED[weid])
        else:
            line['mediacloud_ids'] = '|'.join(MATCHES[weid])

        writer.writerow(line)
