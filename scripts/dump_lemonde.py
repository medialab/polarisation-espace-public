#!/usr/bin/env python3
# =============================================================================
# Script dumping Le Monde's stories
# =============================================================================
#
# We need to retrieve all of Le Monde's stories on mediacloud so we can train
# our thematic classifier afterwards.
#
import os
import csv
import sys
import mediacloud
from pprint import pprint

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

LEMONDE_ID = 39072

client = mediacloud.api.MediaCloud(MEDIACLOUD_API_KEY)

result = client.storyList(solr_filter='media_id:%i' % LEMONDE_ID)
pprint(result)
