from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils import shuffle
import pandas as pd
import json
import pickle
import argparse
from scipy import sparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--max_features",
    type=int,
    help="will preprocess for vocabulary that only consider the top <max_features> ordered by term frequency across the corpus",
)

dargs = parser.parse_args()

assert isinstance(dargs.max_features, int) and dargs.max_features > 0

MAX_FEATURES = dargs.max_features

# load data and shuffle
df = pd.read_csv("../data/labeled/86400.csv")
# df = pd.read_csv("../data/shuffled_86400.csv")
df = shuffle(df)
df.to_csv("../data/shuffled_86400.csv", index=False)

# preprocessing
titles_text = df[["article_title"]].values.ravel()
tfidf = TfidfVectorizer(
    ngram_range=(1, 2),
    token_pattern="\w",
    max_features=MAX_FEATURES,
    stop_words="english",
    lowercase=True,
)
features = tfidf.fit_transform(titles_text)
pickle.dump(tfidf, open("tfidfVectorizer_features={}.pkl".format(MAX_FEATURES), "wb"))
sparse.save_npz("features_ngram=1,2_features={}.npz".format(MAX_FEATURES), features)
