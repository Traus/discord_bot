from collections import defaultdict
from datetime import datetime

when_all_called = defaultdict(lambda: datetime.timestamp(datetime.now()))
when_slap_called = defaultdict(lambda: datetime.timestamp(datetime.now()))
immune_until = defaultdict(int)
