# ON JRRR

DAT=$(date +%y%m%d)

workon gazouilloire-polarisation

# Be sure that bin/export_usersXlinks.py has filter lang: "fr" for mongo queries
cd /store/gazouilloire/gazouilloire-polarisation/
bin/export_usersXlinks.py > /store/gazouilloire/public/polarisation/$DAT-polarisation2-users-urls-FR.csv

# Be sure that bin/export_usersXlinks.py has filter lang: "fr" for mongo queries
cd /store/gazouilloire/gazouilloire-polar-extra/
bin/export_usersXlinks.py > /store/gazouilloire/public/polarisation/$DAT-polarisation2-users-urls-FR-extra.csv

cat /store/gazouilloire/public/polarisation/$DAT-polarisation2-users-urls-FR-extra.csv | grep -v "user_screenname,links,is_retweet" >> /store/gazouilloire/public/polarisation/$DAT-polarisation2-users-urls-FR.csv

rm /store/gazouilloire/public/polarisation/$DAT-polarisation2-users-urls-FR-extra.csv

mv /store/gazouilloire/public/polarisation/$DAT-polarisation2-users-urls-FR.csv /store/gazouilloire/public/polarisation/$DAT-polarisation2-FR-users-urls.csv

deactivate

cd ~/polarisation-espace-public
pyenv activate polarisation
python scripts/compute_bipartite_user_media.py

gzip /store/gazouilloire/public/polarisation/$DAT-polarisation2-FR-users-urls.csv /store/gazouilloire/public/polarisation/$DAT-polarisation2-FR-bipartite-user-media.csv
