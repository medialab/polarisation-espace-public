import csv
import datetime
from random import sample


followers_metadata_out = []
followers_metadata_kept = []

follower_id = set()

# 23 avril 2021 19h15 : date de collecte 
# timestamp utc : 1619205300
stime = "23/04/2021 19:15"
collect_date = int(datetime.datetime.strptime(stime, "%d/%m/%Y %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp())

# Après avoir passé cette commande:
# xsv select 4 followers_graines_out.csv -o follower_id_followers_graines_out.csv
with open("follower_id_followers_graines_out.csv") as f:
    filereader = csv.reader(f)
    for row in filereader:
        follower_id.add(row[0])

# to fix this error : _csv.Error: line contains NUL 
# sed 's/\x0/ /g' followers_metadata.csv > fixed_followers_metadata.csv
with open("fixed_followers_metadata.csv") as g:
    filereader = csv.DictReader(g)

    headers = filereader.fieldnames

    for row in filereader:
        try:
            if row["timestamp_utc"] != '':
                debut_date = int(row["timestamp_utc"])
                active_years_in_seconds = (collect_date - debut_date) 
                active_years = int(active_years_in_seconds) / (3600 * 24 * 365.25)
                tweets_per_year = int(row["tweets"]) / active_years
                if row["follower_id"] in follower_id or int(row["followers"]) < 30 or tweets_per_year < 12:
                    followers_metadata_out.append(row)
                else:
                    followers_metadata_kept.append(row)
        except Exception as e:
            print(e)
            print(row)

with open("followers_metadata_out.csv", "w") as h:
    filewriter = csv.DictWriter(h, fieldnames=headers)
    filewriter.writeheader()
    filewriter.writerows(followers_metadata_out)

id = set()
for follower in followers_metadata_kept:
    id.add(follower["follower_id"])
followers = list(id)

last2000followers = []
last2000followers_ids = sample(followers, 2000)
ids = set(last2000followers_ids)
for element in followers_metadata_kept:
    if element["follower_id"] in ids:
        last2000followers.append(element)

with open("followers_metadata_kept.csv", "w") as csvfile:
    file_writer = csv.DictWriter(csvfile, fieldnames=headers)
    file_writer.writeheader()
    file_writer.writerows(last2000followers)

