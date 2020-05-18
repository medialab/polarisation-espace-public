import csv, json
from collections import defaultdict

cats = defaultdict(int)
users = defaultdict(lambda: defaultdict(int))

keys = "Identitarian,Centre,Alternative Health & UFOs,Right Wing,Tabloids & Health Magazines,Hyper-centre,Leisure and Health,Alternative Health,Left Wing,Revolutionary Right,Regional Daily Press,PQR & Mag,IT & Consumer,Regional Daily Press (East)".split(",")

with open("200515_polarisation_fakenews_wheel_.csv") as f:
  data = list(csv.DictReader(f))

for l in data:
  for k in keys:
    if l[k] == "True":
      users[l["from_user_name"]][k] += 1
      users[l["from_user_name"]]["TOTAL"] += 1
      cats[k] += 1
      if l["retweeted_id"]:
        users[l["from_user_name"]][k + " (retweets)"] += 1
        users[l["from_user_name"]]["TOTAL (retweets)"] += 1
        cats[k + " (retweets)"] += 1
      elif l["quoted_id"]:
        users[l["from_user_name"]][k + " (quotes)"] += 1
        users[l["from_user_name"]]["TOTAL (quotes)"] += 1
        cats[k + " (quotes)"] += 1
      else:
        users[l["from_user_name"]][k + " (original)"] += 1
        users[l["from_user_name"]]["TOTAL (original)"] += 1
        cats[k + " (original)"] += 1

totalkeys = ["TOTAL"] + keys
allkeys = []
for k in totalkeys:
  allkeys.append(k)
  for extra in ["original", "retweets", "quotes"]:
    allkeys.append("%s (%s)" % (k, extra))

with open("fakenews_sharers.csv", "w") as f:
  print >> f, "user," + ",".join(allkeys)
  for u, v in users.items():
    print >> f, u+","+",".join([str(v[k]) for k in allkeys])

print(json.dumps(cats, indent=2, sort_keys=True))

