import sys
import csv
import gzip
from collections import defaultdict
from pymongo import MongoClient

import casanova
from tqdm import tqdm
from ural import normalize_url

from tweets_metas import get_field


# Read list urls to filter
def read_list_urls(list_urls_file):
    categories_medias_urls = defaultdict(lambda: defaultdict(set))
    with open(list_urls_file, "r") as f:
        for row in csv.DictReader(f):
            url = normalize_url(row["clean_url"].strip())
            categories_medias_urls[row["niv0"]][row["webentity"]].add(url)
    return categories_medias_urls


def filter_and_enrich_tweets_from_mongo(db, cat_urls, of=sys.stdout):
    categories = list(cat_urls.keys())
    fields = "id,time,created_at,from_user_name,text,filter_level,possibly_sensitive,withheld_copyright,withheld_scope,withheld_countries,truncated,retweet_count,favorite_count,reply_count,lang,to_user_name,to_user_id,in_reply_to_status_id,source,source_name,source_url,location,lat,lng,from_user_id,from_user_realname,from_user_verified,from_user_description,from_user_url,from_user_profile_image_url,from_user_utcoffset,from_user_timezone,from_user_lang,from_user_tweetcount,from_user_followercount,from_user_friendcount,from_user_favourites_count,from_user_listed,from_user_withheld_scope,from_user_withheld_countries,from_user_created_at,collected_via_search,collected_via_stream,collected_via_thread_only,collected_at_timestamp,retweeted_id,retweeted_user_name,retweeted_user_id,quoted_id,quoted_user_name,quoted_user_id,links,medias_urls,medias_files,mentioned_user_names,mentioned_user_ids,hashtags".split(",")
    headers = fields + ["matched_urls", "webentities"] + categories
    writer = csv.DictWriter(of, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()

    for t in tqdm(db.find(), total=db.count()):
        if len(t.keys()) < 10:
            continue
        for f in fields:
            t[f] = get_field(f, t)
        try:
            links = [normalize_url(u) for u in t["links"].split('|')]
            if not links:
                continue

            t["matched_urls"] = []
            t["webentities"] = set()
            for cat in categories:
                cat_match = False
                for we, urls in cat_urls[cat].items():
                    for u in links:
                        if u in urls:
                            cat_match = True
                            t["matched_urls"].append(u)
                            t["webentities"].add(we)
                            links.remove(u)
                t[cat] = cat_match

            if t["webentities"]:
                t["matched_urls"] = "|".join(t["matched_urls"])
                t["webentities"] = "|".join(t["webentities"])
                writer.writerow(t)

        except Exception as e:
            print("ERROR while processing", t, file=sys.stderr)
            raise(e)


def filter_and_enrich_tweets_from_csv(f, cat_urls, of=sys.stdout, total=None):
    categories = list(cat_urls.keys())
    casa = casanova.enricher(f, of, add=["matched_urls", "webentities"] + categories)
    links_pos = casa.pos.links

    for row in tqdm(casa, total=total):
        try:
            links = [normalize_url(u) for u in row[links_pos].split('|')]
            if not links:
                continue

            matched_urls = []
            webentities = set()
            cat_belongings = []
            for cat in categories:
                cat_match = False
                for we, urls in cat_urls[cat].items():
                    for u in links:
                        if u in urls:
                            cat_match = True
                            matched_urls.append(u)
                            webentities.add(we)
                            links.remove(u)
                cat_belongings.append(cat_match)

            if webentities:
                casa.writerow(row, ["|".join(matched_urls), "|".join(webentities)] + cat_belongings)

        except Exception as e:
            print("ERROR while processing", row, file=sys.stderr)
            raise(e)


def gzip_open(filename):
    return gzip.open(filename, mode="rt")


if __name__ == "__main__":
    list_urls_file = sys.argv[1]
    source = sys.argv[2]
    csv_lines = int(sys.argv[3]) if len(sys.argv) > 3 else None

    cat_urls = read_list_urls(list_urls_file)

    if source.endswith(".csv") or source.endswith(".gz"):
        # read tweets from tweets archive (csv possibly gzipped)
        open_wrapper = gzip_open if source.endswith(".gz") else open
        with open_wrapper(source) as f:
            setattr(sys.stdout, 'tell', lambda: 0)
            filter_and_enrich_tweets_from_csv(f, cat_urls, total=csv_lines)

    else:
        # read tweets from mongodb
        mongodb = MongoClient('localhost', 27017)[source]['tweets']
        filter_and_enrich_tweets_from_mongo(mongodb, cat_urls)
