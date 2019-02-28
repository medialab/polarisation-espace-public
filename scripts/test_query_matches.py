#!/usr/bin/env python3
# =============================================================================
# Script determining which query parts matched an url's text
# =============================================================================
#
import re
import csv
from os.path import join

INPUT_FILE = './data/query-urls.csv'
OUTPUT_FILE = './data/matches.csv'
HTML = './data/query-urls-html'

Q1 = """("gilet jaune" OR "gilets jaunes" OR LREM  OR LaREM OR "Front national" OR FN OR "extrême droite" OR "extrême gauche" OR "extreme droite" OR "extreme gauche"  OR "Rassemblement National"  OR "France insoumise" OR "Lutte Ouvrière" OR "Solidarité et progrès" OR "Union populaire républicaine" OR EELV OR "Europe Ecologie" OR "Nouveau Parti Anticapitaliste" OR "Europe écologie" OR ("Les Verts" AND polit*)  OR PCF OR LFI OR "les Patriotes" OR (Modem NOT connexion) OR ("Les républicains" NOT trump) OR "Parti Radical de Gauche" OR UPR OR PRG  OR "Parti socialiste" OR "Parti communiste"  OR "Mouvement démocrate" OR "Les constructifs" OR UDI OR "Debout la France" OR DLF OR "Front National")"""
Q2 = """(député* OR depute* OR sénat* OR senat*  OR gouvernement*  OR "secrétaire d'état" OR "secretaire d'etat" OR "assemblée nationale" OR parlement OR "l'exécutif" OR élysée OR elysee OR syndicat*  OR "aux européennes" OR "aux europeennes" OR "élections européennes" OR "elections europeennes" OR "élections législatives" OR "elections legislatives")"""
Q3 = """("Jean Lassalle" OR Asselineau OR Cheminade OR "Nathalie Arthaud" OR  "Philippe Poutou" OR "Besancenot" OR "Mélenchon" OR "Melenchon" OR "François Ruffin" OR "Juan Branco" OR "Marion Aubry" OR "Manuel Bompard" OR "André Chassaigne" OR "Marie-George Buffet" OR "Pierre Laurent" OR "Eva Joly" OR "Hulot" OR "Julien Bayou" OR "Cecile Duflot" OR "Olivier Faure" OR "François Hollande" OR "Francois Hollande" OR "Martine Aubry" OR "Hamon" OR "Bernard Cazeneuve" OR "Gerard Filoche" OR "Anne Hidalgo" OR "Raphael Glucksmann" OR "Jean-Marc Ayrault" OR "Vallaud-Belkacem" OR Taubira OR "Sylvia Pinel" OR "Jean-Michel Baylet" OR "Macron" OR "Stanislas Guérini" OR "Richard Ferrand" OR "Gilles Le Gendre" OR "Castaner" OR "De Rugy" OR "Brune Poirson" OR "Muriel Pénicaud" OR "Emmanuelle Wargon" OR "Agnes Buzyn" OR "Marlène Schiappa" OR "Jean-Michel Blanquer" OR "Benjamin Griveaux" OR "Nicole Belloubet" OR "Jean-Yves le Drian" OR "Florence Parly" OR "Mounir Mahjoubi" OR "Frédérique Vidal" OR "Laurent Nunez" OR "Olivier Dussopt" OR "Didier Guillaume" OR "Agnès Pannier-Runacher" OR "Gabriel Attal" OR "Gérard Collomb" OR "Aurore Bergé" OR "Cedric Villani" OR "Gaspard Gantzer" OR "Marc Fesneau" OR "Bayrou" OR "Jacqueline Gourault" OR "Edouard Philippe" OR "Bruno Le Maire" OR "Gérald Darmanin" OR "Franck Riester" OR "Alain Juppé" OR "Jean-Christophe Lagarde" OR "Wauquiez" OR "Sarkozy" OR "Raffarin" OR "Xavier Bertrand" OR "Rachida Dati" OR "Christian Jacob" OR "Francois Fillon" OR "Estrosi" OR "Hortefeux" OR "Claude Guéant" OR "Henri Guaino" OR "Jean-Louis Debré" OR "François Baroin" OR "Dupont-Aignan" OR  "Florian Philippot" OR "Le Pen" OR "Marion Maréchal" OR "Louis Alliot" OR "Eric Drouet" OR "Ingrid Levavasseur" OR "Maxime Nicolle")"""

def parse_query(q):
    q = q[1:-1]

    patterns = []

    for m in q.split(' OR '):
        m = m.replace('"', '').strip().lower()

        if '(' in m:
            m = m[1:-1]
            m = re.split(r'(?:AND|NOT)', m)[0]

        original = m

        m = m.replace('*', '[^\\b]+')

        patterns.append((original, re.compile(m)))

    return patterns

def get_matches(parsed_query, text):
    m = []

    for original, pattern in parsed_query:
        if re.search(pattern, text):
            m.append(original)

    return m

PARSED_Q1 = parse_query(Q1)
PARSED_Q2 = parse_query(Q2)
PARSED_Q3 = parse_query(Q3)

with open(INPUT_FILE, 'r') as f, open(OUTPUT_FILE, 'w') as o:
    reader = csv.DictReader(f)
    writer = csv.DictWriter(o, fieldnames=reader.fieldnames + ['Q1', 'Q2', 'Q3'])
    writer.writeheader()

    for line in reader:

        if not line['filename'].strip() or int(line['status']) >= 400:
            writer.writerow(line)
            continue

        with open(join(HTML, line['filename']), 'r') as cf:
            try:
                html = cf.read()
            except:
                writer.writerow(line)
                continue

        line['Q1'] = ' | '.join(get_matches(PARSED_Q1, html))
        line['Q2'] = ' | '.join(get_matches(PARSED_Q2, html))
        line['Q3'] = ' | '.join(get_matches(PARSED_Q3, html))

        writer.writerow(line)
