#!/usr/bin/env python3
# =============================================================================
# Script collecting various statistics about our mediacloud collections
# =============================================================================
#
import os
import sys
import mediacloud

sys.path.append(os.path.join(os.getcwd()))
from config import MEDIACLOUD_API_KEY

client = mediacloud.api.MediaCloud(MEDIACLOUD_API_KEY)
