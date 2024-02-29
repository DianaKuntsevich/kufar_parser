
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json


URL = 'https://www.kufar.by/l/r~minsk/noutbuki?elementType=categories'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive'
}


# def get_page():
#     URL = ''
#     response = requests.get(URL, headers=HEADERS)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'lxml')
#         pages = soup.find_all('a',
#                               class_="styles_link__8m3I9")
#         print(pages)
#         next_page = 'https://www.kufar.by/' + str(pages)
#         print(next_page)
#         return next_page
#     else:
#         print(f'Bad request url : {response.url} | Status: {response.status_code}')

#
def get_all_links() -> list:
    result = []
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        data = soup.find('div', {'class': "styles_cards__bBppJ"})
        cards = data.find_all('section')
        for card in cards:
            try:
                price = card.find('p', class_="styles_price__G3lbO").text
                price = price.replace('р.', '').replace(' ', '').replace('\xa0', '').replace('Договорная', '').strip()
                price = int(price)
            except Exception as e:
                continue
            # print(price)
            if float(price) > 0:
                link = card.find('a')['href']
                # print(link)
                result.append(link)
    else:
        print(f'Bad request url : {response.url} | Status: {response.status_code}')
    return result


def get_flat_data(link: str) -> dict | None:
    note = {
        'title': '',
        'price': '',
        'image': '',
        'description': '',
        'producer': '',
        'diagonal': '',
        'resolution': '',
        'op': '',
        'processor': '',
        'ram': '',
        'videocard': '',
        'hdd_type': '',
        'hdd_volume': '',
        'battery': '',
        'condition': ''
    }

    response = requests.get(link, headers=HEADERS).text
    soup = BeautifulSoup(response, 'lxml')
    data = soup.find('script', id="__NEXT_DATA__").text

    data = json.loads(data)
    data = data['props']['initialState']
    try:
        title = data['adView']['data']['title']
    except Exception as e:
        title = ''
    try:
        price = data['adView']['data']['price'].replace('р.', '')
    except Exception as e:
        price = ''
    try:
        image = data['adView']['data']['images']['thumbnails']
    except Exception as e:
        image = ''
    try:
        description = data['adView']['data']['description']
    except Exception as e:
        description = ''
    try:
        producer = data['adView']['data']['adParams']['computersLaptopBrand']['vl']
    except Exception as e:
        producer = ''
    try:
        diagonal = data['adView']['data']['adParams']['computersLaptopDiagonal']['vl']
    except Exception as e:
        diagonal = ''
    try:
        resolution = data['adView']['data']['adParams']['computersLaptopResolution']['vl']
    except Exception as e:
        resolution = ''
    try:
        op = data['adView']['data']['adParams']['computersLaptopOs']['vl']
    except Exception as e:
        op = ''
    try:
        processor = data['adView']['data']['adParams']['computersLaptopProcessor']['vl']
    except Exception as e:
        processor = ''
    try:
        ram = data['adView']['data']['adParams']['computerEquipmentLaptopsRam']['vl']
    except Exception as e:
        ram = ''
    try:
        videocard = data['adView']['data']['adParams']['computersLaptopVideocard']['vl']
    except Exception as e:
        videocard = ''
    try:
        hdd_type = data['adView']['data']['adParams']['computersLaptopHddType']['vl']
    except Exception as e:
        hdd_type = ''
    try:
        hdd_volume = data['adView']['data']['adParams']['computersLaptopHddVolume']['vl']
    except Exception as e:
        hdd_volume = ''
    try:
        battery = data['adView']['data']['adParams']['computersLaptopBatteryLife']['vl']
    except Exception as e:
        battery = ''
    try:
        condition = data['adView']['data']['adParams']['condition']['vl']
    except Exception as e:
        condition = ''

    note['title'] = title
    note['price'] = price
    note['image'] = image
    note['description'] = description
    note['producer'] = producer
    note['diagonal'] = diagonal
    note['resolution'] = resolution
    note['op'] = op
    note['processor'] = processor
    note['ram'] = ram
    note['videocard'] = videocard
    note['hdd_type'] = hdd_type
    note['hdd_volume'] = hdd_volume
    note['battery'] = battery
    note['condition'] = condition

    return note


def run():
    links = get_all_links()

    for link in tqdm(links, desc='Parsing data'):
        data = get_flat_data(link)
        # pprint(data)


run()


