from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

rcc_df = pd.DataFrame()

rcc_df["Article"] = [""]
rcc_df["Body"] = [""]
rcc_df["Date"] = [""]

URL = 'https://www.michael-smirnov.ru/Get_RSS.php?pRSSurl=https://www.banki.ru/xml/news.rss'
URL_NEW = 'https://www.michael-smirnov.ru/Get_RSS.php?pRSSurl=https%3A%2F%2Fvc.ru%2Ffeed'

response = requests.get(URL)

soup = BeautifulSoup(response.text, 'lxml')

def total_addition():
    date_get = soup.find_all(class_='pubd nowr')
    body_get = soup.find_all('tr')
    ahref_news = soup.find_all(class_='ahrefnews')
    for i in range(len(ahref_news)):
        if i > 1:
            line_title = ahref_news[i]
            line_body = body_get[i]
            line_date = date_get[i]
            rcc_df.loc[i] = [line_title.get_text(), line_body.get_text(), line_date.get_text()]

    # # убирать первые 2 строки
    # for line in soup.find_all('tr'):
    #     # print(type(line.get_text()))
    #     if line.get_text().startswith((' ', '\t')):
    #         print('1')
    #     else:
    #         print(line.get_text())
    #
    # # убирать самую первую дату
    # for line in soup.find_all(class_='pubd nowr'):
    #     print(line.get_text())


def title_normalizer():
    ahref_news = soup.find_all(class_='ahrefnews')
    for i in range(len(ahref_news)):
        if i > 1:
            line = ahref_news[i]
            rcc_df.loc[i] = line.get_text()

    # for line in soup.find_all(class_='ahrefnews'):
    #     print(line.get_text())
    #     line.get_text()
    #     rcc_df.loc[]


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
    total_addition()


get_info()
print(rcc_df)
