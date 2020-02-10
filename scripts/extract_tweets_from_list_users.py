import os
import sys
import csv
import gzip
import time
from datetime import datetime

# Importing own lib
sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie


def isodate_to_timestamp(dat):
    tim = datetime.strptime(dat, "%Y-%m-%d").timetuple()
    return time.mktime(tim)


# Read list users to keep
def read_list_users(list_users_file):
    list_users = {}
    with open(list_users_file, "r") as f:
        for row in csv.reader(f):
            list_users[row[0].lower()] = row[1]
    return list_users


def filter_tweets(tweets_iterator, list_users, start_timestamp, end_timestamp, medias_trie):
    try:
        for i, t in enumerate(tweets_iterator):
            #print(i, t["id"], t["from_user_name"].lower(), start_timestamp, float(t["time"]), end_timestamp, file=sys.stderr)
            # filter tweets by user
            if (t["from_user_name"].lower() not in list_users or
            # filter tweets by timestamp
                not (start_timestamp < float(t["time"]) < end_timestamp)):
                continue
            # extract medias from links
            t["medias"] = []
            for link in t["links"].split("|"):
                media = medias_trie.longest(link)
                if media:
                    t["medias"].append(media)
            t["medias"] = "|".join(t["medias"])
            yield t
    except Exception as e:
        print("ERROR after line", i, t, file=sys.stderr)
        raise(e)

def gzip_open(filename):
    return gzip.open(filename, mode="rt")

if __name__ == "__main__":
    list_users_file = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    medias_file = sys.argv[4]
    first_corpus_csv = sys.argv[5]
    #mongo_db_1 = sys.argv[6]
    #mongo_db_2 = sys.argv[7]

    headers = "id,created_at,from_user_name,from_user_id,text,retweet_count,favorite_count,to_user_name,to_user_id,lat,lng,from_user_tweetcount,from_user_followercount,from_user_friendcount,from_user_favourites_count,from_user_listed,from_user_created_at,collected_at_timestamp,retweeted_user_name,retweeted_user_id,quoted_user_name,quoted_user_id,mentioned_user_names,mentioned_user_ids,hashtags,links,medias".split(",")
    writer = csv.DictWriter(sys.stdout, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()

    medias_trie = LRUTrie.from_csv(medias_file, detailed=False, urlfield='PREFIXES AS URL', urlseparator=' ', namefield="NAME", filterrows={"type (TAGS)": "media"})
    # print(medias_trie.values, file=sys.stderr)

    list_users = read_list_users(list_users_file)
    # print(len(list_users), file=sys.stderr, file=sys.stderr)

    start_timestamp = isodate_to_timestamp(start_date)
    end_timestamp = isodate_to_timestamp(end_date) + 86400
    # print(start_timestamp, end_timestamp, file=sys.stderr)

    # read tweets from first corpus (csv)
    open_wrapper = gzip_open if first_corpus_csv.endswith(".gz") else open
    with open_wrapper(first_corpus_csv) as f:
        for t in filter_tweets(csv.DictReader(f), list_users, start_timestamp, end_timestamp, medias_trie):
            writer.writerow(t)

    # read tweets from second corpus (mongo)

    # read tweets from second corpus extra (mongo)
