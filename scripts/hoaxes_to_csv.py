#!/usr/bin/env python3
import csv
import json

HOAXES = './data/hoaxes.json'
OUTPUT = './data/hoaxes.csv'

index = {}

with open(HOAXES) as f, open(OUTPUT, 'w') as of:
    data = json.load(f)
    writer = csv.DictWriter(of, fieldnames=['url', 'title', 'verdict', 'description', 'debunk'])
    writer.writeheader()

    for identifier, meta in data['debunks'].items():
        index[identifier] = {
            'title': meta[0],
            'verdict': meta[1],
            'description': meta[2],
            'debunk': meta[3]
        }

    for url, identifier in data['hoaxes'].items():
        meta = index.get(identifier).copy()
        meta['url'] = url
        writer.writerow(meta)
