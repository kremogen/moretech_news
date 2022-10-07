import requests
from bs4 import BeautifulSoup

API_BASE = 'https://www.forbes.ru/'
API_LINK = 'https://api.forbes.ru/api/pub/lists/biznes'


def get_last_news(offset):
    data = {
        'list[limit]': 11,
        'list[offset]': offset
    }
    print(offset)
    response = requests.get(API_LINK, params=data)
    result = []

    try:
        res = response.json()
        articles = res['articles']

        for i in range(len(articles)):
            result.append(API_BASE + articles[i]['data']['url_alias'])

    except Exception as e:
        print(e)

    return result


def get_news_html(url: str):
    resource = requests.get(url)
    text_normalizer(resource.text)
    print(resource.text)


def text_normalizer(text):
    soup = BeautifulSoup(text, 'lxml')
    quotes = soup.find_all(itemprop='articleBody')
    print(quotes)


if __name__ == '__main__':
    offset = 0
    for i in range(10):
        last_news = get_last_news(offset)
        offset += 11
        for j in range(len(last_news) - 1):
            get_news_html(last_news[j])
    # между тегами с классом _3Ywvx находится контент новости
    # data-hid="og:title" property="og:title" content= - заголовок новости
