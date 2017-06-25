# coding=utf-8
import requests
import csv
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

BASE_SERVER = 'http://www.falabella.com'
URL = BASE_SERVER + '/falabella-cl/category/cat6040035/Jeans'
ITEMS_PER_PAGE = 100
PARAMS = {'No': 0, 'Nrpp': ITEMS_PER_PAGE}


class Jean:
    def __init__(self):
        self.brand = ''
        self.description = ''
        self.price = ''
        self.model = ''
        self.type = ''
        self.trouserType = ''
        self.fit = ''
        self.material = ''
        self.style = ''
        self.sizes = ''

    def set_vals_from_raw_values(self, values):
        self.model = values[1] if len(values) > 1 else ''
        self.type = values[2] if len(values) > 2 else ''
        self.trouserType = values[3] if len(values) > 3 else ''
        self.fit = values[4] if len(values) > 4 else ''
        self.material = values[5] if len(values) > 5 else ''
        self.style = values[6] if len(values) > 6 else ''
        self.sizes = values[7] if len(values) > 7 else ''

    def get_csv_output(self):
        return (
            self.brand, self.description, self.price, self.model, self.type, self.trouserType, self.fit, self.material,
            self.style, self.sizes,
        )

    def __str__(self):
        return self.brand + ',' + self.description + ',' + self.price + ',' + self.model + ',' + self.type + ',' + \
               self.trouserType + ',' + self.fit + ',' + self.material + ',' + self.style + ',' + self.sizes


def text_to_unicode(text):
    return unicode(text).encode('utf-8')


def parse_jean_from_description(descr, jean):
    values = []
    for index, string in enumerate(descr):
        value = string.split(':')[1].strip() if len(string.split(':')) > 1 else ''
        values.append(text_to_unicode(value))
        if string.lower().startswith('medidas'):
            break
    jean.set_vals_from_raw_values(values)


def get_jean_detail(jean, detail_page):
    r = requests.get(detail_page)
    soup = BeautifulSoup(r.text, 'html.parser')
    description = soup.find('div', {'id': 'contenidoDescripcionPP'})
    stripped_strings = list(description.stripped_strings)[1:]
    parse_jean_from_description(stripped_strings, jean)


def parse_jeans(raw_jeans, pool):
    parsed_jeans = []
    results = []
    for raw_jean in raw_jeans:
        jean = Jean()
        jean.brand = text_to_unicode(raw_jean.find('div', class_='marca').a['title'])
        jean.description = text_to_unicode(raw_jean.find('div', class_='detalle').a['title'])
        jean.price = text_to_unicode(raw_jean.find('div', class_='precio1').span.text)
        detail_page = BASE_SERVER + raw_jean.find('div', class_='marca').a['href']
        print detail_page
        if '/' in detail_page:
            results.append(pool.apply_async(get_jean_detail, [jean, detail_page]))
        parsed_jeans.append(jean)
    return parsed_jeans, results


r = requests.get(URL, params=PARAMS)
soup = BeautifulSoup(r.text, 'html.parser')
jeans = soup.find_all('div', class_='cajaLP4x')
i = 0
with open('jeans.csv', 'wb') as jeans_csv:
    wr = csv.writer(jeans_csv)
    while len(jeans) > 0:
        pool = ThreadPool(4)
        parsed_jeans, results = parse_jeans(jeans, pool)
        pool.close()
        pool.join()
        for parsed_jean in parsed_jeans:
            wr.writerow(parsed_jean.get_csv_output())
        i += 1
        PARAMS['No'] = i * ITEMS_PER_PAGE
        r = requests.get(URL, params=PARAMS)
        soup = BeautifulSoup(r.text, 'html.parser')
        jeans = soup.find_all('div', class_='cajaLP4x')
