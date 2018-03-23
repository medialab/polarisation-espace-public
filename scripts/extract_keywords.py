#!/usr/bin/env python3
import csv
from collections import defaultdict
from urllib.parse import urlparse

# Parameters
INPUT_FILE = './data/sources_mediacloud.csv'
DEBUG = False

PROBLEMATIC_HOSTS = frozenset([
    'blogs.',
    'blogspot',
    'canalblog',
    'over-blog',
    'tumblr',
    'wordpress'
])

# State
HOSTS = defaultdict(list)

# Process
with open(INPUT_FILE, 'r') as f:
    reader = csv.DictReader(f)

    for line in reader:
        url = line['url']
        parsed = urlparse('http://' + url)
        netloc = parsed.netloc.replace('www.', '')

        if (
            netloc.startswith('fr.') or
            netloc.startswith('francais.') or
            netloc.endswith('.ek.la') or
            netloc.endswith('.free.fr')
        ):
            host = netloc
        elif 'vice.com' in netloc:
            host = netloc + parsed.path
        else:
            span = 3 if any(host in netloc for host in PROBLEMATIC_HOSTS) else 2
            host = '.'.join(netloc.split('.')[-span:])

        HOSTS[host].append((line['name'], url))

# Debug
if DEBUG:
    for host, items in HOSTS.items():
        if len(items) > 1:
            print('Found %s %i times.' % (host, len(items)))

            for name, url in items:
                print('  %s - %s' % (name, url))

            print()

    print('%i total hosts' % len(HOSTS))
else:
    for host in sorted(HOSTS.keys()):
        print(host)
