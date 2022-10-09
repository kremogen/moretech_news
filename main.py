import pandas as pd

from example import telegram_bot
from word_modelling import semantic_processing


def get_news() -> dict:
    result = dict()
    for key in semantic_processing.roles:
        data = pd.read_csv(rf'bin/processed_data_{key}.csv')
        result[key] = data[:5]
    return result


if __name__ == '__main__':
    # create_actual_news_csv('rss_news.csv')
    telegram_bot.start_bot()
