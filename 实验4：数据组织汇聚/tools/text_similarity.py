# 本文件实现了各种可能用到的文本匹配技术
import Levenshtein


# 编辑距离（Levenshtein 距离）
def text_similarity_levenshtein(text1, text2):
    return 1 - Levenshtein.distance(text1, text2) / max(len(text1), len(text2))

# 海明距离
def text_similarity_hamming(text1, text2):
    if len(text1) != len(text2):
        raise ValueError("Strings must be of the same length")
    return sum(el1 != el2 for el1, el2 in zip(text1, text2)) / len(text1)

# Jaccard Distance
# def text_similarity_jaccard(text1, text2):
#     set1, set2 = set(text1.split()), set(text2.split())
#     intersection = len(set1.intersection(set2))
#     union = len(set1.union(set2))
#     return intersection / union

def text_similarity_jaccard(text1, text2):
    set1, set2 = set([i for i in text1]), set([i for i in text2])
    intersaction = len(set1 & set2)
    union = len(set1 | set2)
    return intersaction / union

# Jaro-Winkler Distance
from jellyfish import jaro_winkler_similarity

def text_similarity_jw(text1, text2):
    return jaro_winkler_similarity(text1, text2)

# 余弦相似性
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def text_similarity_cosine(text1, text2):
    tfidf_vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_vectorizer[0:1], tfidf_vectorizer[1:2])
    return cosine_sim[0][0]

# 欧氏距离
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import euclidean

def text_similarity_euclidean(text1, text2):
    tfidf_vectorizer = TfidfVectorizer().fit_transform([text1, text2]).toarray()
    return 1 / (1 + euclidean(tfidf_vectorizer[0], tfidf_vectorizer[1]))

# TF-IDF 实现文本语义相似性
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def text_similarity_tfidf(text1, text2):
    tfidf_vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_vectorizer[0:1], tfidf_vectorizer[1:2])
    return cosine_sim[0][0]

# wordnet 词库判断(只能用于英文)




if __name__ == '__main__':
    print(f'jaccard: {text_similarity_jaccard(text1="就诊ID", text2="门诊ID")}')
    print(f'jw: {text_similarity_jw(text1="就诊ID", text2="门诊ID")}')
    print(f'cosine: {text_similarity_cosine(text1="就诊ID", text2="门诊ID")}')
    print(f'euclidean: {text_similarity_euclidean(text1="就诊ID", text2="门诊ID")}')
    print(f'tfidf: {text_similarity_tfidf(text1="就诊ID", text2="门诊ID")}')


