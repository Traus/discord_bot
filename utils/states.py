from collections import defaultdict
from datetime import datetime

when_all_called = defaultdict(lambda: datetime.timestamp(datetime.now()))
when_slap_called = defaultdict(lambda: datetime.timestamp(datetime.now()))
immune_until = defaultdict(int)
muted_queue = defaultdict(list)
user_permissions = defaultdict(dict)
voice_owners = dict()

statistic = {
    "<:pepe_beer:828026991361261619>": 0,
    "<:tavern_beer:822536261079662672>": 0,
    'slap': 0,
}
