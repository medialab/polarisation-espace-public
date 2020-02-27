import os
import sys
from ural import normalize_url
from pymongo import MongoClient

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie

def extract_media_urls(db, trie):
    print("url,media")
    done = set()
    for tweet in db.find({"langs": "fr"}, projection=["links", "proper_links"]):
        for link in tweet.get("proper_links", tweet["links"]):
            link = normalize_url(link, strip_irrelevant_subdomain=False, strip_protocol=False)
            if link in done:
                continue
            done.add(link)
            media = trie.longest(link)
            if media:
                print('"%s","%s"' % (link.replace('"', '""'), media.replace('"', '""')))

if __name__ == "__main__":
    medias_file = sys.argv[1]
    mongo_db = sys.argv[2]

    medias_trie = LRUTrie.from_csv(medias_file, detailed=False, urlfield='PREFIXES AS URL', urlseparator=' ', namefield="NAME", filterrows={"type (TAGS)": "media"})

    # read tweets from second corpus (mongo)
    db = MongoClient('localhost', 27017)[mongo_db]['tweets']
    extract_media_urls(db, medias_trie)
