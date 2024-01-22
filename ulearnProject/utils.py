from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree

import requests_cache


def get_cbrf_rate(currency, date):
    print(date)
    # BYR -> BYN after 2016-07-01
    if currency == 'BYR' and date > datetime(2016, 7, 1, tzinfo=timezone(timedelta(hours=0))):
        currency = 'BYN'
    session = requests_cache.CachedSession('cbrf_cache', expire_after=604800)
    response = session.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date.strftime("%d/%m/%Y")}')
    response.raise_for_status()
    tree = ElementTree.fromstring(response.content)
    for node in tree.findall('Valute'):
        if node.find('CharCode').text == currency:
            return float(node.find('VunitRate').text.replace(',', '.'))
    return None
