import csv

twitter_handle = set()

followers_graines_out = []
followers_graines_kept = []

with open("graines_out.csv") as csvFile:
    filereader = csv.DictReader(csvFile)

    for row in filereader:
        twitter_handle.add(row["twitter_handle"])

with open("followers_graines.csv") as csvfile:
    filereader = csv.DictReader(csvfile)
    headers = filereader.fieldnames
    for row in filereader:
        if row["twitter_handle"] in twitter_handle:
            followers_graines_out.append(row)
        else:
            followers_graines_kept.append(row)

with open("followers_graines_kept.csv", "w") as csv_file:
    filewriter = csv.DictWriter(csv_file, fieldnames=headers)

    filewriter.writeheader()
    filewriter.writerows(followers_graines_kept)

with open("followers_graines_out.csv", "w") as csvF:
    filewriter = csv.DictWriter(csvF, fieldnames=headers)

    filewriter.writeheader()
    filewriter.writerows(followers_graines_out)

