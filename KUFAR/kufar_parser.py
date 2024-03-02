import json

import requests
from bs4 import BeautifulSoup
import re
from pprint import pprint

from tqdm import tqdm

from KUFAR.models import Notebook


class ParserNotebook:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive'
    }
    @classmethod
    def get_soup(cls, url: str) -> BeautifulSoup:
        response = requests.get(url, headers=cls.HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            return soup
        else:
            print(f'{url} | {response.status_code}')


    @staticmethod
    def _get_item_links(soup: BeautifulSoup) -> list:
        links = []
        sections = soup.find_all('section')
        for section in sections:
            link = section.find('a', href=True)['href'].split('?')[0]
            price = section.find('p', class_="styles_price__G3lbO")
            if not price:
                price = section.find('span', class_="styles_price__vIwzP").text
            else:
                price = price.text
            price = re.sub(r'[^0-9]', '', price)
            if price.isdigit():
                links.append(link)

        return links

    @staticmethod
    def _get_notebook_data(soup: BeautifulSoup, link: str) -> Notebook:
        notebook = Notebook(link)
        data = soup.find('script', id="__NEXT_DATA__").text

        data = json.loads(data)
        data = data['props']['initialState']

        try:
            notebook.title = data['adView']['data']['title']
        except Exception as e:
            notebook.title = ''
        try:
            notebook.price = data['adView']['data']['price'].replace('р.', '')
        except Exception as e:
            notebook.price = ''
        try:
            notebook.image = data['adView']['data']['images']['thumbnails']
        except Exception as e:
            notebook.image = ''
        try:
            notebook.description = data['adView']['data']['description']
        except Exception as e:
            notebook.description = ''
        try:
            notebook.producer = data['adView']['data']['adParams']['computersLaptopBrand']['vl']
        except Exception as e:
            notebook.producer = ''
        try:
            notebook.diagonal = data['adView']['data']['adParams']['computersLaptopDiagonal']['vl']
        except Exception as e:
            notebook.diagonal = ''
        try:
            notebook.resolution = data['adView']['data']['adParams']['computersLaptopResolution']['vl']
        except Exception as e:
            notebook.resolution = ''
        try:
            notebook.os = data['adView']['data']['adParams']['computersLaptopOs']['vl']
        except Exception as e:
            notebook.os = ''
        try:
            notebook.processor = data['adView']['data']['adParams']['computersLaptopProcessor']['vl']
        except Exception as e:
            notebook.processor = ''
        try:
            notebook.ram = data['adView']['data']['adParams']['computerEquipmentLaptopsRam']['vl']
        except Exception as e:
            notebook.ram = ''
        try:
            notebook.video_card = data['adView']['data']['adParams']['computersLaptopVideocard']['vl']
        except Exception as e:
            notebook.video_card = ''
        try:
            notebook.hdd_type = data['adView']['data']['adParams']['computersLaptopHddType']['vl']
        except Exception as e:
            notebook.hdd_type = ''
        try:
            notebook.hdd_volume = data['adView']['data']['adParams']['computersLaptopHddVolume']['vl']
        except Exception as e:
            notebook.hdd_volume = ''
        try:
            notebook.battery = data['adView']['data']['adParams']['computersLaptopBatteryLife']['vl']
        except Exception as e:
            notebook.battery = ''
        try:
            notebook.condition = data['adView']['data']['adParams']['condition']['vl']
        except Exception as e:
            notebook.condition = ''

        return notebook

    def run(self):
        url = 'https://www.kufar.by/l/r~minsk/noutbuki'
        links = self._get_item_links(self.get_soup(url))
        notebooks = []
        for link in tqdm(links, desc='Parsing data'):
            soup = self.get_soup(link)
            if soup:
                notebook_data = self._get_notebook_data(soup, link)
                pprint(notebook_data)



parser = ParserNotebook()
parser.run()