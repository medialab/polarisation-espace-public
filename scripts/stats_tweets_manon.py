import csv, json, sys
from collections import defaultdict

cats = defaultdict(int)
users = defaultdict(lambda: defaultdict(int))

keys = "Identitarian,Centre,Alternative Health & UFOs,Right Wing,Tabloids & Health Magazines,Hyper-centre,Leisure and Health,Alternative Health,Left Wing,Revolutionary Right,Regional Daily Press,PQR & Mag,IT & Consumer,Regional Daily Press (East)".split(",")
keys = "Identitarian,Centre,Parallel Universes,Right Wing,Lifestyle magazines,Hyper-centre,Left Wing,Revolutionary Right,Local Press,IT & Consumer".split(",")
keys = "Nationale-Révolutionnaire,Extrême-droite identitaires,Mondes alternatifs,Médias de droite,Centre,Presse locale et régionale,Magazines spécialisés,Médias de gauche,Hyper-centre".split(",")
keys = "Left Wing,Hyper-centre,Right Wing,IT & Consumer,Lifestyle magazines,Identitarian,Parallel Universes,Local Press,Centre,Revolutionary Right,sensationnaliste,complot,écologie,autre,politique,santé,identitaire".split(",")

filename = sys.argv[1]

with open(filename) as f:
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

with open(filename.replace(".csv", "_fakenews_sharers.csv"), "w") as f:
  print("user," + ",".join(allkeys), file=f)
  for u, v in users.items():
    print(u+","+",".join([str(v[k]) for k in allkeys]), file=f)

for c, v in sorted(cats.items()):
  print("%s: %d" % (c, v))

