import sys
import csv
import casanova


users = {}
headers = []

ct = 1
while ct < len(sys.argv):
    filepath = sys.argv[ct]
    filename = filepath.split("/")[-1]

    headers += [
        "%s screen_name" % filename,
        "%s nb_tweets" %filename,
        "%s first_tweet_id" %filename,
        "%s first_tweet_created_at" %filename,
        "%s last_tweet_id" %filename,
        "%s last_tweet_created_at" %filename
    ]
    print("Working on", filepath, filename, headers, file=sys.stderr)
    with open(filepath) as f:
        casa = casanova.reader(f)
        try:
            idpos = casa.pos.id
            datpos = casa.pos.created_at
            uidpos = casa.pos.from_user_id
            unmpos = casa.pos.from_user_name
        except:
            idpos = casa.pos.id_str
            datpos = casa.pos.timestamp
            uidpos = casa.pos.user_id_str
            unmpos = casa.pos.user_screen_name
        for row in casa:
            tid = int(row[idpos])
            uid = row[uidpos]
            if uid not in users:
                users[uid] = {}
            if filename not in users[uid]:
                users[uid][filename] = {
                    "nb_tweets": 1,
                    "screen_name": row[unmpos],
                    "first_tweet_id": tid,
                    "first_tweet_created_at": row[datpos],
                    "last_tweet_id": tid,
                    "last_tweet_created_at": row[datpos]
                }
            else:
                users[uid][filename]["nb_tweets"] += 1
                if tid < users[uid][filename]["first_tweet_id"]:
                    users[uid][filename]["first_tweet_id"] = tid
                    users[uid][filename]["first_tweet_created_at"] = row[datpos]
                else:
                    users[uid][filename]["screen_name"] = row[unmpos]
                    users[uid][filename]["last_tweet_id"] = tid
                    users[uid][filename]["last_tweet_created_at"] = row[datpos]
    ct += 1

writer = csv.writer(sys.stdout)
writer.writerow(["id_str"] + headers)
for uid, values in users.items():
    row = [uid]
    for h in headers:
        fn = h.split(" ")[0]
        row.append(str(values.get(fn, {}).get(h.replace(fn + " ", ""), "")))
    writer.writerow(row)
