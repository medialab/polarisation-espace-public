from casanova import reader, enricher
from collections import defaultdict

friends = set()
friends_list = defaultdict(list)

# Only the 2000 selected followers

with open("friends_graines.csv") as h:
    filereader = reader(h)

    twitter_handle_pos = filereader.headers['twitter_handle']

    for row, friend_id in filereader.cells('friend_id', with_rows=True):
        friends.add(friend_id)
        friends_list[friend_id].append(row[twitter_handle_pos])

with open("2000_followers_graines_version_2021_09_21.csv") as f, \
    open("2000_followers_graines_version_2021_10_19.csv", "w") as of:
    file_enricher = enricher(f, of, add=['count_graines_in_followers', 'graines_in_followers'])

    for row, friend_id in file_enricher.cells('follower_id', with_rows=True):
        if friend_id in friends:
            nb = len(friends_list[friend_id])
            liste = "|".join(friends_list[friend_id])
            file_enricher.writerow(row, [nb, liste])
        else:
            nb = 0
            liste = ""
            file_enricher.writerow(row, [nb, liste])

with open("followers_metadata_version_2021_09_21.csv") as f, \
    open("followers_metadata_version_2021_10_19.csv", "w") as of:
    file_enricher = enricher(f, of, add=['count_graines_in_followers', 'graines_in_followers'])

    for row, friend_id in file_enricher.cells('follower_id', with_rows=True):
        if friend_id in friends:
            nb = len(friends_list[friend_id])
            liste = "|".join(friends_list[friend_id])
            file_enricher.writerow(row, [nb, liste])
        else:
            nb = 0
            liste = ""
            file_enricher.writerow(row, [nb, liste])
