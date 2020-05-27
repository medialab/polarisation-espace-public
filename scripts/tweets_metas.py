import sys
import re
from datetime import datetime

# Based and enriched from TCAT fields
CORRESP_FIELDS = {
    "id": "_id",
    "time": "timestamp",
    "created_at": lambda x: isodate(x.get("created_at", "")),
    "from_user_name": lambda x: x.get("user_screen_name", x.get("user_name", "")),
    "text": str,
    "filter_level": None,   # WTF is this?
    "possibly_sensitive": "possibly_sensitive",
    "withheld_copyright": str,
    "withheld_scope": str,
    "withheld_countries": lambda x: x.get("withheld_countries", []),      # Added since this is the most interesting info from withheld fields
    "truncated": bool,      # unnecessary since we rebuild text from RTs
    "retweet_count": int,
    "favorite_count": int,
    "reply_count": int,     # Recently appeared in Twitter data, then dropped
    "lang": str,
    "to_user_name": "in_reply_to_screen_name",
    "to_user_id": "in_reply_to_user_id_str",    # Added for better user interaction analysis
    "in_reply_to_status_id": "in_reply_to_status_id_str",
    "source": str,
    "source_name": lambda x: re.split(r"[<>]", (x.get("source", "<>") or "<>"))[2] if x.get("source", "<>") not in ["search", "stream", "thread"] else "",   # Added for simplier postprocess
    "source_url": lambda x: (x.get("source", '"') or '"').split('"')[1] if x.get("source", "<>") not in ["search", "stream", "thread"] else "",              # Added for simplier postprocess
    "location": "user_location",
    "lat": lambda x: get_coords(x)[1],
    "lng": lambda x: get_coords(x)[0],
    "from_user_id": "user_id_str",
    "from_user_realname": "user_name",
    "from_user_verified": "user_verified",
    "from_user_description": "user_description",
    "from_user_url": "user_url",
    "from_user_profile_image_url": "user_profile_image_url_https",
    "from_user_utcoffset": "user_utc_offset",   # Not available anymore after 2018-05-23 #RGPD https://twittercommunity.com/t/upcoming-changes-to-the-developer-platform/104603
    "from_user_timezone": "user_time_zone",     # Not available anymore after 2018-05-23 #RGPD https://twittercommunity.com/t/upcoming-changes-to-the-developer-platform/104603
    "from_user_lang": "user_lang",
    "from_user_tweetcount": "user_statuses",
    "from_user_followercount": "user_followers",
    "from_user_friendcount": "user_friends",
    "from_user_favourites_count": "user_favourites",
    "from_user_listed": "user_listed",
    "from_user_withheld_scope": "user_withheld_scope",
    "from_user_withheld_countries": lambda x: x.get("user_withheld_countries", []),      # Added since this is the most interesting info from withheld fields
    "from_user_created_at": lambda x: isodate(x.get("user_created_at", "")),
    # More added fields:
    "collected_via_search": lambda x: bool(x.get("collected_via_search")),
    "collected_via_stream": lambda x: bool(x.get("collected_via_stream")),
    "collected_via_thread_only": lambda x: bool(x.get("collected_via_thread") and not (x.get("collected_via_search") or x.get("collected_via_stream"))),
    "collected_at_timestamp": "collected_at_timestamp",
    "retweeted_id": "retweet_id",
    "retweeted_user_name": "retweet_user",
    "retweeted_user_id": "retweet_user_id",
    "quoted_id": "quoted_id",
    "quoted_user_name": "quoted_user",
    "quoted_user_id": "quoted_user_id",
    "links": lambda x: x.get("proper_links", x.get("links", [])),
    "medias_urls": lambda x: [_url for _id,_url in x.get("medias", [])],
    "medias_files": lambda x: [_id for _id,_url in x.get("medias", [])],
    "mentioned_user_names": lambda x: x.get("mentions_names", process_extract(x["text"], "@")),
    "mentioned_user_ids": "mentions_ids",
    "hashtags": lambda x: x.get("hashtags", process_extract(x["text"], "#"))
}

def search_field(field, tweet):
    if field not in CORRESP_FIELDS:
        return tweet.get(field, '')
    if not CORRESP_FIELDS[field]:
        return ''
    if CORRESP_FIELDS[field] == bool:
        return tweet.get(field, False)
    if CORRESP_FIELDS[field] == int:
        return tweet.get(field, 0)
    if CORRESP_FIELDS[field] == str:
        return tweet.get(field, '')
    if type(CORRESP_FIELDS[field]) == str:
        return tweet.get(CORRESP_FIELDS[field], 0 if field.endswith('count') else '')
    else:
        try:
            return CORRESP_FIELDS[field](tweet)
        except Exception as e:
            print("WARNING: Can't apply export fonction for field %s to tweet %s\n%s: %s" % (field, tweet, type(e), e), file=sys.stderr)
            return ""

def format_field(val):
    if type(val) == bool:
        return "1" if val else "0"
    if type(val) == list:
        return "|".join([v for v in val if v])
    if val == None:
        return ''
    return val if type(val) == str else str(val)

def get_field(field, tweet):
    try:
        return format_field(search_field(field, tweet)).replace('\n', ' ').replace('\r', ' ')
    except Exception as e:
        print("ERROR with field", field, tweet, file=sys.stderr)
        raise(e)

re_clean_rt = re.compile(r"^RT @\w+: ")
def process_extract(text, car):
    return sorted([r.lstrip(car).lower() for r in re.split(r'[^\w%s]+' % car, re_clean_rt.sub('', text)) if r.startswith(car)])

def get_coords(tw):
    if 'coordinates' not in tw or not tw['coordinates']:
        tw['coordinates'] = {}
    if 'coordinates' not in tw['coordinates'] or not tw['coordinates']['coordinates']:
        tw['coordinates']['coordinates'] = ['', '']
    return tw['coordinates']['coordinates']

isodate = lambda x: datetime.strptime(x, '%a %b %d %H:%M:%S +0000 %Y').isoformat()

