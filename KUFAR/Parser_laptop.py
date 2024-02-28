
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


URL = 'https://www.kufar.by/l/r~minsk/noutbuki?elementType=categories'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Alt-Used': 'realt.by',
    'Connection': 'keep-alive'
}

PARAM_PATTERN = {
    'Количество комнат': 'rooms',
    'Площадь общая': 'square',
    'Год постройки': 'year',
    'Этаж / этажность': 'floor',
    'Тип дома': 'type_house',
    'Область': 'region',
    'Населенный пункт': 'city',
    'Улица': 'street',
    'Район города': 'district',
    'Координаты': 'coordinates'




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

    }

    response = requests.get(link, headers=HEADERS)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('h1', class_="styles_brief_wrapper__title__Ksuxa").text
        note['title'] = title
        # print(title)
        try:
            price = soup.find('span', class_="styles_main__eFbJH").text
            price = price.replace('р.', '').replace(' ', '').replace('\xa0', '').strip()
        except Exception as e:
            return
        note['price'] = int(price)
        # print(price)
        try:
            image = soup.find('img', class_="styles_slide__image__YIPad styles_slide__image__vertical__QdnkQ")['src']
        except Exception as e:
            image = ''

        note['image'] = image
        print(image)
    #     try:
    #         description = soup.find('div',
    #                                 class_=['description_wrapper__tlUQE']).text
    #         description = description.replace('\n', '')
    #     except Exception as e:
    #
    #         description = ''
    #     flat['description'] = description
    #     # print(description)
    #
    #     params = soup.find_all('li', class_="relative py-1")
    #     for param in params:
    #         key = param.find('span').text
    #         if key not in PARAM_PATTERN:
    #             continue
    #         value = param.find(['p', 'a']).text.replace('г. ', '').replace(' м²', '')
    #         flat[PARAM_PATTERN[key]] = value
    # else:
    #     print(f'Bad request url : {response.url} | Status: {response.status_code}')
    # return note
#
#
#
def run():
    links = get_all_links()

    for link in tqdm(links, desc='Parsing data'):
        data = get_flat_data(link)
        # pprint(data)



run()

