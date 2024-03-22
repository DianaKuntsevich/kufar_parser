import json

import requests
from bs4 import BeautifulSoup
import re
from pprint import pprint

from environs import Env

from db_client import DBPostgres
from tqdm import tqdm
from dataclasses import astuple
from kufar.models import Notebook

env = Env()
env.read_env()

DBNAME = env('DBNAME')
DBUSER = env('DBUSER')
DBPASSWORD = env('DBPASSWORD')
DBHOST = env('DBHOST')
DBPORT = env('DBPORT')


class NoteDB(DBPostgres):
    def save_data(self, data: list[Notebook]) -> None:
        data = [astuple(i) for i in data]
        self.update_query('''WITH note_id as (
        INSERT INTO product_app_notebook(link, title, price, description, producer, diagonal, 
        resolution, os, processor, ram, video_card, hdd_type, hdd_volume, battery, condition) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (link) DO UPDATE SET price = excluded.price
        RETURNING id
        )
        INSERT INTO product_app_image(image, notebook_id) VALUES (unnest(COALESCE(%s, ARRAY[]::text[])), (SELECT id FROM note_id))
        ON CONFLICT (image) DO NOTHING
        ''', data)

    def crete_table(self):
        self.update_query('''
        CREATE TABLE IF NOT EXISTS notebook (
        id SERIAL PRIMARY KEY,
        link varchar(160) UNIQUE,
        title varchar(500),
        price NUMERIC(10, 2),
        description TEXT,
        producer varchar(100),
        diagonal varchar(100),
        resolution varchar(100),
        os varchar(100),
        processor varchar(100),
        ram varchar(100),
        video_card varchar(100),
        hdd_type varchar(100),
        hdd_volume varchar(100),
        battery varchar(100),
        condition varchar(100) 
        );
        CREATE TABLE IF NOT EXISTS image(
        id serial PRIMARY KEY,
        image varchar(160) UNIQUE,
        notebook_id integer REFERENCES notebook(id)
        )
        ''')


class ParserNotebook:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive'
    }
    DB = NoteDB(
        DBNAME, DBUSER, DBPASSWORD, DBHOST, DBPORT
    )

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

        js_data = soup.find('script', id="__NEXT_DATA__").text
        data = json.loads(js_data)['props']['initialState']['listing']['pagination']
        try:
            next_page_token = list(filter(lambda el : el['label'] == 'next', data))[0]['token']
        except Exception as e:
            next_page_token = ''

        return [links, next_page_token]

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
            notebook.price = float(data['adView']['data']['discount']['price'].replace('р.', '').replace(' ', ''))
        except Exception as e:
            notebook.price = float(data['adView']['data']['price'].replace('р.', '').replace(' ', ''))
        try:
            notebook.image = data['adView']['data']['images']
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
        # self.DB.crete_table()
        url = 'https://www.kufar.by/l/r~minsk/noutbuki'
        flag = True
        while flag:
            links_and_token = self._get_item_links(self.get_soup(url))
            links = links_and_token[0]
            notebooks = []
            for link in tqdm(links, desc='Parsing data'):
                soup = self.get_soup(link)
                if soup:
                    notebook_data = self._get_notebook_data(soup, link)
                    notebooks.append(notebook_data)
                else:
                    continue
            self.DB.save_data(notebooks)

            token = links_and_token[1]
            if not token:
                flag = False

            url = f'https://www.kufar.by/l/r~minsk/noutbuki?cursor={token}'



parser = ParserNotebook()
parser.run()
