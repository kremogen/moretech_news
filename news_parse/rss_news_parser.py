from abc import abstractmethod, ABC
import os
import feedparser
import requests
import pandas as pd
from feedparser import FeedParserDict
import re


class RssParser(ABC):
    def __init__(self, csv_file: str, rss_link: str) -> None:
        self.csv_file: str = csv_file
        self.rss_link: str = rss_link
        self.df: pd.DataFrame = pd.DataFrame()

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

    @staticmethod
    def clear_emojis(string) -> str:
        regrex_pattern = re.compile(pattern="["
                                            u"\U0001F600-\U0001F64F"  # emoticons
                                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                            u"\U00002702-\U000027B0"
                                            u"\U000024C2-\U0001F251"
                                            "]+", flags=re.UNICODE)
        return regrex_pattern.sub(r'', string)

    @abstractmethod
    def parse_data(self) -> None:
        raise NotImplementedError

    def concat_data(self, title: str, body: str, link: str, date: str) -> None:
        ddf = pd.DataFrame([[self.clear_emojis(title).strip(), self.clear_emojis(body).strip(), link, date]])
        self.df = pd.concat([self.df, ddf])

    def final_append(self) -> int:
        self.df.to_csv(self.csv_file, mode='a', index=False, header=False)
        print(f'Added ' + str(len(self.df)) + ' items from ' + self.rss_link)
        return len(self.df)


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


class KommersantParser(RssParser, ABC):
    def __init__(self, csv_file: str) -> None:
        super().__init__(csv_file, 'https://www.kommersant.ru/RSS/section-business.xml')

    def parse_data(self) -> None:
        feed = super().get_xml_as_feedparser()
        if feed is not None:
            entries = feed['entries']
            for i in range(len(entries)):
                self.concat_data(entries[i]['title'], self.clear_html_tags(entries[i]['summary']),
                                 entries[i]['link'], entries[i]['published'])


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


class KlerkParser(RssParser, ABC):
    def __init__(self, csv_file: str) -> None:
        super().__init__(csv_file, 'https://www.klerk.ru/export/news.rss')

    def parse_data(self) -> None:
        feed = super().get_xml_as_feedparser()
        if feed is not None:
            entries = feed['entries']
            for i in range(len(entries)):
                self.concat_data(entries[i]['title'],
                                 self.clear_html_tags(entries[i]['summary']),
                                 entries[i]['link'], entries[i]['published'])


class AifParser(RssParser, ABC):
    def __init__(self, csv_file: str) -> None:
        super().__init__(csv_file, 'https://aif.ru/rss/money.php')

    def parse_data(self) -> None:
        feed = super().get_xml_as_feedparser()
        if feed is not None:
            entries = feed['entries']
            for i in range(len(entries)):
                if 'yandex_full-text' in entries[i]:
                    self.concat_data(entries[i]['title'],
                                     self.clear_html_tags(entries[i]['yandex_full-text']),
                                     entries[i]['link'], entries[i]['published'])


def create_actual_news_csv(filename: str) -> None:
    try:
        os.remove(filename)
    except:
        pass

    ps = [
        VedomostiParser(filename),
        KommersantParser(filename),
        BankiRuParser(filename),
        BuhParser(filename),
        KlerkParser(filename),
        AifParser(filename)
    ]

    count = 0
    for i in range(len(ps)):
        ps[i].parse_data()
        count += ps[i].final_append()

    print('Total added ' + str(count) + ' news')
