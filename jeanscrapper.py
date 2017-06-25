import requests
import csv
from bs4 import BeautifulSoup

BASE_SERVER = 'http://www.falabella.com'
URL = BASE_SERVER + '/falabella-cl/category/cat6040035/Jeans'
ITEMS_PER_PAGE = 100
PARAMS = {'No': 0, 'Nrpp': ITEMS_PER_PAGE}


def text_to_unicode(text):
    return unicode(text).encode('utf-8')


def parse_jeans(raw_jeans):
    parsed_jeans = []
    for raw_jean in raw_jeans:
        detail_page = BASE_SERVER + raw_jean.find('div', class_='marca').a['href']
        brand = raw_jean.find('div', class_='marca').a['title']
        description = raw_jean.find('div', class_='detalle').a['title']
        price = raw_jean.find('div', class_='precio1').span.text
        parsed_jeans.append(
            (
                text_to_unicode(brand),
                text_to_unicode(description),
                text_to_unicode(price)
            )
        )
    return parsed_jeans


r = requests.get(URL, params=PARAMS)
soup = BeautifulSoup(r.text, 'html.parser')
jeans = soup.find_all('div', class_='cajaLP4x')
i = 0
with open('jeans.csv', 'wb') as jeans_csv:
    wr = csv.writer(jeans_csv)
    while len(jeans) > 0:
        parsed_jeans = parse_jeans(jeans)
        for parsed_jean in parsed_jeans:
            wr.writerow(parsed_jean)
        i += 1
        PARAMS['No'] = i * ITEMS_PER_PAGE
        r = requests.get(URL, params=PARAMS)
        soup = BeautifulSoup(r.text, 'html.parser')
        jeans = soup.find_all('div', class_='cajaLP4x')
