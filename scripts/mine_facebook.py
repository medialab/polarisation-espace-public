import csv
import sys
import json
import time
import os.path
import argparse
import datetime
import requests
import urllib.parse
import pandas as pd
from random import choices
from pprint import pprint
from bs4 import BeautifulSoup
from math import floor, log, ceil
from collections import Counter, defaultdict

sys.path.append(os.path.join(os.getcwd()))
from lib.lru_trie import LRUTrie
from config import FB_APP_ID, FB_APP_SECRET

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_PATH, "data")

ACCESS_TOKEN = FB_APP_ID + "|" + FB_APP_SECRET

MEDIA_FILE = os.path.join(DATA_PATH, 'sources.csv')
MEDIAS_TRIE = LRUTrie.from_csv(MEDIA_FILE)

PROXIES = {
    'http': 'http://proxy.medialab.sciences-po.fr:3128',
    'https': 'http://proxy.medialab.sciences-po.fr:3128',
}

FULL_API_WAIT_TIME = 15  # 10 is not enough
WAIT_TIME = 1


def select_top_urls(source_csv, sample_size=100):
    """Creates a top_urls.csv corresponding to the [sample_size] most shared urls"""
    try:
        with open(os.path.join(DATA_PATH, source_csv), 'r') as csv_file:
            urls = csv.DictReader(csv_file)
            i = 0
            with open(os.path.join(DATA_PATH, "top_urls.csv"), 'w') as resultfile:
                fieldnames = ['media', 'url', 'shares']
                writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in urls:
                    i += 1
                    if i > sample_size:
                        break
                    url = row['url']
                    twitter_shares = row['shares']
                    media = MEDIAS_TRIE.longest(url)
                    writer.writerow({'media': media, 'url': url,
                                    'shares': twitter_shares})
    except FileNotFoundError:
        print("ERROR -", "there is no source file (source_urls.csv) in /data")
        sys.exit()


def select_top_urls_per_media(source_csv, nb_per_media=10):
    """Creates a top_urls_per_media.csv corresponding to the [nb_per_media] most shared urls by media"""
    try:
        with open(os.path.join(DATA_PATH, source_csv), 'r') as csv_file:
            urls = csv.DictReader(csv_file)

            with open(os.path.join(DATA_PATH, "top_urls_per_media.csv"), 'w') as resultfile:
                fieldnames = ['media', 'url', 'shares']
                writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
                writer.writeheader()
                media_dict = defaultdict(Counter)
                i = 0
                for row in urls:
                    i += 1
                    if i % 1000 == 0:
                        print('Sampling by media -', i, 'urls processed.', end="\r")
                    page_url = row['url']
                    twitter_shares = row['shares']
                    media = MEDIAS_TRIE.longest(page_url)
                    media_dict[media][page_url] = int(twitter_shares)

                for key, value in media_dict.items():
                    top_media_urls = value.most_common(nb_per_media)
                    for element in top_media_urls:
                        writer.writerow(
                            {'media': key, 'url': element[0], 'shares': element[1]})
    except FileNotFoundError:
        print("ERROR -", "there is no source file (source_urls.csv) in /data")
        sys.exit()


def select_random_urls(source_csv, sample_size=100):
    """Creates a urls_random_sample.csv with [sample_size] urls randomly picked from source_urls.csv"""
    try:
        csv_file = pd.read_csv(os.path.join(DATA_PATH, source_csv),
                                header=1, names=['url', 'shares'])
    except FileNotFoundError:
        print("ERROR -", "there is no source file (source_urls.csv) in /data")
        sys.exit()
    sample = csv_file.sample(sample_size)
    with open(os.path.join(DATA_PATH, "urls_random_sample.csv"), 'w') as resultfile:
        fieldnames = ['media', 'url', 'shares']
        writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
        writer.writeheader()
        for index, row in sample.iterrows():
            media = MEDIAS_TRIE.longest(row['url'])
            writer.writerow(
                {'media': media, 'url': row['url'], 'shares': row['shares']})


def select_random_urls_per_media(source_csv, nb_per_media=10):
    """Creates a urls_random_sample_per_media.csv with [nb_per_media] urls for each media randomly picked from source_urls.csv"""
    try:
        with open(os.path.join(DATA_PATH, source_csv), 'r') as csv_file:
            urls = csv.DictReader(csv_file)

            with open(os.path.join(DATA_PATH, "urls_random_sample_per_media.csv"), 'w') as resultfile:
                fieldnames = ['media', 'url', 'shares']
                writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
                writer.writeheader()
                media_dict = defaultdict(Counter)
                i = 0
                for row in urls:
                    i += 1
                    if i % 1000 == 0:
                        print('Sampling by media -', i, 'urls processed.', end="\r")
                    page_url = row['url']
                    twitter_shares = row['shares']
                    media = MEDIAS_TRIE.longest(page_url)
                    media_dict[media][page_url] = int(twitter_shares)

                for key, value in media_dict.items():
                    random_media_urls = choices(list(value.items()), k=nb_per_media)
                    for element in random_media_urls:
                        writer.writerow(
                            {'media': key, 'url': element[0], 'shares': element[1]})
    except FileNotFoundError:
        print("ERROR -", "there is no source file (source_urls.csv) in /data")
        sys.exit()

def call_API(page_url, row, complete):
    http_error = False
    https_error = False
    http_https_duplicate = False
    print(">> Fetching ", "http://" + page_url)
    print("   ", datetime.datetime.now())
    encoded_url = urllib.parse.quote(page_url)
    # TOKEN API
    if complete:
        http_api_url = "https://graph.facebook.com/v3.1/?id=" + "http://" + encoded_url + \
            "&fields=engagement&access_token=" + \
            urllib.parse.quote(ACCESS_TOKEN)
        time.sleep(FULL_API_WAIT_TIME)
        https_api_url = "https://graph.facebook.com/v3.1/?id=" + "https://" + encoded_url + \
            "&fields=engagement&access_token=" + \
            urllib.parse.quote(ACCESS_TOKEN)
        time.sleep(FULL_API_WAIT_TIME)
        try:
            with requests.get(http_api_url, proxies=PROXIES) as response:
                http_data = response.json()['engagement']
            http_reaction_count = http_data['reaction_count']
            http_comment_count = http_data['comment_count']
            http_share_count = http_data['share_count']
            http_comment_plugin_count = http_data['comment_plugin_count']
            http_error = False
        except (requests.exceptions.HTTPError, KeyError, json.decoder.JSONDecodeError):
            print("   - Cannot fetch HTTP page: ", http_api_url)
            http_error = True
            http_reaction_count = 0
            http_comment_count = 0
            http_share_count = 0
            http_comment_plugin_count = 0
        try:
            with requests.get(https_api_url, proxies=PROXIES) as response:
                https_data = response.json()[
                    'engagement']
            https_reaction_count = https_data['reaction_count']
            https_comment_count = https_data['comment_count']
            https_share_count = https_data['share_count']
            https_comment_plugin_count = https_data['comment_plugin_count']
            https_error = False
        except (requests.exceptions.HTTPError, KeyError, json.decoder.JSONDecodeError):
            print("   - Cannot fetch HTTPS page: ", https_api_url)
            https_error = True
            https_reaction_count = 0
            https_comment_count = 0
            https_share_count = 0
            https_comment_plugin_count = 0
    # BUTTON COUNT
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
        http_button_result = ''.join(filter(str.isalnum, http_button_result))
        print(http_button_result)
        https_button_html = requests.get(https_button_request).content.decode('UTF-8')
        https_button_soup = BeautifulSoup(https_button_html, 'html.parser')
        https_button_result = https_button_soup.find(
            'span', attrs={"id": u"u_0_0"}).get_text()
        https_button_result = ''.join(filter(str.isalnum, https_button_result))
    except:
        http_button_result = None
        https_button_result = None
    # NO TOKEN API
    http_notoken_url = "https://graph.facebook.com/?id=" + \
        urllib.parse.quote("http://" + page_url)
    https_notoken_url = "https://graph.facebook.com/?id=" + \
        urllib.parse.quote("https://" + page_url)
    try:
        with requests.get(http_notoken_url, proxies=PROXIES, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}) as response:
            http_data = response.json()
            time.sleep(WAIT_TIME)
        http_notoken_comment_count = http_data['share']['comment_count']
        http_notoken_share_count = http_data['share']['share_count']
        http_notoken_error = False
    except Exception as exception:
        print("   NOTOKEN API FAIL - Cannot fetch HTTP page: ",
              http_notoken_url, exception, type(exception))
        http_notoken_error = True
        http_notoken_comment_count = None
        http_notoken_share_count = None
    try:
        with requests.get(https_notoken_url, proxies=PROXIES, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}) as response:
            https_data = response.json()
            time.sleep(WAIT_TIME)
        https_notoken_comment_count = https_data['share']['comment_count']
        https_notoken_share_count = https_data['share']['share_count']
        https_notoken_error = False
    except Exception as exception:
        print("   NOTOKEN API FAIL - Cannot fetch HTTPS page: ",
              https_notoken_url, exception, type(exception))
        https_notoken_error = True
        https_notoken_comment_count = None
        https_notoken_share_count = None
    if (not http_error) or (not https_error):
        if complete:
            total_reaction_count = http_reaction_count + https_reaction_count
            total_comment_count = http_comment_count + https_comment_count
            total_share_count = http_share_count + https_share_count
            total_comment_plugin_count = http_comment_plugin_count + https_comment_plugin_count
            if not (total_reaction_count == 0 and total_comment_count == 0 and total_share_count == 0 and total_comment_plugin_count == 0):
                if https_reaction_count in range(http_reaction_count, http_reaction_count + ceil(log(max(http_reaction_count, 1)))) and https_comment_count in range(http_comment_count, http_comment_count + ceil(log(max(http_comment_count, 1)))) and https_share_count in range(http_share_count, http_share_count + ceil(log(max(http_share_count, 1)))):
                    total_reaction_count = http_reaction_count
                    total_comment_count = http_comment_count
                    total_share_count = http_share_count
                    total_comment_plugin_count = http_comment_plugin_count
                    http_https_duplicate = True
        else:
            http_reaction_count = None
            http_comment_count = None
            http_share_count = None
            http_comment_plugin_count = None
            https_reaction_count = None
            https_comment_count = None
            https_share_count = None
            https_comment_plugin_count = None
            total_reaction_count = None
            total_comment_count = None
            total_share_count = None
            total_comment_plugin_count = None

        result_row = {"url": page_url, "twitter_shares": row["shares"], 
                        "fb_http_button_result": http_button_result, "fb_https_button_result": https_button_result, 
                        "fb_http_notoken_comment_count": http_notoken_comment_count, "fb_http_notoken_share_count": http_notoken_share_count, 
                        "fb_https_notoken_comment_count": https_notoken_comment_count, "fb_https_notoken_share_count": https_notoken_share_count,
                        "fb_http_reaction_count": http_reaction_count, "fb_http_comment_count": http_comment_count,
                        "fb_http_share_count": http_share_count, "fb_http_comment_plugin_count": http_comment_plugin_count,
                        "fb_https_reaction_count": https_reaction_count, "fb_https_comment_count": https_comment_count,
                        "fb_https_share_count": https_share_count, "fb_https_comment_plugin_count": https_comment_plugin_count,
                        "fb_total_reaction_count": total_reaction_count, "fb_total_comment_count": total_comment_count,
                        "fb_total_share_count": total_share_count, "fb_total_comment_plugin_count": total_comment_plugin_count,
                        "http_https_duplicate": http_https_duplicate,
                        "http_error": http_error, "https_error": https_error}
    else:
        result_row = None
    return result_row

def fetch_facebook_data(row, force=False, complete=False):
    """Fetches FB data concerning the url and stores it in a temporary file"""
    page_url = row['url']
    small_url = page_url
    if small_url.endswith('/'):
        small_url = small_url[:-1]
    if len(small_url) > 200:
        small_url = small_url[:199]
    file_name = os.path.join(DATA_PATH, "temp_fb_files",
                             small_url.replace("/", "_")+".json")

    if force or not os.path.isfile(file_name):
        result_row = call_API(page_url, row, complete)

        try:
            if row['media']:
                result_row['media'] = row['media']
        except:
            pass

        if result_row["fb_total_reaction_count"] == 0 and result_row["fb_total_comment_count"] == 0 and result_row["fb_total_share_count"] == 0:
            if not page_url.endswith('/'):
                print("   No result with this url, trying again with a '/' at the end of the url...")
                page_url = page_url + '/'
                result_row_bis = call_API(page_url, row, complete)
                if result_row_bis is not None:
                    result_row = result_row_bis 

        if force and (result_row["fb_total_reaction_count"] > 0 or result_row["fb_total_comment_count"] > 0 or result_row["fb_total_share_count"] > 0):
            print("   Successful update of zero data-file.")

        file_name = os.path.join(
            DATA_PATH, "temp_fb_files", small_url.replace("/", "_")+".json")

        with open(file_name, "w") as file:
            json.dump(result_row, file, ensure_ascii=False, indent=4)


def add_facebook_data(csv_file="most_shared_urls.csv", complete=False):
    """Creates a [csv_file]_with_fb_data.csv (from the csv file passed in params) with supplementary columns containing Facebook API data"""
    try:
        with open(os.path.join(DATA_PATH, csv_file), 'r') as urls_list:
            urls = csv.DictReader(urls_list)
            for row in urls:
                fetch_facebook_data(row, complete=complete)
    except FileNotFoundError:
        print("ERROR -", csv_file, "not found.")
        sys.exit()
    
    with open(os.path.join(DATA_PATH, csv_file), 'r') as urls_list:
        urls = csv.DictReader(urls_list)
        with open(os.path.join(DATA_PATH, csv_file[:-4] + "_with_fb_data" + ".csv"), 'w') as resultfile:
            fieldnames = ['url', 'twitter_shares', 'fb_http_button_result',
                            'fb_https_button_result', 'fb_button_total',
                            'fb_http_notoken_comment_count', 'fb_http_notoken_share_count',
                            'fb_https_notoken_comment_count', 'fb_https_notoken_share_count',
                            'fb_http_reaction_count', 'fb_http_comment_count',
                            'fb_http_share_count', 'fb_http_comment_plugin_count',
                            'fb_https_reaction_count', 'fb_https_comment_count',
                            'fb_https_share_count', 'fb_https_comment_plugin_count',
                            'fb_total_reaction_count', 'fb_total_comment_count',
                            'fb_total_share_count', 'fb_total_comment_plugin_count',
                            'http_error', 'https_error', 'http_https_duplicate']
            if "media" in urls.fieldnames:
                fieldnames.append('media')
            writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
            writer.writeheader()
            nb_zero_files = 0
            nb_urls = 0
            for row in urls:
                nb_urls += 1
                small_url = row['url']
                if small_url.endswith('/'):
                    small_url = small_url[:-1]
                if len(small_url) > 200:
                    small_url = small_url[:199]
                    
                json_file = os.path.join(DATA_PATH, "temp_fb_files",
                                        small_url.replace("/", "_")+".json")
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    try:
                        if data['http_error'] == None:
                            data['http_error'] == False
                    except:
                        data['http_error'] = False
                    try:
                        if data['fb_http_button_result'] == data['fb_https_button_result']:
                            data['fb_button_total'] == data['fb_http_button_result']
                        else:
                            data['fb_button_total'] == data['fb_http_button_result'] + \
                                data['fb_https_button_result']
                    except:
                        data['http_error'] = False
                    try:
                        if data['https_error'] == None:
                            data['https_error'] == False
                    except:
                        data['https_error'] = False

                    if complete:
                        if (data['fb_total_reaction_count'] == 0 and data['fb_total_comment_count'] == 0 and data['fb_total_share_count'] == 0 and data['fb_total_comment_plugin_count'] == 0):
                            nb_zero_files += 1

                    writer.writerow(data)
                    
    print("--------------------------------------------------------------")
    print("Facebook data fetching finished - find the results in /data.")
    print(nb_urls, "urls processed.")
    print('Urls with 0 shares:', nb_zero_files)
    print("--------------------------------------------------------------")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("source_csv", help="The csv containing the urls you want Facebook data on")
    parser.add_argument("sample_type", help="Choose how you want to sample your csv of urls (choose 'whole' if you want to process all your source file)", choices=['top', 'random', 'whole'])
    parser.add_argument("--sample_size", help="Sets the total amount of urls of the sample (if no per-media option), or the number of urls per media (if per-media option)", type=int)
    parser.add_argument("--per-media", help="Sample the urls according to their media", action="store_true")
    parser.add_argument(
        "--complete", help="Fetch complete data - very slow", action="store_true")
    args = parser.parse_args()

    if args.sample_type == 'top':
        if args.per_media:
            select_top_urls_per_media(args.source_csv, args.sample_size)
            add_facebook_data(csv_file="top_urls_per_media.csv", complete=args.complete)
        else:
            select_top_urls(args.source_csv, args.sample_size)
            add_facebook_data(csv_file="top_urls.csv", complete=args.complete)
    elif args.sample_type == 'random':
        if args.per_media:
            select_random_urls_per_media(args.source_csv, args.sample_size)
            add_facebook_data(
                csv_file="urls_random_sample_per_media.csv", complete=args.complete)
        else:
            select_random_urls(args.source_csv, args.sample_size)
            add_facebook_data(csv_file="urls_random_sample.csv",
                              complete=args.complete)

    elif args.sample_type == 'whole':
        if args.per_media:
            print("ERROR - 'whole' sample type and 'per-media' sample option are incompatible.")
            sys.exit()
        else:
            add_facebook_data(args.source_csv, complete=args.complete)


    # select_top_urls(100000)
    # select_top_urls_per_media(20)
    # select_random_urls(10000)
    # select_random_urls_per_media()
    # add_facebook_data("most_shared_urls_per_media")

