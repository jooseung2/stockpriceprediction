import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Flatten, Dropout
from tensorflow.keras.layers import MaxPooling1D
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.utils import shuffle
from sklearn.preprocessing import LabelBinarizer
import gensim
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
import keras
import os
import re
import argparse
from nltk.corpus import stopwords

# model hyper parameters
EMBEDDING_DIM = 300
SEQUENCE_LENGTH_PERCENTILE = 90
n_layers = 2
hidden_units = 500
batch_size = 100
pretrained_embedding = False
# if we have pre-trained embeddings, specify if they are static or non-static embeddings
TRAINABLE_EMBEDDINGS = True
patience = 2
dropout_rate = 0.3
n_filters = 100
window_size = 8
dense_activation = "relu"
l2_penalty = 0.0003
epochs = 10
VALIDATION_SPLIT = 0.1


def token_to_index(token, dictionary):
    if token not in dictionary.token2id:
        return None
    return dictionary.token2id[token] + 1

def texts_to_indices(text, dictionary):
    result = list(map(lambda x: token_to_index(x, dictionary), text))
    return list(filter(None, result))

def train(train_texts, train_labels, dictionary, model_file=None, EMBEDDINGS_MODEL_FILE=None):
    """
    Train a word-level CNN text classifier.
    :param train_texts: tokenized and normalized texts, a list of token lists, [['sentence', 'blah', 'blah'], ['sentence', '2'], .....]
    :param train_labels: the label for each train text
    :param dictionary: A gensim dictionary object for the training text tokens
    :param model_file: An optional output location for the ML model file
    :param EMBEDDINGS_MODEL_FILE: An optinal location for pre-trained word embeddings file location
    :return: the produced keras model
    """
    assert len(train_texts)==len(train_labels)
    lengths=list(map(lambda x: len(x), train_texts))
    a = np.array(lengths)
    MAX_SEQUENCE_LENGTH = int(np.percentile(a, SEQUENCE_LENGTH_PERCENTILE))
    train_texts_indices = list(map(lambda x: texts_to_indices(x, dictionary), train_texts))
    x_data = pad_sequences(train_texts_indices, maxlen=int(MAX_SEQUENCE_LENGTH))

    train_labels = keras.utils.np_utils.to_categorical(train_labels, num_classes=3)
    y_data = train_labels
    model = Sequential()

    if pretrained_embedding and (EMBEDDINGS_MODEL_FILE is not None):
        embeddings_index = gensim.models.KeyedVectors.load_word2vec_format(EMBEDDINGS_MODEL_FILE, binary=True)
        embedding_matrix = np.zeros((len(dictionary) + 1, EMBEDDING_DIM))
        for word, i in dictionary.token2id.items():
            embedding_vector = embeddings_index[word] if word in embeddings_index else None
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector
        model.add(Embedding(len(dictionary) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=MAX_SEQUENCE_LENGTH,
                            trainable=TRAINABLE_EMBEDDINGS))
    else:
        model.add(Embedding(len(dictionary) + 1,
                            EMBEDDING_DIM,
                            input_length=MAX_SEQUENCE_LENGTH))
    model.add(Dropout(dropout_rate))
    model.add(Conv1D(filters=n_filters,
                     kernel_size=window_size,
                     activation='relu'))
    model.add(MaxPooling1D(MAX_SEQUENCE_LENGTH - window_size + 1))
    model.add(Flatten())

    for _ in range(n_layers):
        model.add(Dropout(dropout_rate))
        model.add(Dense(hidden_units,
                        activation=dense_activation,
                        kernel_regularizer=l2(l2_penalty),
                        bias_regularizer=l2(l2_penalty),
                        kernel_initializer='glorot_uniform',
                        bias_initializer='zeros'))

    model.add(Dropout(dropout_rate))
    model.add(Dense(len(train_labels[0]),
                    activation='softmax',
                    kernel_regularizer=l2(l2_penalty),
                    bias_regularizer=l2(l2_penalty),
                    kernel_initializer='glorot_uniform',
                    bias_initializer='zeros'))

    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])

    print(model.summary())

    early_stopping = EarlyStopping(patience=patience)
    Y = np.array(y_data)
    fit = model.fit(x_data,
                    Y,
                    batch_size=batch_size,
                    epochs=epochs,
                    validation_split=VALIDATION_SPLIT,
                    verbose=1,
                    callbacks=[early_stopping])

    print(fit.history.keys())
    print(fit.history)
    
    if model_file:
        model.save(model_file)
    return model

def tokenize(text):
    stopwords_set = set(stopwords.words('english'))
    tokens = map(lambda x: re.sub(r'[^a-zA-Z ]+', '', x.lower()), text.split())
    tokens = list(filter(None, tokens))
    # tokens = list(map(lambda x: [word for word in x if word not in stopwords_set and len(word) > 2], tokens))
    return tokens

if __name__ == '__main__':
    import multiprocessing
    def process_article_title(article):
        title = article[0]
        label = article[1]
        tokens = tokenize(title)
        if tokens:
            return tokens, label
        else:
            return None

    df = pd.read_csv('../data/shuffled_86400.csv')
    titles_text = df[['article_title']].values.ravel()
    labels = df[['label']].values.ravel()
    # encoder = LabelBinarizer()
    # encoder.fit(labels)
    # transformed_label = encoder.transform(labels)
    
    title_and_label = zip(titles_text, labels)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    result = pool.map(process_article_title, title_and_label)
    result=list(filter(None, result))

    texts, labels = zip(*result)
    mydict = gensim.corpora.Dictionary(texts)
    mydict.save('article_title.dict')
    train(texts, labels, mydict, model_file='stockprice_cnn.model')#,EMBEDDINGS_MODEL_FILE='GoogleNews-vectors-negative300.bin'))