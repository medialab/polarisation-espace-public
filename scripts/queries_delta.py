#!/usr/bin/env python3
# =============================================================================
# Script testing the delta between queries results
# =============================================================================
#
import os
import re
import csv
import sys
import mediacloud
from os.path import join
from datetime import date

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

FRANCE_LOCAL_COLLECTION = 38379799
FRANCE_NATIONAL_COLLECTION = 34412146

START_DATE = date(2018, 4, 1)
TODAY = date.today()
DEFAULT_DATE = [START_DATE, TODAY]

INPUT_FILE = './data/politiques-a-tester.csv'
OUTPUT_FILE = './data/queries-delta.csv'

MASTER_QUERY = """"Macron" "Besancenot" "Mélenchon" "François Ruffin" "Hamon" "Olivier Faure" "Hidalgo" "François Hollande" "Ségolène Royal" "Le Drian" "Castaner" "Benjamin Griveaux" "Jean-Michel Blanquer" "de Rugy" "Nicolas Hulot" "Marlène Schiappa" "Muriel Penicaud" "Buzyn" "Bayrou" "Bruno Le Maire" "Juppé" "Xavier Bertrand" "Pécresse" "Darmanin" "Sarkozy" "Wauquiez" "Dupont-Aignan" "Philippot" "Marion Maréchal" "Le Pen" "Edouard Philippe"((sénat* NOT améri*)    ("secrétaire d'état" NOT améri*)  "assemblée nationale"   élysée  syndicat*   "aux européennes"  "scrutin européen"  "élections européennes") ("gilet jaune"  "gilets jaunes"  LREM   LaREM  "Front national"  FN    "Rassemblement National"   "France insoumise"  "Lutte Ouvrière"  "Solidarité et progrès"  "Union populaire républicaine"  EELV  "Europe Ecologie"  "Nouveau Parti Anticapitaliste"  "Europe écologie"  ("Les Verts" AND polit*)   PCF  LFI  "les Patriotes"  (Modem NOT connexion)  ("Les républicains" NOT (améri*))  "Parti Radical de Gauche"  UPR  PRG   "Parti socialiste"  "Parti communiste"   "Mouvement démocrate"  "Les constructifs"  UDI  "Debout la France"  DLF  "Front National")"""

client = mediacloud.api.AdminMediaCloud(MEDIACLOUD_API_KEY)

def count(addendum=None):

    solr_query = '(tags_id_media:%s OR tags_id_media:%s) AND (%s' % (
        FRANCE_LOCAL_COLLECTION,
        FRANCE_NATIONAL_COLLECTION,
        MASTER_QUERY
    )

    if addendum:
        solr_query += ' "%s")' % addendum
    else:
        solr_query += ')'

    return client.storyCount(solr_query, client.publish_date_query(*DEFAULT_DATE))['count']

MASTER_COUNT = count()

with open(INPUT_FILE, 'r') as f:
    reader = csv.DictReader(f)
    writer = csv.DictWriter(sys.stdout, fieldnames=['addendum', 'master_count', 'with_addendum', 'delta', 'ratio'])
    writer.writeheader()

    for line in reader:
        c = count(line['nom'])
        d = c - MASTER_COUNT

        writer.writerow({
            'addendum': line['nom'],
            'master_count': MASTER_COUNT,
            'with_addendum': c,
            'delta': d,
            'ratio': '%2f' % (d / MASTER_COUNT)
        })
