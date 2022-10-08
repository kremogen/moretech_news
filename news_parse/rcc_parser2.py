from abc import abstractmethod, ABC

import feedparser
import requests
import pandas as pd
from feedparser import FeedParserDict
import re


class RssParser(ABC):
    def __init__(self, csv_file: str, rss_link: str) -> None:
        self.csv_file = csv_file
        self.rss_link = rss_link
        self.df = pd.DataFrame()

    def get_xml(self) -> str or None:
        try:
            res = requests.get(self.rss_link)
            return res.text
        except Exception as e:
            print(e)
        return None

    def get_xml_as_feedparser(self) -> FeedParserDict or None:
        xml = self.get_xml()
        return None if xml is None else feedparser.parse(xml)

    @staticmethod
    def clear_html_tags(string) -> str:
        return re.sub(r'\<[^>]*\>', '', string)

    @abstractmethod
    def parse_data(self) -> None:
        raise NotImplementedError

    def concat_data(self, title: str, body: str, link: str, date: str) -> None:
        ddf = pd.DataFrame([[title, body, link, date]])
        self.df = pd.concat([self.df, ddf])

    def final_append(self):
        self.df.to_csv(self.csv_file, mode='a', index=False, header=False)


class BuhParser(RssParser, ABC):
    def __init__(self, csv_file: str) -> None:
        super().__init__(csv_file, 'https://buh.ru/rss/?chanel=news')

    def parse_data(self) -> None:
        feed = super().get_xml_as_feedparser()
        if feed is not None:
            entries = feed['entries']
            for i in range(len(entries)):
                self.concat_data(entries[i]['title'], entries[i]['summary'],
                                 entries[i]['link'], entries[i]['published'])
        else:
            print('Feed is None!')


class BankiRuParser(RssParser, ABC):
    def __init__(self, csv_file: str) -> None:
        super().__init__(csv_file, 'https://www.banki.ru/xml/news.rss')

    def parse_data(self) -> None:
        feed = super().get_xml_as_feedparser()
        if feed is not None:
            entries = feed['entries']
            for i in range(len(entries)):
                self.concat_data(entries[i]['title'], self.clear_html_tags(entries[i]['summary']),
                                 entries[i]['link'], entries[i]['published'])
        else:
            print('Feed is None!')


# todo: MOSTLY DON'T HAVE SUMMARY BLOCK
class VedomostiParser(RssParser, ABC):
    def __init__(self, csv_file: str) -> None:
        super().__init__(csv_file, 'https://www.vedomosti.ru/rss/rubric/business')

    def parse_data(self) -> None:
        feed = super().get_xml_as_feedparser()
        if feed is not None:
            entries = feed['entries']
            for i in range(len(entries)):
                if 'summary' in entries[i]:
                    self.concat_data(entries[i]['title'], self.clear_html_tags(entries[i]['summary']),
                                     entries[i]['link'], entries[i]['published'])
        else:
            print('Feed is None!')


if __name__ == '__main__':
    filename = 'test.csv'

    p = BuhParser(filename)
    p.parse_data()
    p.final_append()

    p = BankiRuParser(filename)
    p.parse_data()
    p.final_append()

    p = VedomostiParser(filename)
    p.parse_data()
    p.final_append()
