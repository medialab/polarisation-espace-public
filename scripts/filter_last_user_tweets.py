import sys
import csv
import casanova

with open("/store/tweets/COVID19/190703_tweets_lancet_full.csv") as f:
  reader = casanova.reverse_reader(f)
  done = {}
  with open("/store/tweets/COVID19/190703_tweets_lancet_last_by_user.csv", "w") as g:
    writer = csv.writer(g)
    writer.writerow(reader.fieldnames)
    for row in reader:
      if row[reader.pos.from_user_name] not in done:
        writer.writerow(row)
        done[row[reader.pos.from_user_name]] = True

