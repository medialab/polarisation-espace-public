from casanova import reader, enricher

followers = set()
followee_list = {}

# Only the 2000 selected followers

with open("2000_followers_graines.csv") as h:
    filereader = reader(h)

    for row, follower_id in filereader.cells('follower_id', with_rows=True):
        followers.add(follower_id)

with open("followers_graines.csv") as g:
    filereader = reader(g)

    twitter_handle_pos = filereader.headers['twitter_handle']

    for row, follower_id in filereader.cells('follower_id', with_rows=True) :
        if follower_id in followers:
            if follower_id in followee_list:
                followee_list[follower_id].append(row[twitter_handle_pos])
            else:
                followee_list[follower_id] = []
                followee_list[follower_id].append(row[twitter_handle_pos])

with open("2000_followers_graines.csv") as f, \
    open("2000_followers_graines_followee_nb.csv", "w") as of:
    file_enricher = enricher(f, of, add=['followee_count', 'followee_list'])

    for row, follower_id in file_enricher.cells('follower_id', with_rows=True):
        nb = len(followee_list[follower_id])
        liste = followee_list[follower_id][0]
        for graine in followee_list[follower_id][1:]:
            liste += "|"
            liste += graine
        file_enricher.writerow(row, [nb, liste])


# Applied to all the followers

# with open("followers_graines.csv") as g:
#     filereader = reader(g)

#     twitter_handle_pos = filereader.headers['twitter_handle']

#     for row, follower_id in filereader.cells('follower_id', with_rows=True) :
#         if follower_id in followee_list:
#             followee_list[follower_id].append(row[twitter_handle_pos])
#         else:
#             followee_list[follower_id] = []
#             followee_list[follower_id].append(row[twitter_handle_pos])

# with open("fixed_followers_metadata.csv") as f, \
#     open("followers_metadata_followee_nb.csv", "w") as of:
#     file_enricher = enricher(f, of, add=['followee_count', 'followee_list'])

#     for row, follower_id in file_enricher.cells('follower_id', with_rows=True):
#         nb = len(followee_list[follower_id])
#         liste = followee_list[follower_id][0]
#         for graine in followee_list[follower_id][1:]:
#             liste += "|"
#             liste += graine
#         file_enricher.writerow(row, [nb, liste])