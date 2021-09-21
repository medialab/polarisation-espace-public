import csv

twitter_handle = set()

followers_graines_out = []
followers_graines_kept = []

with open("VF-Carte Raison - Corpus-final.csv") as csvFile:
    filereader = csv.DictReader(csvFile)

    for row in filereader:
        twitter_handle.add(row["twitter_handle"])

with open("followers_graines.csv") as csvfile:
    filereader = csv.DictReader(csvfile)
    headers = filereader.fieldnames
    for row in filereader:
        if row["twitter_handle"] in twitter_handle:
            followers_graines_kept.append(row)
        else:
            followers_graines_out.append(row)

with open("followers_graines_version_2021_09_21.csv", "w") as csv_file:
    filewriter = csv.DictWriter(csv_file, fieldnames=headers)

    filewriter.writeheader()
    filewriter.writerows(followers_graines_kept)

with open("followers_graines_out.csv", "w") as csvF:
    filewriter = csv.DictWriter(csvF, fieldnames=headers)

    filewriter.writeheader()
    filewriter.writerows(followers_graines_out)

