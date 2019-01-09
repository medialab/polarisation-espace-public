import csv
import sys
import json
import os.path
import requests
import datetime
import argparse
import urllib.parse
from bs4 import BeautifulSoup
from collections import Counter, defaultdict

sys.path.append(os.path.join(os.getcwd()))

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_PATH, "data")


def format_button_result(string):
    try:
        digits = string.split('.')
        if len(digits) > 1:
            if digits[1][-1] == 'K':
                result = int(digits[0])*1000 + int(digits[1][:-1])*100
            elif digits[1][-1] == 'M':
                result = int(digits[0])*1000000 + int(digits[1][:-1])*100000
        elif len(digits) == 1:
            if digits[0][-1] == 'K':
                result = int(digits[0][:-1])*1000
            elif digits[0][-1] == 'M':
                result = int(digits[0][:-1])*1000000
            else:
                result = int(digits[0])
    except:
        result = None
    return(result)


def fetch_button_data(page_url):
    print(datetime.datetime.now(), ">> Fetching ", "http://" + page_url)
    try:
        http_button_request = "https://www.facebook.com/plugins/like.php?href=" + \
            urllib.parse.quote("http://" + page_url) + "&layout=box_count"
        https_button_request = "https://www.facebook.com/plugins/like.php?href=" + \
            urllib.parse.quote("https://" + page_url) + "&layout=box_count"
        http_button_html = requests.get(
            http_button_request).content.decode('UTF-8')
        http_button_soup = BeautifulSoup(http_button_html, 'html.parser')
        http_button_result = http_button_soup.find(
            'span', attrs={"id": u"u_0_0"}).get_text()
        https_button_html = requests.get(
            https_button_request).content.decode('UTF-8')
        https_button_soup = BeautifulSoup(https_button_html, 'html.parser')
        https_button_result = https_button_soup.find(
            'span', attrs={"id": u"u_0_0"}).get_text()
    except:
        http_button_result = None
        https_button_result = None
    return {"http": http_button_result, "https": https_button_result}


def store_button_data(page_url, retryzero, url_id=None):

    if url_id:
        file_name = os.path.join(DATA_PATH, "temp_fb_button_files",
                                 url_id+".json")
    else:
        small_url = page_url
        if small_url.endswith('/'):
            small_url = small_url[:-1]
        if len(small_url) > 200:
            small_url = small_url[:199]
        file_name = os.path.join(DATA_PATH, "temp_fb_button_files",
                                 small_url.replace("/", "_")+".json")

    if not os.path.isfile(file_name):
        data = fetch_button_data(page_url)
        if (data['http'] == data['https']) and (format_button_result(data['http']) == 0) and retryzero:
            data = fetch_button_data(page_url + '/')
        result = {"fb_http_data": format_button_result(data['http']),
                  "fb_https_data": format_button_result(data['https'])}

        with open(file_name, "w") as file:
            json.dump(result, file, ensure_ascii=False, indent=4)


def add_facebook_data(csv_file, retryzero=False):

    with open(os.path.join(DATA_PATH, csv_file + ".csv"), 'r') as urls_list:
        urls = csv.DictReader(urls_list)
        for row in urls:
            store_button_data(row['normalized'], retryzero=retryzero,
                              url_id=row['id'])

    nb_zero = 0
    nb_null = 0
    nb_urls = 0
    with open(os.path.join(DATA_PATH, csv_file + ".csv"), 'r') as source_csv_file:
        source_csv = csv.DictReader(source_csv_file)
        fieldnames = source_csv.fieldnames
        fieldnames.append("fb_http_data")
        fieldnames.append("fb_https_data")
        with open(os.path.join(DATA_PATH, csv_file + "_with_fb_button_data" + ".csv"), 'w') as result_csv:
            writer = csv.DictWriter(result_csv, fieldnames=fieldnames)
            writer.writeheader()
            for row in source_csv:
                result = row
                url_id = row['id']
                try:
                    json_file = os.path.join(DATA_PATH, "temp_fb_button_files",
                                             url_id+".json")
                    with open(json_file, 'r') as f:
                        fb_data = json.load(f)
                        result['fb_http_data'] = fb_data['fb_http_data']
                        result['fb_https_data'] = fb_data['fb_https_data']
                except:
                    small_url = row['url']
                    if small_url.endswith('/'):
                        small_url = small_url[:-1]
                    if len(small_url) > 200:
                        small_url = small_url[:199]
                    json_file = os.path.join(DATA_PATH, "temp_fb_button_files",
                                             small_url.replace("/", "_")+".json")
                    with open(json_file, 'r') as f:
                        fb_data = json.load(f)
                        result['fb_http_data'] = fb_data['fb_http_data']
                        result['fb_https_data'] = fb_data['fb_https_data']
                if (result['fb_http_data'] == result['fb_https_data']) and (result['fb_http_data'] == 0):
                    nb_zero += 1
                if (result['fb_http_data'] == result['fb_https_data']) and (result['fb_http_data'] is None):
                    nb_null += 1
                nb_urls += 1
                writer.writerow(result)

    print("--------------------------------------------------------------")
    print("Facebook data fetching finished - find the results in /data.")
    print(nb_urls, "urls processed.")
    print('Urls with 0 shares:', nb_zero)
    print('Urls at null shares:', nb_zero)
    print("--------------------------------------------------------------")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_csv", help="The csv with the urls you want Facebok data from")
    parser.add_argument(
        "--retryzero", help="Re-fetches urls with 0 shares by adding an ending '/'", action="store_true")
    args = parser.parse_args()
    add_facebook_data(args.source_csv, retryzero=args.retryzero)
