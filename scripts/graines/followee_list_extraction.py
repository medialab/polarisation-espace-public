from casanova import reader, enricher
from collections import defaultdict

followers = set()
followee_list = defaultdict(list)

# Only the 2000 selected followers

with open("2000_followers_graines.csv") as h:
    filereader = reader(h)

    for row, follower_id in filereader.cells('follower_id', with_rows=True):
        followers.add(follower_id)

with open("followers_graines_kept.csv") as g:
    filereader = reader(g)

    twitter_handle_pos = filereader.headers['twitter_handle']

    for row, follower_id in filereader.cells('follower_id', with_rows=True) :
        if follower_id in followers:
            followee_list[follower_id].append(row[twitter_handle_pos])

with open("2000_followers_graines.csv") as f, \
    open("2000_followers_graines_followee_nb.csv", "w") as of:
    file_enricher = enricher(f, of, add=['followee_count', 'followee_list'])

    for row, follower_id in file_enricher.cells('follower_id', with_rows=True):
        nb = len(followee_list[follower_id])
        liste = "|".join(followee_list[follower_id])
        file_enricher.writerow(row, [nb, liste])


# Applied to all the followers

# with open("followers_graines_kept.csv") as g:
#     filereader = reader(g)

#     twitter_handle_pos = filereader.headers['twitter_handle']

#     for row, follower_id in filereader.cells('follower_id', with_rows=True) :
#         followee_list[follower_id].append(row[twitter_handle_pos])
        
# with open("fixed_followers_metadata.csv") as f, \
#     open("followers_metadata_followee_nb.csv", "w") as of:
#     file_enricher = enricher(f, of, add=['followee_count', 'followee_list'])

#     for row, follower_id in file_enricher.cells('follower_id', with_rows=True):
#         if follower_id in followee_list:
#             nb = len(followee_list[follower_id])
#             liste = "|".join(followee_list[follower_id])
#             file_enricher.writerow(row, [nb, liste])