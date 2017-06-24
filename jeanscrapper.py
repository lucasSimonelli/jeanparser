import requests
import csv
from bs4 import BeautifulSoup

URL='http://www.falabella.com/falabella-cl/category/cat6040035/Jeans'
ITEMS_PER_PAGE=100
PARAMS={'No':0, 'Nrpp':ITEMS_PER_PAGE}


def parseJeans(jeans):
    prices = []
    for jean in jeans:
        brand = jean.find('div', class_='marca').a['title']
        description = jean.find('div', class_='detalle').a['title']
        price = jean.find('div', class_='precio1').span.text
        prices.append((unicode(brand).encode('utf-8'),
        unicode(description).encode('utf-8'),
        unicode(price).encode('utf-8')))
    return prices


r = requests.get(URL, params=PARAMS)
soup = BeautifulSoup(r.text, 'html.parser')
jeans = soup.find_all('div', class_='cajaLP4x')
i = 0
with open('jeans.csv', 'wb') as jeans_csv:
    while len(jeans) > 0:
        parsed_jeans = parseJeans(jeans)
        wr = csv.writer(jeans_csv)
        for parsed_jean in parsed_jeans:
            wr.writerow(parsed_jean)
        i += 1
        PARAMS['No'] = i*ITEMS_PER_PAGE
        r = requests.get(URL, params=PARAMS)
        soup = BeautifulSoup(r.text, 'html.parser')
        jeans = soup.find_all('div', class_='cajaLP4x')
