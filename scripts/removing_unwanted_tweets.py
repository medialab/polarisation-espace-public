import csv

followers = set()

with open("followers_metadata_kept.csv") as f:
    filereader_f = csv.DictReader(f)

    for row in filereader_f:
        followers.add(row["follower_id"])

with open("tweets_mentionnant_les_graines_depuis_20200101.csv") as g, open("2000_followers_tweets_mentionnant_les_graines_depuis_20200101.csv", "w") as h:
    filereader = csv.reader(g)
    headers = next(filereader)
    count = 0
    for i in range(len(headers)):
        if headers[i] == "url":
            count += 1
        if count == 2 and headers[i] == "url":
            headers[i] = "tweet_url"

    filewriter = csv.writer(h)
    filewriter.writerow(headers)

    for row in filereader:
        if row[23] in followers:
            filewriter.writerow(row)