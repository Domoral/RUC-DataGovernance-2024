import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 下载必要的NLTK资源
nltk.download('punkt')
nltk.download('stopwords')

def text_similarity_wordnet_tfidf(desc1, desc2):
    # Tokenization and stopwords removal
    stop_words = set(stopwords.words('english'))

    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
        return ' '.join(filtered_tokens)

    clean_desc1 = preprocess_text(desc1)
    clean_desc2 = preprocess_text(desc2)

    # Computing TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([clean_desc1, clean_desc2])

    # Calculating cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return cosine_sim

from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def text_similarity_bert(text1, text2):
    # 加载预训练的BERT模型和tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
    model = BertModel.from_pretrained('bert-base-chinese')

    # 对输入文本进行tokenization
    inputs1 = tokenizer(text1, return_tensors='pt')
    inputs2 = tokenizer(text2, return_tensors='pt')

    # 获取BERT的embedding
    with torch.no_grad():
        outputs1 = model(**inputs1)
        outputs2 = model(**inputs2)

    # 获取 [CLS] token 的embedding
    cls_embedding1 = outputs1.last_hidden_state[:, 0, :].numpy()
    cls_embedding2 = outputs2.last_hidden_state[:, 0, :].numpy()

    # 计算余弦相似性
    cosine_sim = cosine_similarity(cls_embedding1, cls_embedding2)
    return cosine_sim[0][0]