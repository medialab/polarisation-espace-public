import os
import sys
import csv
import json
import gzip
from random import sample
from datetime import date
from collections import defaultdict

import casanova
from tqdm import tqdm


time_reducers = {
    "day": lambda dt: dt[0:10],
    "week": lambda dt: "-".join(str(b) for b in date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10])).isocalendar()[0:2]),
    "month": lambda dt: dt[0:7],
    "year": lambda dt: dt[0:4]
}


def filter_and_index_tweets(f, period="week", total=None, filter_threads=True, filter_retweets=True, filter_quotes=False):
    index = defaultdict(list)
    casa = casanova.reader(f)
    id_pos = casa.pos.id
    created_at_pos = casa.pos.created_at
    threads_pos = casa.pos.collected_via_thread_only
    RT_pos = casa.pos.retweeted_id
    quote_pos = casa.pos.quoted_id

    try:
        sampler = time_reducers[period]
    except KeyError:
        print("ERROR: no reducer for a period named %s" % period, file=sys.stderr)
        exit(1)

    try:
        for i, row in enumerate(tqdm(casa, total=total)):
            if (filter_threads and row[threads_pos] == "1") or \
               (filter_retweets and row[RT_pos]) or \
               (filter_quotes and row[quote_pos]):
                continue
            timeperiod = sampler(row[created_at_pos])
            index[timeperiod].append(i)

    except Exception as e:
        print("ERROR indexing while working on row #%s:" % i, row, file=sys.stderr)
        raise(e)

    return index


def sample_tweets(f, index, outdir, total=None, samples_sizes=[100]):
    casa = casanova.reader(f)
    samples_indexes = defaultdict(dict)
    outfiles = {}
    for siz in samples_sizes:
        for period, indexes in sorted(index.items()):
            lentweets = len(indexes)
            ntweets = min(siz, lentweets)
            outf = os.path.join(outdir, "%s_sample_%s.csv" % (period, siz))
            print("-", period, ":", lentweets, "filtered tweets to", ntweets, "->", outf)
            outfiles[outf] = {"file": open(outf, "w")}
            outfiles[outf]["writer"] = csv.writer(outfiles[outf]["file"])
            outfiles[outf]["writer"].writerow(casa.fieldnames)
            for i in sample(indexes, ntweets):
                samples_indexes[siz][i] = outfiles[outf]["writer"]

    try:
        for i, row in enumerate(tqdm(casa, total=total)):
            for siz, idx in samples_indexes.items():
                if i in idx:
                    idx[i].writerow(row)

    except Exception as e:
        print("ERROR sampling while working on row #%s:" % i, row, file=sys.stderr)
        raise(e)

    for outf in outfiles:
        outfiles[outf]["file"].close()


def gzip_open(filename):
    return gzip.open(filename, mode="rt")


if __name__ == "__main__":
    source = sys.argv[1]
    n_tweets = int(sys.argv[2]) if len(sys.argv) > 2 else None
    outdirectory = sys.argv[3] if len(sys.argv) > 3 else None

    open_wrapper = gzip_open if source.endswith(".gz") else open
    indexfile = source.replace(".gz", "").replace(".csv", ".idx")

    if not os.path.exists(indexfile) or not outdirectory:
        with open_wrapper(source) as f:
            setattr(sys.stdout, 'tell', lambda: 0)
            index = filter_and_index_tweets(f, period="week", total=n_tweets, filter_threads=True, filter_retweets=True, filter_quotes=False)
            with open(indexfile, "w") as idxf:
                json.dump(index, idxf)
    else:
        with open(indexfile) as idxf:
            index = json.load(idxf)

    if outdirectory:
        with open_wrapper(source) as f:
            setattr(sys.stdout, 'tell', lambda: 0)
            sample_tweets(f, index, outdirectory, total=n_tweets, samples_sizes=[500, 100000])
