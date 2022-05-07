import json
import os
from random import randint

import requests

try:
    from local_settings import TENOR_API
except ImportError:
    TENOR_API = os.environ.get("TENOR_API")


def find_gif(search_term, limit=10):
    r = requests.get(
        "https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, TENOR_API, limit))

    result = json.loads(r.content)
    gif_url = result['results'][randint(0, limit-1)]['media'][0]['gif']['url']
    return gif_url
