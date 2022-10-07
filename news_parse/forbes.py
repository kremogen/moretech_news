import requests

API_BASE = 'https://www.forbes.ru/'
API_LINK = 'https://api.forbes.ru/api/pub/lists/biznes'


def get_last_news():
    data = {
        'list[limit]': 11,
        'list[offset]': 88
    }

    response = requests.get(API_LINK, json=data)
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
    print(resource.text)


if __name__ == '__main__':
    news = get_last_news()

    link = news[1]
    print(link)
    get_news_html(link)  # между тегами с классом _3Ywvx находится контент новости
    # data-hid="og:title" property="og:title" content= - заголовок новости
