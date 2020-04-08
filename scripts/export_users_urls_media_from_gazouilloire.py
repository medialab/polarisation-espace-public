#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, sys
import progressbar
from pymongo import MongoClient
from ural import normalize_url
from ural.lru import LRUTrie
from gazouilloire.web.export import format_csv, isodate

trie = LRUTrie(tld_aware=True)
if len(sys.argv) > 1:
    medias_file = sys.argv[1]
    print >> sys.stderr, "INFO: Building LRUTrie for %s..." % medias_file
    import csv
    with open(medias_file) as f:
        for media in csv.DictReader(f):
            if media["type (TAGS)"] != "media":
                continue
            for url in media["PREFIXES AS URL"].split(" "):
                trie.set(url, media["NAME"].decode("utf-8"))

with open('config.json') as confile:
    conf = json.loads(confile.read())

db = MongoClient(conf['mongo']['host'], conf['mongo']['port'])[conf['mongo']['db']]['tweets']

query = {}
print >> sys.stderr, "INFO: Counting matching results..."
count = db.count(query)

print >> sys.stderr, "INFO: Building and storing csv data..."
print "user_id,user_screenname,link,domain,media,datetime,is_retweet,followers"
bar = progressbar.ProgressBar(max_value=count)
for t in bar(db.find(query, limit=count, projection={"user_screen_name": 1, "user_id_str": 1, "links": 1, "proper_links": 1, "retweet_id": 1, "created_at": 1, "user_followers": 1})):
    links = t.get("proper_links", t["links"])
    if not links:
        continue
    name = t.get("user_screen_name")
    uid = t.get("user_id_str")
    dtime = isodate(t["created_at"])
    isRT = str(1 if t["retweet_id"] else 0)
    fols = str(t["user_followers"])
    for l in links:
        try:
            lnk = normalize_url(l.decode("utf-8"))
        except Exception as e:
            print >> sys.stderr, "ERROR: url misformatted", l, type(e), e
            lnk = l
        try:
            domain = normalize_url(l.split("/")[2])
        except Exception as e:
            print >> sys.stderr, "ERROR: normalizing domain for url", l, type(e), e
            domain = ""
        try:
            media = trie.match(l) or ""
        except Exception as e:
            print >> sys.stderr, "ERROR: LRUtrie matching crashes for url", l, type(e), e
            media = ""
        print ",".join([format_csv(v) for v in [uid, name, lnk, domain, media, dtime, isRT, fols]])
