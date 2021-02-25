import json
from random import randint

import requests

from constants import TENOR_API


def find_gif(search_term, limit=10):
    r = requests.get(
        "https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, TENOR_API, limit))

    result = json.loads(r.content)
    gif_url = result['results'][randint(0, limit-1)]['media'][0]['gif']['url']
    return gif_url
