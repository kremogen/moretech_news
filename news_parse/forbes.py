import requests
from bs4 import BeautifulSoup

API_BASE = 'https://www.forbes.ru/'
API_LINK = 'https://api.forbes.ru/api/pub/lists/biznes'


def get_last_news_data(offset):
    data = {
        'list[limit]': 11,
        'list[offset]': offset
    }

    response = requests.get(API_LINK, params=data)
    try:
        res = response.json()
        return res['articles']
    except Exception as e:
        print(e)

    return None


def get_news_html(url: str):
    resource = requests.get(url)
    print(text_normalizer(resource.text))


def text_normalizer(text) -> list:
    soup = BeautifulSoup(text, 'lxml')
    quotes = soup.find_all(itemprop='articleBody')
    return quotes


def get_news_link(url_alias: str):
    return API_BASE + url_alias


# между тегами с классом _3Ywvx находится контент новости
# data-hid="og:title" property="og:title" content= - заголовок новости

if __name__ == '__main__':
    offset = 0
    for i in range(2):
        last_news_data = get_last_news_data(offset)
        offset += 11
        for j in range(len(last_news_data) - 1):
            news_link = get_news_link(last_news_data[j]['data']['url_alias'])
            print(news_link)
            print('date: ' + str(last_news_data[j]['data']['photo']['timestamp']))
            get_news_html(news_link)
            print('\n')
