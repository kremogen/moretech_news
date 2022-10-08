from bs4 import BeautifulSoup
import requests
import re

URL = 'https://www.michael-smirnov.ru/Get_RSS.php?pRSSurl=https://www.banki.ru/xml/news.rss'
URL_NEW = 'https://www.michael-smirnov.ru/Get_RSS.php?pRSSurl=https%3A%2F%2Fvc.ru%2Ffeed'

response = requests.get(URL_NEW)

soup = BeautifulSoup(response.text, 'lxml')


def title_normalizer():
    for line in soup.find_all(class_='ahrefnews'):
        print(line.get_text())


def text_normalizer():
    # убирать первые 2 строки
    for line in soup.find_all('tr'):
        #print(type(line.get_text()))
        if line.get_text().startswith((' ', '\t')):
            print('1')
        else:
            print(line.get_text())


def date_checker():
    # убирать самую первую дату
    for line in soup.find_all(class_='pubd nowr'):
        print(line.get_text())


def get_info():
    title_normalizer()
    text_normalizer()
    date_checker()
    # print(response.text)


get_info()
