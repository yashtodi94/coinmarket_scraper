import yaml
import urllib3
from lxml import html
from time import sleep
from bs4 import BeautifulSoup
import json

http = urllib3.PoolManager()


def extract_data(url):
    r = http.request('GET', xpaths['base_url'] + url)
    data = dict()
    if r.status == 200:
        soup = BeautifulSoup(r.data.decode('utf-8'), 'lxml')
        exchange = soup.find('h1').text.strip()

        data[exchange] = dict()
        table = soup.find('table')

        for row in table.find_all('tr'):
            row_data = row.find_all('td')

            if row_data:
                currency = row_data[1].text.strip()
                volume = row.findChild('span', attrs={'class': 'volume'})
                price = row.findChild('span', attrs={'class': 'price'})

                data[exchange][currency] = {
                    'pair': row_data[2].text.strip(),
                    'volume_percent': row_data[5].text.strip(),
                    'last_updated': row_data[6].text.strip(),
                    'volume': {
                        'in_bitcoins': volume['data-btc'],
                        'in_usd': volume['data-btc'],
                        'in_native': volume['data-native'],
                        'formatted_value': volume.text.strip()
                    },
                    'price': {
                        'in_bitcoins': price['data-btc'],
                        'in_usd': price['data-usd'],
                        'in_native': price['data-native'],
                        'formatted_value': price.text.strip()
                    }
                }
    return data


with open('exchange_xpath', 'r') as f:
    xpaths = yaml.load(f)

r = http.request('GET', xpaths['base_url'] + xpaths['all_exchanges'])

if r.status == 200:
    base_html = html.fromstring(r.data.decode('utf-8'))
    exchange_urls = base_html.xpath(xpaths['exchange_urls_xpath'])

    for url in exchange_urls:
        print(json.dumps(extract_data(url)) + '\n\n')
        sleep(5)
