import datetime
import json
import requests
from bs4 import BeautifulSoup
from text_cleaner import preprocess_text
import csv

# last_stamp = str((datetime.datetime.now().timestamp())).split('.')[0]
last_stamp = 1659906524


def get_text(url):
    text = []
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    blocks = soup.find('div', class_="article__content").find_all('p')
    for b in blocks:
        text.append(b.text)
    text = "".join(text)
    return preprocess_text(text)


def get_articles():
    global last_stamp
    print(last_stamp)
    url = f'https://www.rbc.ru/v10/ajax/get-news-feed/project/rbcnews.uploaded/lastDate/{last_stamp}/limit/99?_=1665187277141'
    response = requests.get(url).json()
    for i in range(len(response['items'])):
        print('a')
        try:
            new = response['items'][i]['html']
            soup = BeautifulSoup(new, "lxml")
            title = soup.find('span', class_="news-feed__item__title").text
            title = preprocess_text(" ".join(title.split()))
            link = soup.find('a').get('href')
            text = get_text(link)
            last_stamp = response['items'][i]['publish_date_t']
            correct_date = datetime.datetime.utcfromtimestamp(int(last_stamp)).strftime('%Y.%m.%d')
            print(last_stamp)
            try:
                with open('rbc_data.csv', mode='a', encoding='utf-8') as w_file:
                    file_writer = csv.writer(w_file, delimiter=',', lineterminator='\r')
                    file_writer.writerow([title, text, correct_date])
            except Exception as e:
                print('Файл уже существует, начинаю сохранять данные:\n')
        except Exception:
            pass

    return last_stamp


def main():
    for d in range(100):
        get_articles()


if __name__ == "__main__":
    main()
