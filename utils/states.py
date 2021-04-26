from collections import defaultdict
from datetime import datetime

from constants import beer_emoji

when_all_called = defaultdict(lambda: datetime.timestamp(datetime.now()))
when_slap_called = defaultdict(lambda: datetime.timestamp(datetime.now()))
immune_until = defaultdict(int)
muted_queue = defaultdict(list)
user_permissions = defaultdict(dict)
voice_owners = dict()

statistic = {
    beer_emoji.beer: 0,
    beer_emoji.ale: 0,
    beer_emoji.wine: 0,
    beer_emoji.vodka: 0,
    'slap': 0,
}
