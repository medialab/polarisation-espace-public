import sys
import csv
import gzip
from collections import defaultdict

from io import StringIO
import requests
import casanova
from tqdm import tqdm
from ural import normalize_url
from ural.lru import NormalizedLRUTrie as LRUTrie

from tweets_metas import get_field


def build_medias_trie():
    trie = LRUTrie(tld_aware=True)
    corpus_url = "https://raw.githubusercontent.com/medialab/corpora/master/polarisation/medias.csv"
    print("INFO: Building LRUTrie for %s..." % corpus_url, file=sys.stderr)
    corpus_data = requests.get(corpus_url).text
    for media in csv.DictReader(StringIO(corpus_data)):
        for url in media["prefixes"].split("|"):
            trie.set(url, media["name"])
    return trie



def extract_users_urls_medias_from_csv(f, trie, of=sys.stdout, total=None, filter_fr=False, min_date=None):
    headers = ['tweet_id', 'user_screen_name', 'user_id',
               'normalized_url', 'domain_name', 'webentity',
               'datetime', 'is_retweet', 'nb_followers']
    writer = csv.writer(of)
    writer.writerow(headers)
    casa = casanova.reader(f)
    try:
        for row, (tid, uname, uid, dtime, rtid, nbfols, links, lang) in tqdm(enumerate(
          casa.cells(['id', 'from_user_name', 'from_user_id', 'created_at',
                      'retweeted_id', 'from_user_followercount', 'links', 'lang'])),
          total=total):
            if filter_fr and lang != 'fr':
                continue
            if min_date and dtime < min_date:
                continue
            is_rt = (rtid != '')
            for url in links.split('|'):
                url = url.strip()
                if not url:
                    continue
                webentity = trie.match(url)
                normalized = normalize_url(url)
                domain = normalized.split("/")[0]
                if not webentity:
                    #if "twitter.com/" not in url and "youtube.com" not in url:
                    #    print('WARNING: url unmatched on row #%s: %s' % (row, domain), file=sys.stderr)
                    continue
                writer.writerow([tid, uname, uid, normalized, domain, webentity, dtime, is_rt, nbfols])

    except Exception as e:
        print('ERROR while processing row #%s (https://twitter.com/%s/statuses/%s)' % (row, uname, tid), file=sys.stderr)
        raise(e)


def gzip_open(filename):
    return gzip.open(filename, mode="rt")


if __name__ == "__main__":

    filter_fr = False
    if "--fr" in sys.argv:
        filter_fr = True
        sys.argv.remove("--fr")

    min_date = None
    if "--min-date" in sys.argv:
        min_date = sys.argv[sys.argv.index('--min-date') + 1]
        sys.argv.remove("--min-date")
        sys.argv.remove(min_date)

    source = sys.argv[1]

    csv_lines = int(sys.argv[2]) if len(sys.argv) > 2 else None

    trie = build_medias_trie()

    # read tweets from tweets archive (csv possibly gzipped)
    open_wrapper = gzip_open if source.endswith(".gz") else open
    with open_wrapper(source) as f:
        setattr(sys.stdout, 'tell', lambda: 0)
        extract_users_urls_medias_from_csv(f, trie, total=csv_lines, filter_fr=filter_fr, min_date=None)
