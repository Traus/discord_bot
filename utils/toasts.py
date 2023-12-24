import re
from datetime import date

import requests

URL = 'https://rdshop.ru/articles/povod/%s/%s'


def find_toast(month: int = None, day: int = None) -> str:
    month = month or date.today().month
    day = day or date.today().day
    response = requests.get(URL % (month, day))
    pattern = r'(?<=Повод выпить:).*?(?=")'
    result = re.findall(pattern, response.text)[0]
    return result.strip()
