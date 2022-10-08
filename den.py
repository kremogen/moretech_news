from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import pymorphy2
import nltk
from nltk.corpus import stopwords

def norm(x):
    morph = pymorphy2.MorphAnalyzer()
    p = morph.parse(x)[0]
    return p.normal_form


stopwords.words("russian")
morph = pymorphy2.MorphAnalyzer()
print(norm("зубки"))
df_Vsc = pd.read_csv("dateParseDay.csv")
print(df_Vsc)
df_Vsc["Article"] = df_Vsc["Article"].apply(lambda x: str(x))
df_Vsc["Article"] = df_Vsc["Article"].apply(lambda x: x.split())
df_Vsc["Article"] = df_Vsc["Article"].apply(lambda x: [j if j not in stopwords.words("russian") else "" for j in x])
df_Vsc["Article"] = df_Vsc["Article"].apply(lambda x: [morph.parse(j)[0].normal_form for j in x])
df_Vsc["Article"] = df_Vsc["Article"].apply(lambda x: " ".join(x))
print(df_Vsc["Article"])

# print(df_Vsc.values[0][0] + " "+ df_Vsc.values[0][1])

business_words = ["расширение", "инвестиция", "обслуживание", "масштабирование", "акция", "производство", "обеспечение",
                  "сохранность",
                  "имущество", "должностные", "инструкции", "работника", "ооо", "ип", "оаа", "эффективной",
                  "деятельности", "коммерческая", "тайная", "лицензия"]

buh_words = ["налог", "льгота", "сдача", "отчетность", "зарплата", "имущество", "закупка", "маржинальность",
             "себестоимость", "расчет", "документы", "налоговая", "бухгалтерский", "учет", "кассовый", "кадровый",
             "банк", "законодательство"]

normalized_business = list(map(norm, business_words))
normalized_buh = list(map(norm, buh_words))

print(business_words)
print(normalized_business)

for i in range(20):
    docs = [
        " ".join(normalized_buh),
        df_Vsc.values[i][1]
    ]

    # instantiate CountVectorizer()
    cv = CountVectorizer()
    # this steps generates word counts for the words in your docs
    word_count_vector = cv.fit_transform(docs)
    # print(word_count_vector.shape)
    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(word_count_vector)
    # print idf values
    df_idf = pd.DataFrame(tfidf_transformer.idf_, index=cv.get_feature_names_out(), columns=["idf_weights"])
    # sort ascending
    sortDf = df_idf.sort_values(by=['idf_weights'])
    if (sortDf.values[0] == 1.0):
        print(docs[1])
    else:
        print("Не подходит под Ген Директор")

'''''
# count matrix
count_vector = cv.transform(docs)
# tf-idf scores
tf_idf_vector = tfidf_transformer.transform(count_vector)

feature_names = cv.get_feature_names()
# get tfidf vector for first document
first_document_vector = tf_idf_vector[0]
# print the scores
df = pd.DataFrame(first_document_vector.T.todense(), index=feature_names, columns=["tfidf"])
print(df.sort_values(by=["tfidf"], ascending=False))
'''''
