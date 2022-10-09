from gensim.models import Word2Vec
import time
import re
from collections import Counter
import itertools
from statistics import median


import pymorphy2
import gensim.models
import gensim.downloader
import numpy as np
import pandas as pd
import spacy
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

roles = {
    "Boss": [
        "расширение",
        "инвестиция",
        "обслуживание",
        "масштабирование",
        "акция",
        "производство",
        "обеспечение",
        "сохранность",
        "имущество",
        "должностные",
        "инструкции",
        "работника",
        "ооо",
        "ип",
        "оаа",
        "эффективной",
        "деятельности",
        "коммерческая",
        "тайная",
        "лицензия"
    ],
    "Accountant": [
        "налог",
        "льгота",
        "сдача",
        "отчетность",
        "зарплата",
        "имущество",
        "закупка",
        "маржинальность",
        "себестоимость",
        "расчет",
        "документы",
        "налоговая",
        "бухгалтерский",
        "учет",
        "кассовый",
        "кадровый",
        "банк",
        "законодательство"
    ]
}

SPEECH_PARTS = ['NOUN', 'ADJ', 'VERB', 'ADV', 'PROPN']
NLP = spacy.load("ru_core_news_lg")

morph = pymorphy2.MorphAnalyzer()
stopwords.words("russian")
lex_rank_summarizer = LexRankSummarizer()


class SemanticProcessing:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
        self.model = gensim.downloader.load("word2vec-ruscorpora-300")
        self.t_words = []
        self.setup_dataframe()

    def setup_dataframe(self):
        self.dataframe = self.dataframe.dropna()
        self.dataframe = self.dataframe.drop_duplicates()
        # self.dataframe = self.dataframe.set_index("Date")
        self.dataframe = self.dataframe.sort_values("Date", ascending=False)

    def optimize_body(self):
        print("optimizing body")

        self.dataframe["Digest"] = self.dataframe["Body"].apply(
            lambda x: self.find_digest(x))
        self.dataframe["Body"] = self.dataframe["Body"].apply(
            lambda x: self.preprocess_text(x))
        self.dataframe["Body"] = self.find_grams(self.dataframe["Body"])
        self.dataframe["Body"] = self.dataframe["Body"].apply(
            lambda x: self.tf_list(x))

        print("optimizing body finished")

    def optimize_article(self):
        '''
        Оптимизация заголовка новости
        '''
        print("optimizing articles")

        self.dataframe["Article_original"] = self.dataframe["Article"]
        self.dataframe["Article"] = self.dataframe["Article"].apply(
            lambda x: self.preprocess_text(x))

        print("optimizing articles finished")

    def drop_similar(self):
        '''
        Вычленение похожих новостей по процентному соотношению подобия
        '''
        normalized_digests = self.dataframe["Digest"].apply(
            lambda x: NLP(" ".join(x)))
        combinations = list(itertools.combinations(normalized_digests, r=2))
        for x, y in combinations:
            if x.similarity(y) > 0.83:
                article_to_drop = x if len(x) > len(y) else y
                try:
                    self.dataframe = self.dataframe.drop(
                        normalized_digests.index[
                            normalized_digests == article_to_drop])
                except KeyError:
                    continue

    @staticmethod
    def preprocess_text(word):
        '''
        Лемматизация текста
        :param word:
        :return:
        '''
        word = word.lower().replace("ё", "е")
        word = re.sub('((www\\.[^\\s]+)|(https?://[^\\s]+))', '', word)
        word = re.sub('@[^\\s]+', '', word)
        word = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', word)
        word = re.sub(' +', ' ', word)
        return [token.lemma_ for token in NLP(
            word) if token.pos_ in SPEECH_PARTS]

    @staticmethod
    def tf_list(article, n=10) -> list:
        '''
        Частота появления термина.
        :param article:
        :param n:
        :return:
        '''
        tf_idf_v = TfidfVectorizer(use_idf=True)
        tf_idf = tf_idf_v.fit_transform(article)
        result = pd.DataFrame(
            tf_idf[0].T.todense(),
            index=tf_idf_v.get_feature_names_out(),
            columns=["TF-IDF"])
        result = result.sort_values('TF-IDF', ascending=False)
        return result.head(n).index.to_list()

    @staticmethod
    def get_median_similarity_for_body(model, terms, role_keywords):
        '''
        Медиана частоты появления слов в теле новости
        :param model:
        :param terms:
        :param role_keywords:
        :return:
        '''
        result = []

        for article_word, keyword in itertools.product(terms, role_keywords):
            try:
                result.append(
                    model.similarity(
                        article_word +
                        "_" +
                        NLP(article_word)[0].pos_,
                        keyword +
                        "_" +
                        NLP(keyword)[0].pos_))
            except KeyError as e:
                result.append(0.0)
                # print(e)

        return median(result)

    def get_most_similar_for_role(self, role):
        self.optimize_body()
        self.drop_similar()

        self.dataframe[role] = self.dataframe["Body"].map(
            lambda x: self.get_median_similarity_for_body(
                model=self.model,
                terms=x,
                role_keywords=roles[role]))
        our_df = self.dataframe.sort_values(role, ascending=False)
        our_df.to_csv("processed_data.csv")

    @staticmethod
    def find_digest(body):
        '''
        Поиск дайджестов для формирования новостной рассылки
        :param body:
        :return:
        '''
        pl_parser = PlaintextParser.from_string(body, Tokenizer('russian'))
        summary = lex_rank_summarizer(pl_parser.document, sentences_count=3)
        result = []
        for sentence in summary:
            result.append(str(sentence))
        return result

    @staticmethod
    def find_grams(articles):
        '''
        Заменяет словосочетания соответствующими n-граммами там, где это может быть нужно.
        :param articles:
        :return:
        '''
        bigram = gensim.models.Phrases(articles)
        trigram = gensim.models.Phrases(bigram[articles])
        bigram_model = gensim.models.phrases.Phraser(bigram)
        trigram_model = gensim.models.phrases.Phraser(trigram)

        result = pd.Series(0, index=np.arange(len(articles)))

        for i, entry in articles.items():
            result[i] = bigram_model[entry]
            result[i] = trigram_model[bigram_model[entry]]

        return result

    def find_trends(self):
        '''
        Определяет тренды по частоте появления слов.
        :return:
        '''
        self.optimize_article()

        div2 = int(len(self.dataframe) / 2)
        old_articles = self.dataframe["Article"].head(div2)
        new_articles = self.dataframe["Article"].tail(div2 - div2 % 2)

        #c_old_articles = old_articles.apply(lambda x: pd.value_counts(x)).sum(axis=0).sort_values(ascending=False).apply(Counter)
        #c_new_articles = new_articles.apply(lambda x: pd.value_counts(x)).sum(axis=0).sort_values(ascending=False).apply(Counter)
        #print(c_old_articles, c_new_articles)
        c_old_articles = Counter(
            list(itertools.chain.from_iterable(old_articles)))
        c_new_articles = Counter(
            list(itertools.chain.from_iterable(new_articles)))

        # diff between 2 dicts
        c_new_articles.subtract(c_old_articles)
        diff = dict(c_new_articles.most_common())
        # print(diff)

        self.t_words = diff
        # print(self.t_words)
        y_pred = KMeans(n_clusters=3).fit_predict(
            np.asarray(list(diff.values())).reshape(-1, 1))

        t_kw = dict()
        # print(y_pred)
        for i in range(1, len(y_pred)):
            if y_pred[i] != y_pred[i - 1]:
                t_kw = dict(list(diff.items())[0:i])
                break
        print(t_kw)


if __name__ == "__main__":
    time_start = time.time()
    # df = pd.read_csv("dataset.tsv", sep="\t")
    data = pd.read_csv("rss_news.csv", names=["Article", "Body", "Link", "Date"])[:10]
    # data = pd.read_csv("testW.csv")
    print(data)
    # data = preprocess_df(data[:5])
    # eval_data_4_role("Boss", data)

    semantic_processing = SemanticProcessing(data)
    semantic_processing.find_trends()
    print(semantic_processing.dataframe)

    # # semantic_processing.get_most_similar_for_role("Boss")
    # semantic_processing.find_trends()
    # print(NLP("россия").similarity(NLP("нефть")))
    print(time.time() - time_start)
