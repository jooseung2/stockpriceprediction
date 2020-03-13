import tensorflow as tf
from tensorflow.keras.models import load_model
import gensim
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import os

# os.environ["NLTK_DATA"] = "/usr/local/share/nltk_data"
# from nltk.corpus import stopwords


class CNN:
    def __init__(self):
        self.mydict = gensim.corpora.Dictionary.load("models/cnn/article_title.dict")
        # self.stopwords_set = set(stopwords.words("english"))
        self.session = tf.compat.v1.Session()
        self.graph = tf.compat.v1.get_default_graph()
        with self.graph.as_default():
            with self.session.as_default():
                self.model = load_model("models/cnn/stockprice_cnn.model")

    def tokenize(self, text):
        tokens = map(lambda x: re.sub(r"[^a-zA-Z ]+", "", x.lower()), text.split())
        tokens = list(filter(None, tokens))
        return tokens

    def token_to_index(self, token, dictionary):
        if token not in dictionary.token2id:
            return None
        return dictionary.token2id[token] + 1

    def texts_to_indices(self, text, dictionary):
        result = list(map(lambda x: self.token_to_index(x, dictionary), text))
        return list(filter(None, result))

    def predict(self, text):
        tokenized_text = [self.tokenize(text)]
        train_texts_indices = list(
            map(lambda x: self.texts_to_indices(x, self.mydict), tokenized_text)
        )
        x_data = pad_sequences(train_texts_indices, maxlen=15)
        with self.graph.as_default():
            with self.session.as_default():
                result = self.model.predict_classes(x_data)
        return int(result[0])
